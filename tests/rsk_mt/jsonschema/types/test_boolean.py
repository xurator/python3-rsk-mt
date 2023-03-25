### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema type: boolean"""

from unittest import TestCase

from rsk_mt.jsonschema.types import TYPE_CORE

from .test_type import TypeTestBuilder

class TestBoolean(TestCase, metaclass=TypeTestBuilder):
    """Test JSON Schema type boolean."""
    type_name = 'boolean'
    type_ = TYPE_CORE[type_name]
    accept = (
        False, True,
    )
    reject = (
        None,
        -1, 0, 1,
        -1.5, 0.0, 1.5,
        "", "string",
        [], ["foo", "bar", "baz"],
        {}, {"foo": "bar"},
    )
