### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation` `const`_ validation.

   .. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
   .. _const: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.1.3
"""
# pylint: enable=line-too-long

from rsk_mt.model import ModelledDict
from . import (Validator, equal)

class Const(metaclass=ModelledDict): # pylint: disable=too-few-public-methods
    """JSON Schema `const`_ validation."""
    keyword = 'const'
    model = {
        keyword: {},
    }
    policy = 'must-ignore'
    def validator(self, root, schema): # pylint: disable=unused-argument
        """Build a |Validator| instance implementing `const`_ validation.

        The |Validator| instance must only accept values passing the `const`_
        validation rules in |Schema| `schema` under |RootSchema| `root`.
        """
        return Validator.build(root, schema, self, (
            # pylint: disable=undefined-variable
            (self.keyword, lambda const: lambda val: equal(const, val)),
        ))
