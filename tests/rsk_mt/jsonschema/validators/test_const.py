### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema validator: const"""

from unittest import TestCase

from rsk_mt.jsonschema.validators import Const

from .test_validator import (
    ValidatorTestBuilder,
    MockRoot,
)

class TestConst(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator const."""
    validation = Const
    spec = {
        'const': 'foo',
    }
    base_uri = 'test://const/'
    root = MockRoot(base_uri)
    accept = (
        'foo',
    )
    reject = (
        'bar',
    )
