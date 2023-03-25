### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation`_ `boolean`_ validation.

   .. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
   .. _boolean: https://tools.ietf.org/html/draft-handrews-json-schema-01#section-4.2.1
"""
# pylint: enable=line-too-long

from rsk_mt.model import ModelledDict
from . import TypeValidator

class Boolean(metaclass=ModelledDict): # pylint: disable=too-few-public-methods
    """JSON Schema `boolean`_ type validation."""
    model = {}
    policy = 'must-ignore'
    primitive = 'boolean'
    def validator(self, root, schema):
        """Build a |Validator| instance implementing `boolean`_ validation.

        The |Validator| instance must only accept values passing the `boolean`_
        validation rules in |Schema| `schema` under |RootSchema| `root`.
        """
        return TypeValidator.build(root, schema, self)
