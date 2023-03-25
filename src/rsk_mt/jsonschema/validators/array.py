### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation`_ `array`_ validation.

   .. |ModelledTuple| replace:: :class:`ModelledTuple <rsk_mt.model.ModelledTuple>`

   .. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
   .. _array: https://tools.ietf.org/html/draft-handrews-json-schema-01#section-4.2.1
   .. _items: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.4.1
   .. _additionalItems: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.4.2
   .. _maxItems: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.4.3
   .. _minItems: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.4.4
   .. _uniqueItems: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.4.5
   .. _contains: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.4.6

   .. _JSON Pointer: https://tools.ietf.org/html/rfc6901
"""
# pylint: enable=line-too-long

from types import GeneratorType

from rsk_mt.model import (ModelledDict, ModelledTuple, Model)
from . import (TYPE_SCHEMA, TYPE_SCHEMA_OR_SEQOF)
from ..types import (TYPE_CORE, TYPE_NON_NEGATIVE_INTEGER)
from . import (Validator, build_validators, equal)

class ArrayModel(Validator, Model):
    """A sequence model and |Validator| enforcing a JSON Schema array model.

    The JSON Schema array model is specified by `model_spec` and `policy_spec`.
    """
    def __init__(self, model_spec, policy_spec):
        self._head_keyword = self._head = None
        self._tail_keyword = self._tail = None
        self._cont_keyword = self._cont = None
        Validator.__init__(self, model_spec['schema'])
        Model.__init__(self, model_spec, policy_spec)
    def _define(self):
        (self._head_keyword, self._head) = self._model_spec['head']
        (self._tail_keyword, self._tail) = self._model_spec['tail']
        (self._cont_keyword, self._cont) = self._model_spec['cont']
        self.validators = self._model_spec['validators']
    def check(self, val):
        return isinstance(val, (list, tuple, GeneratorType))
    def __call__(self, val):
        if not self.check(val):
            raise TypeError(val)
        if isinstance(val, GeneratorType):
            val = tuple(val)
        val = super().__call__(val)
        if self._cont and not any(self._cont.validate(item) for item in val):
            raise ValueError(val)
        formed = []
        idx = 0
        while idx < len(val):
            try:
                item = val[idx]
                item = self._head[idx](item)
            except IndexError:
                break
            else:
                formed.append(item)
            idx += 1
        while idx < len(val):
            item = val[idx]
            if self._tail is not None:
                formed.append(self._tail(item))
            elif self._policy_spec == 'must-understand':
                raise ValueError(item)
            elif self._policy_spec == 'must-accept':
                formed.append(item)
            ### else self._policy_spec == 'must-ignore' => discard
            idx += 1
        return formed
    def debug(self, val, results):
        if not self.check(val):
            return False
        valid = super().debug(val, results)
        cont = False
        head = True
        idx = 0
        while idx < len(val):
            results.key_path_push(idx)
            try:
                head = self._head[idx].debug(val[idx], results) and head
            except IndexError:
                break
            else:
                if self._cont:
                    cont = self._cont.debug(val[idx], results) or cont
            finally:
                results.key_path_pop()
            idx += 1
        if idx:
            results.assertion(self._schema, self._head_keyword, head)
        valid = valid and head
        debug_tail = False
        tail = True
        while idx < len(val):
            results.key_path_push(idx)
            if self._tail:
                debug_tail = True
                tail = self._tail.debug(val[idx], results) and tail
            elif self._policy_spec == 'must-understand':
                debug_tail = True
                tail = False
            if self._cont:
                cont = self._cont.debug(val[idx], results) or cont
            results.key_path_pop()
            idx += 1
        if debug_tail:
            results.assertion(self._schema, self._tail_keyword, tail)
        valid = valid and tail
        if self._cont:
            results.assertion(self._schema, self._cont_keyword, cont)
            valid = valid and cont
        return valid

def build_validator_unique(unique):
    """Build a unique items validator function.

    Return a boolean function for testing whether all items in an array are
    unique. If `unique` is False, return None.
    """
    def validator(val):
        """Return True if all items in `val` are unique, otherwise False."""
        idx = 0
        while idx < len(val) - 1:
            item = val[idx]
            idx += 1
            try:
                dup = idx + val[idx:].index(item)
            except ValueError:
                pass
            else:
                if equal(item, val[dup]):
                    return False
        return True
    return validator if unique else None

class Array(metaclass=ModelledDict):
    """JSON Schema `array`_ type validation."""
    model = {
        'items': {
            'value_type': TYPE_SCHEMA_OR_SEQOF,
        },
        'additionalItems': {
            'value_type': TYPE_SCHEMA,
        },
        'maxItems': {
            'value_type': TYPE_NON_NEGATIVE_INTEGER,
        },
        'minItems': {
            'value_type': TYPE_NON_NEGATIVE_INTEGER,
        },
        'uniqueItems': {
            'value_type': TYPE_CORE['boolean'],
        },
        'contains': {
            'value_type': TYPE_SCHEMA,
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
    primitive = 'array'
    def model_and_policy(self, root, schema):
        """Return a model, policy for creating a |ModelledTuple| class.

        The model and policy enforcing the `array`_ validation rules for
        `schema` under `root`.
        """
        # pylint: disable=unsubscriptable-object
        head = ()
        tail_keyword = 'additionalItems'
        tail = None
        cont = None
        try:
            items = self['items']
        except KeyError:
            items = None
        if items is None:
            policy = 'must-accept'
        elif items is True or items is False or isinstance(items, dict):
            ref = schema.absolute_ref('items')
            tail_keyword = 'items'
            tail = root.get_schema(ref)
            policy = 'must-understand'
        else:
            head = []
            for idx in range(len(items)):
                ref = schema.absolute_ref('items', idx)
                head.append(root.get_schema(ref))
            additional = self.get('additionalItems', True) # pylint: disable=no-member
            if additional is False:
                policy = 'must-understand'
            elif additional is True:
                policy = 'must-accept'
            else:
                ref = schema.absolute_ref('additionalItems')
                tail = root.get_schema(ref)
                policy = 'must-understand'
        try:
            ref = schema.absolute_ref('contains')
            cont = root.get_schema(ref)
        except KeyError:
            pass
        model = {
            'schema': schema,
            'head': ('items', head),
            'tail': (tail_keyword, tail),
            'cont': ('contains', cont),
            'validators': build_validators(root, self, (
                # pylint: disable=undefined-variable
                ('minItems', lambda min_: lambda val: min_ <= len(val)),
                ('maxItems', lambda max_: lambda val: len(val) <= max_),
                ('uniqueItems', build_validator_unique),
            )),
        }
        return model, policy
    def validator(self, root, schema):
        """Build a |Validator| class implementing `array`_ validation.

        Return a class built by |ModelledTuple| that accepts values passing the
        `array`_ validation rules in |Schema| `schema` under |RootSchema|
        `root`. When validation is successful, a class instance created from the
        accepted value is returned in place of the accepted value. That instance
        also implements custom base classes in `root` for `schema`.
        """
        bases = root.get_bases(schema.uri)
        model, policy = self.model_and_policy(root, schema)
        body = {
            'model_cls': ArrayModel,
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
        return ModelledTuple(schema.uri, bases, body)
