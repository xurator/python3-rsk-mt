### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation`_ `enum`_ validation.

   .. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
   .. _enum: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.1.2
"""
# pylint: enable=line-too-long

from rsk_mt.model import ModelledDict
from . import (Validator, equal)
from ..types import TYPE_CORE

class Enum(metaclass=ModelledDict): # pylint: disable=too-few-public-methods
    """JSON Schema `enum`_ validation."""
    keyword = 'enum'
    model = {
        keyword: {
            'value_type': TYPE_CORE['array'],
        },
    }
    policy = 'must-ignore'
    def validator(self, root, schema): # pylint: disable=unused-argument
        """Build a |Validator| instance implementing `enum`_ validation.

        The |Validator| instance must only accept values passing the `enum`_
        validation rules in |Schema| `schema` under |RootSchema| `root`.
        """
        # pylint: disable=used-before-assignment
        func = lambda enum: lambda val: any(equal(val, item) for item in enum)
        return Validator.build(root, schema, self, (
            (self.keyword, func),
        ))
