### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation`_ `object`_ validation.

   .. |TypeError| replace:: :class:`TypeError`
   .. |KeyError| replace:: :class:`KeyError`

   .. |ModelledDict| replace:: :class:`ModelledDict <rsk_mt.model.ModelledDict>`

   .. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
   .. _object: https://tools.ietf.org/html/draft-handrews-json-schema-01#section-4.2.1
   .. _maxProperties: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.5.1
   .. _minProperties: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.5.2
   .. _required: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.5.3
   .. _properties: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.5.4
   .. _patternProperties: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.5.5
   .. _additionalProperties: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.5.6
   .. _dependencies: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.5.7
   .. _propertyNames: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.5.8

   .. _JSON Pointer: https://tools.ietf.org/html/rfc6901
"""
# pylint: enable=line-too-long

from types import GeneratorType
import re

from rsk_mt.enforce.value import (Choice, SequenceOf)
from rsk_mt.model import (MappingModel, ModelledDict)
from . import TYPE_SCHEMA
from ..types import (TYPE_CORE, TYPE_NON_NEGATIVE_INTEGER)
from . import (Validator, build_validators)

TYPE_DEPENDENCIES = Choice((
    TYPE_SCHEMA,
    SequenceOf(TYPE_CORE['string']),
))

# pylint: disable=unsubscriptable-object

class ObjectModel(Validator, MappingModel):
    """An object model and |Validator| enforcing a JSON Schema object model.

    The JSON Schema object model is specified by `model_spec` and `policy_spec`.
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, model_spec, policy_spec):
        self._mandatory = None
        self._is_mandatory = None
        self._ge_min = None
        self._le_max = None
        self._properties = None
        self._pattern_properties = None
        self._additional_properties = None
        self._property_names = None
        self._dep_instance = None
        self._dep_presence = None
        self._dependencies = None
        Validator.__init__(self, model_spec['schema'])
        MappingModel.__init__(self, model_spec, policy_spec)
    def _define(self):
        self.validators = self._model_spec['validators']
        self._mandatory = frozenset(self._model_spec['required'])
        self._is_mandatory = lambda key: key in self._mandatory
        self._ge_min = self.get_validator(
            'minProperties',
            lambda val, dec: True,
        )
        self._le_max = self.get_validator(
            'maxProperties',
            lambda val, inc: True,
        )
        self._properties = self._model_spec['properties']
        self._pattern_properties = self._model_spec['patternProperties']
        self._additional_properties = self._model_spec['additionalProperties']
        self._property_names = self._model_spec['propertyNames']
        self._dep_instance = self._model_spec['dependencies']['instance']
        self._dep_presence = self._model_spec['dependencies']['presence']
        self._dependencies = self._dep_instance or self._dep_presence
    def invalid(self, initial, other=None, key=None):
        """A boolean function for testing whether an update is invalid or not.

        If a dict copy of `initial`, updated with `other` (if not None), then
        with `key` deleted (if not None), is invalid according to this model,
        then return True. Otherwise return False.
        """
        val = dict(initial)
        if other is not None:
            val.update(other)
        if key is not None:
            del val[key]
        try:
            self(val)
        except (TypeError, ValueError):
            return True
        else:
            return False
    def form_pair(self, key, val):
        """Form a pair from `key`, `val` according to the rules of this model.

        Raise |KeyError| if `key` cannot be accepted.
        Raise |TypeError| or |ValueError| if the model cannot accept `val`.
        Raise |KeyError| for any other error reason.
        """
        ### enforce `val`...
        ### ...using properties schema at `key`
        try:
            schema = self._properties[key]
        except KeyError:
            schema = None
        else:
            val = schema(val)
        ### ...using all pattern properties with a regexp hit on `key`
        for regexp in self._pattern_properties:
            if regexp.search(key):
                schema = self._pattern_properties[regexp]
                val = schema(val)
        ### ...otherwise additional properties
        if schema is None:
            if self._additional_properties:
                val = self._additional_properties(val)
        ### enforce `key`
        if self._property_names is None:
            return (key, val)
        try:
            return (self._property_names(key), val)
        except (KeyError, ValueError):
            # pylint: disable=raise-missing-from
            raise KeyError(key)
    def default_value(self, key):
        ### prefer default value in properties schema at `key`
        try:
            return self._properties[key].default
        except KeyError:
            pass
        ### only accept a single matching pattern properties default
        ### multiple matching pattern properties defaults is an error
        ### (no method to select winner)
        defaults = []
        for regexp in self._pattern_properties:
            if regexp.search(key):
                schema = self._pattern_properties[regexp]
                try:
                    defaults.append(schema.default)
                except KeyError:
                    pass
                else:
                    if len(defaults) > 1:
                        raise KeyError(key)
        try:
            return defaults[0]
        except IndexError:
            pass
        ### last resort is any additionalProperties default
        if self._additional_properties:
            return self._additional_properties.default
        raise KeyError(key)
    def screen_setitem(self, mapping, key, val):
        pair = self.form_pair(key, val)
        if not self._le_max(mapping, 1):
            raise KeyError(key)
        if self._dependencies and self.invalid(mapping, (pair,)):
            raise KeyError(key)
        return pair
    def screen_moditem(self, mapping, key, val):
        pair = self.form_pair(key, val)
        if self._dependencies and self.invalid(mapping, (pair,)):
            raise KeyError(key)
        return pair
    def screen_delitem(self, mapping, key):
        if key in mapping:
            if self._is_mandatory(key):
                raise KeyError(key)
            if not self._ge_min(mapping, 1):
                raise KeyError(key)
            if self._dependencies and self.invalid(mapping, None, key):
                raise KeyError(key)
        return key
    def screen_update(self, mapping, other):
        formed = {}
        for key in other:
            try:
                pair = self.form_pair(key, other[key])
            except (KeyError, ValueError):
                # pylint: disable=raise-missing-from
                raise ValueError(other)
            else:
                formed[pair[0]] = pair[1]
        if not self._le_max(
                mapping,
                len(frozenset(formed) - frozenset(mapping)),
            ):
            raise ValueError(other)
        if self._dependencies and self.invalid(mapping, other):
            raise ValueError(other)
        return formed
    def pairs_free(self, mapping):
        free = set(mapping) - self._mandatory
        if not self._ge_min(mapping, len(free)):
            free = set()
        elif self._dependencies:
            free = set()
        return free
    def check(self, val):
        return isinstance(val, (dict, GeneratorType))
    def __call__(self, val):
        """Return a :class:`dict` value from mapping `val`.

        Raise |TypeError| or |ValueError| if `val` does not conform to this
        instance's model and policy.
        """
        if not self.check(val):
            raise TypeError(val)
        if isinstance(val, GeneratorType):
            val = dict(val)
        val = super().__call__(val)
        formed = {}
        for key in val:
            try:
                pair = self.form_pair(key, val[key])
            except KeyError:
                raise ValueError(val) # pylint: disable=raise-missing-from
            else:
                formed[pair[0]] = pair[1]
        if self._dep_instance:
            for key in formed:
                try:
                    schema = self._dep_instance[key]
                except KeyError:
                    pass
                else:
                    schema(formed)
        if self._dep_presence:
            for key in formed:
                try:
                    if self._dep_presence[key] - formed.keys():
                        raise ValueError(val)
                except KeyError:
                    pass
        return formed
    def debug(self, val, results):
        def debug_val(valid, key, schema, val):
            """Update `valid` result at `key` with `schema` debug of `val`."""
            valid[key] = schema.debug(val, results) and (
                valid[key] if key in valid else True
            )
        if not self.check(val):
            return False
        valid = super().debug(val, results)
        k_valid = {}
        for key in val:
            results.key_path_push(key)
            schema = None
            try:
                schema = self._properties[key]
            except KeyError:
                pass
            else:
                debug_val(k_valid, 'properties', schema, val[key])
            for regexp in self._pattern_properties:
                if regexp.search(key):
                    schema = self._pattern_properties[regexp]
                    debug_val(k_valid, 'patternProperties', schema, val[key])
            if schema is None:
                if self._additional_properties:
                    schema = self._additional_properties
                    debug_val(k_valid, 'additionalProperties', schema, val[key])
            results.key_path_pop()
            try:
                schema = self._dep_instance[key]
            except KeyError:
                pass
            else:
                debug_val(k_valid, 'dependencies', schema, val)
            try:
                d_valid = not self._dep_presence[key] - val.keys()
            except KeyError:
                pass
            else:
                try:
                    k_valid['dependencies'] = k_valid['dependencies'] and d_valid
                except KeyError:
                    k_valid['dependencies'] = d_valid
        for keyword in k_valid:
            results.assertion(self._schema, keyword, k_valid[keyword])
            valid = valid and k_valid[keyword]
        return valid

def build_validator_required(required):
    """Build a required key validator function.

    Return a boolean function for testing whether an object value has pairs at
    all `required` keys. If `required` is empty, return None.
    """
    required = frozenset(required)
    if not required:
        return None
    return lambda val: not (required - frozenset(val.keys()))

class Object(metaclass=ModelledDict):
    """JSON Schema `object`_ type validation."""
    model = {
        'maxProperties': {
            'value_type': TYPE_NON_NEGATIVE_INTEGER,
        },
        'minProperties': {
            'value_type': TYPE_NON_NEGATIVE_INTEGER,
        },
        'required': {
            'value_type': SequenceOf(TYPE_CORE['string']),
        },
        'properties': {
            'value_type': TYPE_CORE['object'],
            'default': {},
        },
        'patternProperties': {
            'value_type': TYPE_CORE['object'],
            'default': {},
        },
        'additionalProperties': {
            'value_type': TYPE_SCHEMA,
            'default': True,
        },
        'dependencies': {
            'value_type': TYPE_CORE['object'],
            'default': {},
        },
        'propertyNames': {
            'value_type': TYPE_SCHEMA,
            'default': {},
        },
        'format': {
            'value_type': TYPE_CORE['string'],
        },
        'contentEncoding': {
            'value_type': TYPE_CORE['string'],
        },
        'contentMediaType': {
            'value_type': TYPE_CORE['string'],
        },
    }
    policy = 'must-ignore'
    primitive = 'object'
    def __init__(self):
        for key in ('properties', 'patternProperties'):
            if key in self: # pylint: disable=unsupported-membership-test
                for val in self[key].values():
                    TYPE_SCHEMA(val)
        for key in ('dependencies',):
            if key in self: # pylint: disable=unsupported-membership-test
                for val in self[key].values():
                    TYPE_DEPENDENCIES(val)
    @staticmethod
    def _subschema(root, schema, *args):
        """Return the subschema at relative ref `*args`

        Return the subschema at relative ref `*args` from `schema` under `root`.
        If there is no such subschema, return None.
        """
        try:
            return root.get_schema(schema.absolute_ref(*args))
        except KeyError:
            return None
    def model_and_policy(self, root, schema):
        """Return a model, policy for creating a |ModelledDict| class.

        The model and policy enforcing the `object`_ validation rules for
        `schema` under `root`.
        """
        model = {
            'schema': schema,
            'validators': build_validators(root, self, (
                # pylint: disable=undefined-variable
                (
                    'minProperties',
                    lambda min_: lambda val, dec=0: min_ <= (len(val) - dec),
                ),
                (
                    'maxProperties',
                    lambda max_: lambda val, inc=0: (len(val) + inc) <= max_
                ),
                (
                    'required',
                    build_validator_required,
                ),
            )),
            'required': self.get('required', ()), # pylint: disable=no-member
            'minProperties': self.get('minProperties'), # pylint: disable=no-member
            'maxProperties': self.get('maxProperties'), # pylint: disable=no-member
            'properties': {
                k: self._subschema(root, schema, 'properties', k)
                for k in self['properties']
            },
            'patternProperties': {
                re.compile(k): self._subschema(
                    root, schema, 'patternProperties', k,
                ) for k in self['patternProperties']
            },
            'additionalProperties': self._subschema(
                root, schema, 'additionalProperties',
            ),
            'propertyNames': self._subschema(root, schema, 'propertyNames'),
            'dependencies': {
                'instance': {
                    k: self._subschema(root, schema, 'dependencies', k)
                    for k, v in self['dependencies'].items() if isinstance(
                        v, (dict, bool),
                    )
                },
                'presence': {
                    k: v
                    for k, v in self['dependencies'].items() if isinstance(
                        v, list,
                    )
                },
            },
        }
        if self['additionalProperties'] is True:
            policy = 'must-accept'
        else:
            policy = 'must-understand'
        return model, policy
    def validator(self, root, schema):
        """Build a |Validator| class implementing `object`_ validation.

        Return a class built by |ModelledDict| that accepts values passing the
        `object`_ validation rules in |Schema| `schema` under |RootSchema|
        `root`. When validation is successful, a class instance created from the
        accepted value is returned in place of the accepted value. That instance
        also implements custom base classes in `root` for `schema`.
        """
        bases = root.get_bases(schema.uri)
        model, policy = self.model_and_policy(root, schema)
        body = {
            'model_cls': ObjectModel,
            'model': model,
            'policy': policy,
            'check': classmethod(
                lambda cls, val: cls.model.check(val)
            ),
            'cast': classmethod(
                lambda cls, val: cls(val)
            ),
            'debug': classmethod(
                lambda cls, val, results: cls.model.debug(val, results)
            ),
        }
        return ModelledDict(schema.uri, bases, body)
