### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema validator: oneOf"""

from unittest import TestCase

from rsk_mt.enforce.value import (Number, Constrained)
from rsk_mt.enforce.constraint import Range
from rsk_mt.jsonschema.validators import OneOf

from .test_validator import (
    ValidatorTestBuilder,
    MockRoot,
    MockSchema,
)

class TestOneOf(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator oneOf."""
    validation = OneOf
    spec = {
        'oneOf': [
            {
                'type': 'number',
                'minimum': 50,
            },
            {
                'type': 'number',
                'minimum': 60,
            },
        ],
    }
    base_uri = 'test://oneOf/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(
            base_uri, '/oneOf/0',
            Constrained(Number(), (
                Range.yang(f"{spec['oneOf'][0]['minimum']} .. max"),
            )),
        ),
        MockSchema(
            base_uri, '/oneOf/1',
            Constrained(Number(), (
                Range.yang(f"{spec['oneOf'][1]['minimum']} .. max"),
            )),
        ),
    ))
    accept = (
        50,
        59,
    )
    reject = (
        'bar',
        49,
        60,
    )
    debug = (
        (
            50,
            True,
            {
                '': {
                    base_uri + '#': {
                        'oneOf': True,
                    },
                },
            },
        ),
    )
