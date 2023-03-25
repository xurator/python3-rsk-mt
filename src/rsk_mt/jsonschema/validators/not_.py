### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation`_ `not`_ validation.

   .. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
   .. _not: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.7.4
"""
# pylint: enable=line-too-long

from rsk_mt.model import ModelledDict
from . import (Validator, TYPE_SCHEMA)

class NotValidator(Validator):
    """A |Validator| implementing `not`_ validation.

    A |Validator| instance must only accept values that are not accepted by
    `not_schema`.
    """
    def __init__(self, schema, keyword, not_schema):
        Validator.__init__(self, schema)
        self._keyword = keyword
        self._not_schema = not_schema
    def __call__(self, val):
        try:
            self._not_schema(val)
        except (TypeError, ValueError):
            return val
        else:
            raise ValueError(val)
    def debug(self, val, results):
        valid = True ^ bool(self._not_schema.debug(val, results))
        results.assertion(self._schema, self._keyword, valid)
        return valid

class Not(metaclass=ModelledDict): # pylint: disable=too-few-public-methods
    """JSON Schema `not`_ validation."""
    keyword = 'not'
    model = {
        keyword: {
            'value_type': TYPE_SCHEMA,
        },
    }
    policy = 'must-ignore'
    def validator(self, root, schema):
        """Build a |Validator| instance implementing `not`_ validation.

        The |Validator| instance must only accept values passing the `not`_
        validation rules in |Schema| `schema` under |RootSchema| `root`.
        """
        ref = schema.absolute_ref(self.keyword)
        subschema = root.get_schema(ref)
        return NotValidator(schema, self.keyword, subschema)
