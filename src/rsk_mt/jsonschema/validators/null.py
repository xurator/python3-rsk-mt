### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation`_ `null`_ validation.

   .. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
   .. _null: https://tools.ietf.org/html/draft-handrews-json-schema-01#section-4.2.1
"""
# pylint: enable=line-too-long

from rsk_mt.model import ModelledDict
from . import TypeValidator

class Null(metaclass=ModelledDict): # pylint: disable=too-few-public-methods
    """JSON Schema `null`_ type validation."""
    model = {}
    policy = 'must-ignore'
    primitive = 'null'
    def validator(self, root, schema):
        """Build a |Validator| instance implementing `null`_ validation.

        The |Validator| instance must only accept values passing the `null`_
        validation rules in |Schema| `schema` under |RootSchema| `root`.
        """
        return TypeValidator.build(root, schema, self)
