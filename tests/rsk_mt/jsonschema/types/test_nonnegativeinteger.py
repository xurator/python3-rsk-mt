### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema type: non-negative-integer"""

from unittest import TestCase

from rsk_mt.jsonschema.types import TYPE_NON_NEGATIVE_INTEGER

from .test_type import TypeTestBuilder

class TestNonNegativeInteger(TestCase, metaclass=TypeTestBuilder):
    """Test JSON Schema type non-negative-integer."""
    type_name = 'non-negative-integer'
    type_ = TYPE_NON_NEGATIVE_INTEGER
    accept = (
        0, 1,
    )
    reject = (
        None,
        False, True,
        -1,
        -1.5, 0.0, 1.5,
        "", "string",
        [], ["foo", "bar", "baz"],
        {}, {"foo": "bar"},
    )
