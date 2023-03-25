### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema validator: null"""

from unittest import TestCase

from rsk_mt.jsonschema.validators import Null

from .test_validator import (
    ValidatorTestBuilder,
    MockRoot,
)

class TestNull(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator null."""
    validation = Null
    spec = {}
    base_uri = 'test://null/'
    root = MockRoot(base_uri)
    accept = (
        None,
    )
    reject = (
        False, True,
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )
