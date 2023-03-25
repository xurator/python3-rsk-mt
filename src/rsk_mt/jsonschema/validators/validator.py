### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation`_ validator implementation.

   .. |ValueError| replace:: :class:`ValueError`
   .. |RootSchema| replace:: :class:`RootSchema <rsk_mt.jsonschema.schema.RootSchema>`
   .. |Schema| replace:: :class:`Schema <rsk_mt.jsonschema.schema.Schema>`
   .. |Validator| replace:: :class:`Validator <rsk_mt.jsonschema.validators.validator.Validator>`
   .. |AlreadyDefinedError| replace:: :class:`AlreadyDefinedError <rsk_mt.model.AlreadyDefinedError>`

   .. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
   .. _primitive: https://tools.ietf.org/html/draft-handrews-json-schema-01#section-4.2.1
   .. _format: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-7
   .. _contentEncoding: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-8.3
"""
# pylint: enable=line-too-long

from rsk_mt.enforce.value import (ValueType, Constrained, Choice, SequenceOf)
from rsk_mt.enforce.constraint import Length
from ..types import TYPE_CORE

TYPE_SCHEMA = Choice((TYPE_CORE['object'], TYPE_CORE['boolean']))
### a sequence of schemas accepts an empty sequence
TYPE_SCHEMA_SEQOF = SequenceOf(TYPE_SCHEMA)
### an array of schemas rejects an empty sequence
TYPE_SCHEMA_ARRAY = Constrained(TYPE_SCHEMA_SEQOF, (Length.yang('1 .. max'),))
### a schema or sequence of schemas
TYPE_SCHEMA_OR_SEQOF = Choice((TYPE_SCHEMA, TYPE_SCHEMA_SEQOF))

def _build_validator_format(root, validation):
    """Build a format validator (keyword, function) pair.

    If a named format is specified in `validation`, that format is supported in
    `root` and the format validates the primitive type enforced by `validation`,
    then return a keyword, boolean function pair for semantic validation.
    Otherwise return None.
    """
    keyword = 'format'
    try:
        name = validation[keyword]
        primitive = validation.primitive
    except (KeyError, AttributeError):
        func = None
    else:
        func = root.get_format(name)
    return (keyword, func) if func and func.validates(primitive) else None

def _build_validator_encoding(root, validation):
    """Build an encoding validator (keyword, function) pair.

    If a named encoding is specified in `validation`, that encoding is supported
    in `root` and `validation` validates string values, then return a keyword,
    boolean function pair for semantic validation. Otherwise return None.
    """
    keyword = 'contentEncoding'
    try:
        name = validation[keyword]
        primitive = validation.primitive
    except (KeyError, AttributeError):
        func = None
    else:
        func = root.get_encoding(name)
    return (keyword, func) if func and primitive == 'string' else None

def build_validators(root, validation, build_pairs):
    """Build a list of value validator (keyword, function) pairs.

    Return a list of value validator (keyword, function) pairs for `validation`
    in `root` from custom `build_pairs`, an iterable of (keyword, builder) pairs
    and specified `format`_ and `contentEncoding`_ validators.
    """
    validators = []
    for (keyword, builder) in build_pairs:
        try:
            val = validation[keyword]
        except KeyError:
            pass
        else:
            func = builder(val)
            if func:
                validators.append((keyword, func))
    for builder in (_build_validator_format, _build_validator_encoding):
        pair = builder(root, validation)
        if pair:
            validators.append(pair)
    return validators

class Validator(ValueType):
    """A value validator for JSON Schema `schema`.

    Schema validator enforces the sequence of (keyword, function) pairs in
    :attr:`validators`, where each boolean function is a value validator
    returning True if a value passes the validation rule assertions at keyword
    in `schema`.
    """
    def __init__(self, schema):
        ValueType.__init__(self)
        self._schema = schema
        self._validators = ()
    @property
    def validators(self):
        """Yield this instance's value validator pairs."""
        for pair in self._validators:
            yield pair
    @validators.setter
    def validators(self, pairs):
        """Set this instance's value validator pairs."""
        self._validators = pairs
    def get_validator(self, keyword, default=None):
        """Get this instance's value validator function for `keyword`.

        Return `default` if there is no value validator pair for `keyword`.
        """
        for (v_keyword, func) in self.validators:
            if v_keyword == keyword:
                return func
        return default
    def __call__(self, val):
        for (_keyword, func) in self.validators:
            if not func(val):
                raise ValueError(val)
        return val
    def debug(self, val, results):
        """Return True if `val` is valid, else False.

        Also record the outcome of each keyword assertion in `results`.
        """
        valid = True
        for (keyword, func) in self.validators:
            f_valid = func(val)
            results.assertion(self._schema, keyword, f_valid)
            valid = f_valid and valid
        return valid
    @classmethod
    def build(cls, root, schema, validation, build_pairs=()):
        """Build a `cls` instance for `validation`.

        Return a validator `cls` instance for `validation` rules in |Schema|
        `schema` under |RootSchema| `root`. Build value validator pairs from
        `build_pairs`.
        """
        obj = cls(schema)
        obj.validators = build_validators(root, validation, build_pairs)
        return obj

class TypeValidator(Validator):
    """A value validator for JSON Schema `schema` enforcing `value_type`."""
    def __init__(self, schema, value_type):
        Validator.__init__(self, schema)
        self._value_type = value_type
    def check(self, val):
        return self._value_type.check(val)
    def __call__(self, val):
        self._value_type(val)
        return super().__call__(val)
    def cast(self, val):
        val = self._value_type(val)
        return super().cast(val)
    @classmethod
    def build(cls, root, schema, validation, build_pairs=()):
        obj = cls(schema, TYPE_CORE[validation.primitive])
        obj.validators = build_validators(root, validation, build_pairs)
        return obj

def equal(val1, val2):
    """A boolean function testing equality of `primitive`_ values."""
    if val1 is val2:
        return True
    if val1 == val2:
        if isinstance(val1, (float, int)) and isinstance(val2, (float, int)):
            # if numeric, both values must be numeric or both must be boolean
            if not isinstance(val1, bool) ^ isinstance(val2, bool):
                return True
        elif isinstance(val1, type(val2)) and isinstance(val2, type(val1)):
            # otherwise both values must be of the same type
            # and values in structured values must also satisfy equality
            # constraints
            if isinstance(val1, dict):
                return all(equal(val1[k], val2[k]) for k in val1)
            if isinstance(val1, (list, tuple)):
                return all(equal(val1[i], val2[i]) for i in range(len(val1)))
            return True
    return False
