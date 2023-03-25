### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation`_ `number`_ and `integer`_ validation.

   .. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
   .. _integer: https://tools.ietf.org/html/draft-handrews-json-schema-01#section-4.2.1
   .. _number: https://tools.ietf.org/html/draft-handrews-json-schema-01#section-4.2.1
   .. _multipleOf: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.2.1
   .. _maximum: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.2.2
   .. _exclusiveMaximum: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.2.3
   .. _minimum: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.2.4
   .. _exclusiveMinimum: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.2.5
"""
# pylint: enable=line-too-long

from rsk_mt.model import ModelledDict
from ..types import (TYPE_CORE, TYPE_POSITIVE_NUMBER)
from . import TypeValidator

MODEL_NUMBER = {
    'multipleOf': {
        'value_type': TYPE_POSITIVE_NUMBER,
    },
    'maximum': {
        'value_type': TYPE_CORE['number'],
    },
    'exclusiveMaximum': {
        'value_type': TYPE_CORE['number'],
    },
    'minimum': {
        'value_type': TYPE_CORE['number'],
    },
    'exclusiveMinimum': {
        'value_type': TYPE_CORE['number'],
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

def validator(validation, root, schema):
    """Build a |Validator| instance implementing numeric `validation`.

    The |Validator| instance must only accept values passing the `integer`_ or
    `number`_ `validation` rules in |Schema| `schema` under |RootSchema| `root`.
    """
    return TypeValidator.build(root, schema, validation, (
        # pylint: disable=undefined-variable
        ('multipleOf', lambda div: lambda val: int(val/div) == val/div),
        ('maximum', lambda max_: lambda val: val <= max_),
        ('exclusiveMaximum', lambda emax: lambda val: val < emax),
        ('minimum', lambda min_: lambda val: min_ <= val),
        ('exclusiveMinimum', lambda emin: lambda val: emin < val),
    ))

class Integer(metaclass=ModelledDict): # pylint: disable=too-few-public-methods
    """JSON schema `integer`_ type validation."""
    model = MODEL_NUMBER
    policy = 'must-ignore'
    primitive = 'integer'
    validator = validator

class Number(metaclass=ModelledDict): # pylint: disable=too-few-public-methods
    """JSON Schema `number`_ type validation."""
    model = MODEL_NUMBER
    policy = 'must-ignore'
    primitive = 'number'
    validator = validator
