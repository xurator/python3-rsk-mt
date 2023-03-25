### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation`_ `allOf`_ validation.

   .. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
   .. _allOf: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.7.1
"""
# pylint: enable=line-too-long

from rsk_mt.model import ModelledDict
from . import (Validator, TYPE_SCHEMA_ARRAY)

class AllOfValidator(Validator):
    """A |Validator| implementing `anyOf`_ validation.

    A |Validator| instance must only accept values accepted by all schemas in
    `schemas`.
    """
    def __init__(self, schema, keyword, schemas):
        Validator.__init__(self, schema)
        self._keyword = keyword
        self._schemas = schemas
    def __call__(self, val):
        for schema in self._schemas:
            val = schema(val)
        return val
    def debug(self, val, results):
        valid = True
        for schema in self._schemas:
            valid = schema.debug(val, results) and valid
        results.assertion(self._schema, self._keyword, valid)
        return valid

class AllOf(metaclass=ModelledDict): # pylint: disable=too-few-public-methods
    """JSON Schema `allOf`_ validation."""
    keyword = 'allOf'
    model = {
        keyword: {
            'value_type': TYPE_SCHEMA_ARRAY,
        },
    }
    policy = 'must-ignore'
    def validator(self, root, schema):
        """Build a |Validator| instance implementing `allOf`_ validation.

        The |Validator| instance must only accept values passing the `allOf`_
        validation rules in |Schema| `schema` under |RootSchema| `root`.
        """
        subschemas = []
        for idx in range(len(self[self.keyword])): # pylint: disable=unsubscriptable-object
            ref = schema.absolute_ref(self.keyword, idx)
            subschemas.append(root.get_schema(ref))
        return AllOfValidator(schema, self.keyword, subschemas)
