### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation`_ `oneOf`_ validation.

   .. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
   .. _oneOf: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.7.3
"""
# pylint: enable=line-too-long

from rsk_mt.model import ModelledDict
from . import (Validator, TYPE_SCHEMA_ARRAY)

class OneOfValidator(Validator):
    """A |Validator| implementing `oneOf`_ validation.

    A |Validator| instance must only accept values that are accepted by exactly
    one schema in `schemas`.
    """
    def __init__(self, schema, keyword, schemas):
        Validator.__init__(self, schema)
        self._keyword = keyword
        self._schemas = schemas
    def __call__(self, val):
        accepted = None
        valid = 0
        for schema in self._schemas:
            try:
                accepted = schema(val)
            except (TypeError, ValueError):
                continue
            else:
                valid += 1
                if valid > 1:
                    raise ValueError(val)
        if not valid:
            raise ValueError(val)
        return accepted
    def debug(self, val, results):
        valid = 0
        for schema in self._schemas:
            if schema.debug(val, results):
                valid += 1
        valid = valid == 1
        results.assertion(self._schema, self._keyword, valid)
        return valid

class OneOf(metaclass=ModelledDict): # pylint: disable=too-few-public-methods
    """JSON Schema `oneOf`_ validation."""
    keyword = 'oneOf'
    model = {
        keyword: {
            'value_type': TYPE_SCHEMA_ARRAY,
        },
    }
    policy = 'must-ignore'
    def validator(self, root, schema):
        """Build a |Validator| instance implementing `oneOf`_ validation.

        The |Validator| instance must accept values passing the `oneOf`_
        validation rules in |Schema| `schema` under |RootSchema| `root`.
        """
        # pylint: disable=unsubscriptable-object
        subschemas = []
        for idx in range(len(self[self.keyword])):
            ref = schema.absolute_ref(self.keyword, idx)
            subschemas.append(root.get_schema(ref))
        return OneOfValidator(schema, self.keyword, subschemas)
