### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema validator: enum"""

from unittest import TestCase

from rsk_mt.jsonschema.validators import Enum

from .test_validator import (
    ValidatorTestBuilder,
    MockRoot,
)

class TestEnum(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator enum."""
    validation = Enum
    spec = {
        'enum': [
            None,
            False,
            True,
            123,
            4.5,
            'string',
            (),
            [1, 2, 3],
            {},
            {"a": "b"},
            ### duplicates ok
            None,
            True,
            4.5,
        ],
    }
    base_uri = 'test://enum/'
    root = MockRoot(base_uri)
    accept = tuple(
        spec['enum']
    )
    reject = (
        'this-string-not-in-enum',
        (9, 10),
    )
