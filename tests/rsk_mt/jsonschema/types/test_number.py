### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema type: number"""

from unittest import TestCase

from rsk_mt.jsonschema.types import TYPE_CORE

from .test_type import TypeTestBuilder

class TestNumber(TestCase, metaclass=TypeTestBuilder):
    """Test JSON Schema type number."""
    type_name = 'number'
    type_ = TYPE_CORE[type_name]
    accept = (
        -1, 0, 1,
        -1.5, 0.0, 1.5,
    )
    reject = (
        None,
        False, True,
        "", "string",
        [], ["foo", "bar", "baz"],
        {}, {"foo": "bar"},
    )
