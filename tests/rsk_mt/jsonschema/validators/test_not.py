### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema validator: not"""

from unittest import TestCase

from rsk_mt.enforce.value import (String, Constrained)
from rsk_mt.enforce.constraint import Pattern
from rsk_mt.jsonschema.validators import Not

from .test_validator import (
    ValidatorTestBuilder,
    MockRoot,
    MockSchema,
)

class TestNot(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator not."""
    validation = Not
    spec = {
        'not': {
            'type': 'string',
            'pattern': '^x*',
        },
    }
    base_uri = 'test://not/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(
            base_uri, '/not',
            Constrained(String(), (
                Pattern(spec['not']['pattern']),
            )),
        ),
    ))
    accept = (
        None,
        77,
    )
    reject = (
        # reject a matching string
        'xyz',
    )
    debug = (
        (
            'xyz',
            False,
            {
                '': {
                    base_uri + '#': {
                        'not': False,
                    },
                },
            }
        ),
    )
