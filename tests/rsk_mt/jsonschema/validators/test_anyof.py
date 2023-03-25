### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema validator: anyOf"""

from unittest import TestCase

from rsk_mt.enforce.value import (Number, Constrained)
from rsk_mt.enforce.constraint import Range
from rsk_mt.jsonschema.validators import AnyOf

from .test_validator import (
    ValidatorTestBuilder,
    MockRoot,
    MockSchema,
)

class TestAnyOf(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator anyOf."""
    validation = AnyOf
    spec = {
        'anyOf': [
            {
                'type': 'number',
                'minimum': 10,
                'maximum': 30,
            },
            {
                'type': 'number',
                'minimum': 20,
                'maximum': 40,
            },
        ],
    }
    base_uri = 'test://anyOf/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(
            base_uri, '/anyOf/0',
            Constrained(Number(), (
                Range((
                    (spec['anyOf'][0]['minimum'], spec['anyOf'][0]['maximum']),
                )),
            )),
        ),
        MockSchema(
            base_uri, '/anyOf/1',
            Constrained(Number(), (
                Range((
                    (spec['anyOf'][1]['minimum'], spec['anyOf'][1]['maximum']),
                )),
            )),
        ),
    ))
    accept = (
        11,
        31,
        25,
    )
    reject = (
        'foo',
        5,
    )
    debug = (
        (
            11,
            True,
            {
                '': {
                    base_uri + '#': {
                        'anyOf': True,
                    },
                },
            }
        ),
        (
            'foo',
            False,
            {
                '': {
                    base_uri + '#': {
                        'anyOf': False,
                    },
                },
            }
        ),
    )
