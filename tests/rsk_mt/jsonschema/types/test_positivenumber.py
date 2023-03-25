### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema type: positive-number"""

from unittest import TestCase

from rsk_mt.jsonschema.types import TYPE_POSITIVE_NUMBER

from .test_type import TypeTestBuilder

class TestPositiveNumber(TestCase, metaclass=TypeTestBuilder):
    """Test JSON Schema type positive-number."""
    type_name = 'positive-number'
    type_ = TYPE_POSITIVE_NUMBER
    accept = (
        1,
        1.5,
    )
    reject = (
        None,
        False, True,
        -1, 0,
        -1.5, 0.0,
        "", "string",
        [], ["foo", "bar", "baz"],
        {}, {"foo": "bar"},
    )
