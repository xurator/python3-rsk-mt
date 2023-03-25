### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation`_ `conditional`_ validation.

   .. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
   .. _conditional: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.6
"""
# pylint: enable=line-too-long

from rsk_mt.model import ModelledDict
from . import (Validator, TYPE_SCHEMA)

class ConditionalValidator(Validator):
    """A |Validator| implementing `conditional`_ validation.

    A |Validator| instance must only accept values that are accepted by
    `if_schema` and `then_schema` (if not None), or are not accepted by
    `if_schema` but are accepted by `else_schema` (if not None).
    """
    def __init__(self, schema, if_schema, then_schema=None, else_schema=None):
        Validator.__init__(self, schema)
        self.if_schema = if_schema
        self.then_schema = then_schema
        self.else_schema = else_schema
    def __call__(self, val):
        try:
            val = self.if_schema(val)
        except (TypeError, ValueError):
            if self.else_schema:
                val = self.else_schema(val)
        else:
            if self.then_schema:
                val = self.then_schema(val)
        return val
    def debug(self, val, results):
        valid = self.if_schema.debug(val, results)
        results.assertion(self._schema, 'if', valid)
        if valid:
            if self.then_schema:
                valid = self.then_schema.debug(val, results)
                results.assertion(self._schema, 'then', valid)
        else:
            valid = True
            if self.else_schema:
                valid = self.else_schema.debug(val, results)
                results.assertion(self._schema, 'else', valid)
        return valid

class Conditional(metaclass=ModelledDict): # pylint: disable=too-few-public-methods
    """JSON Schema `conditional`_ validation."""
    keyword = 'if'
    model = {
        'if': {
            'value_type': TYPE_SCHEMA,
        },
        'then': {
            'value_type': TYPE_SCHEMA,
        },
        'else': {
            'value_type': TYPE_SCHEMA,
        },
    }
    policy = 'must-ignore'
    @staticmethod
    def _subschema(root, schema, keyword):
        """Return the subschema at `keyword` under `schema`."""
        try:
            return root.get_schema(schema.absolute_ref(keyword))
        except KeyError:
            return None
    def validator(self, root, schema): # pylint: disable=inconsistent-return-statements
        """Build a |Validator| instance implementing `conditional`_ validation.

        The |Validator| instance must only accept values passing `conditional`_
        validation rules in |Schema| `schema` under |RootSchema| `root`.
        """
        try:
            if_schema = root.get_schema(schema.absolute_ref('if'))
        except KeyError:
            return None
        else:
            then_schema = self._subschema(root, schema, 'then')
            else_schema = self._subschema(root, schema, 'else')
            return ConditionalValidator(
                schema,
                if_schema,
                then_schema,
                else_schema,
            )
