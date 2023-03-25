### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema type: integer"""

from unittest import TestCase

from rsk_mt.jsonschema.types import TYPE_CORE

from .test_type import TypeTestBuilder

class TestInteger(TestCase, metaclass=TypeTestBuilder):
    """Test JSON Schema type integer."""
    type_name = 'integer'
    type_ = TYPE_CORE[type_name]
    accept = (
        -1, 0, 1,
    )
    reject = (
        None,
        False, True,
        -1.5, 0.0, 1.5,
        "", "string",
        [], ["foo", "bar", "baz"],
        {}, {"foo": "bar"},
    )
