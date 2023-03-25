### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema type: string"""

from unittest import TestCase

from rsk_mt.jsonschema.types import TYPE_CORE

from .test_type import TypeTestBuilder

class TestString(TestCase, metaclass=TypeTestBuilder):
    """Test JSON Schema type string."""
    type_name = 'string'
    type_ = TYPE_CORE[type_name]
    accept = (
        "", "string",
    )
    reject = (
        None,
        False, True,
        -1, 0, 1,
        -1.5, 0.0, 1.5,
        [], ["foo", "bar", "baz"],
        {}, {"foo": "bar"},
    )
