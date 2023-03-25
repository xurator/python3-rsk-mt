### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation`_ `string`_ validation.

   .. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
   .. _string: https://tools.ietf.org/html/draft-handrews-json-schema-01#section-4.2.1
   .. _maxLength: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.3.1
   .. _minLength: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.3.2
   .. _pattern: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.3.3
"""
# pylint: enable=line-too-long

import re

from rsk_mt.model import ModelledDict
from ..types import (TYPE_NON_NEGATIVE_INTEGER, TYPE_CORE)
from . import TypeValidator

# pylint: disable=unsubscriptable-object

class String(metaclass=ModelledDict): # pylint: disable=too-few-public-methods
    """JSON Schema `string`_ type validation."""
    model = {
        'maxLength': {
            'value_type': TYPE_NON_NEGATIVE_INTEGER,
        },
        'minLength': {
            'value_type': TYPE_NON_NEGATIVE_INTEGER,
        },
        'pattern': {
            'value_type': TYPE_CORE['string'],
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
    primitive = 'string'
    def validator(self, root, schema):
        """Build a |Validator| instance implementing `string`_ validation.

        The |Validator| instance must only accept values passing the `string`_
        validation rules in |Schema| `schema` under |RootSchema| `root`.
        """
        def build_validator_pattern(pattern):
            """Build a pattern validator function.

            Return a boolean function for testing whether a string value matches
            regex `pattern`.
            """
            regexp = re.compile(pattern)
            return lambda val: regexp.search(val) is not None
        return TypeValidator.build(root, schema, self, (
            # pylint: disable=undefined-variable
            ('maxLength', lambda max_: lambda val: len(val) <= max_),
            ('minLength', lambda min_: lambda val: min_ <= len(val)),
            ('pattern', build_validator_pattern),
        ))
