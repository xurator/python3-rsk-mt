### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema validator: allOf"""

from unittest import TestCase

from rsk_mt.enforce.value import (String, Constrained)
from rsk_mt.enforce.constraint import (Length, Pattern)
from rsk_mt.jsonschema.validators import AllOf

from .test_validator import (
    ValidatorTestBuilder,
    MockRoot,
    MockSchema,
)

class TestAllOf(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator allOf."""
    validation = AllOf
    spec = {
        'allOf': [
            {
                'type': 'string',
                'minLength': 5,
            },
            {
                'type': 'string',
                'pattern': 'aa*bb*',
            },
        ],
    }
    base_uri = 'test://allOf/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(
            base_uri, '/allOf/0',
            Constrained(String(), (
                Length.yang(f"{spec['allOf'][0]['minLength']} .. max"),
            )),
        ),
        MockSchema(
            base_uri, '/allOf/1',
            Constrained(String(), (
                Pattern(spec['allOf'][1]['pattern']),
            )),
        ),
    ))
    accept = (
        'aabbb',
    )
    reject = (
        99,
        '',
        'aabb',
    )
    debug = (
        (
            'aabbb',
            True,
            {
                '': {
                    base_uri + '#': {
                        'allOf': True,
                    },
                },
            }
        ),
        (
            99,
            False,
            {
                '': {
                    base_uri + '#': {
                        'allOf': False,
                    },
                },
            },
        ),
    )
