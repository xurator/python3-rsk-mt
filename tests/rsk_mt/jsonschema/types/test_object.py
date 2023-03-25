### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema type: object"""

from unittest import TestCase

from rsk_mt.jsonschema.types import TYPE_CORE

from .test_type import TypeTestBuilder

class TestObject(TestCase, metaclass=TypeTestBuilder):
    """Test JSON Schema type object."""
    type_name = 'object'
    type_ = TYPE_CORE[type_name]
    accept = (
        {}, {"foo": "bar"},
    )
    reject = (
        None,
        False, True,
        -1, 0, 1,
        -1.5, 0.0, 1.5,
        "", "string",
        [], ["foo", "bar", "baz"],
    )
