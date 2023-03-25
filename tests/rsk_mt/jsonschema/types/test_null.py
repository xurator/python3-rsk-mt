### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema type: null"""

from unittest import TestCase

from rsk_mt.jsonschema.types import TYPE_CORE

from .test_type import TypeTestBuilder

class TestNull(TestCase, metaclass=TypeTestBuilder):
    """Test JSON Schema type null."""
    type_name = 'null'
    type_ = TYPE_CORE[type_name]
    accept = (
        None,
    )
    reject = (
        False, True,
        -1, 0, 1,
        -1.5, 0.0, 1.5,
        "", "string",
        [], ["foo", "bar", "baz"],
        {}, {"foo": "bar"},
    )
