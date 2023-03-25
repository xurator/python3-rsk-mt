### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema keyword: type"""

from unittest import TestCase

from .test_keyword import KeywordTestBuilder

class TestType(TestCase, metaclass=KeywordTestBuilder):
    """Test JSON Schema keyword type."""
    keyword = 'type'
    accept = (
        "null", "boolean", "integer", "number", "string", "array", "object",
        ["number"],
        ["null", "boolean", "integer", "number", "string", "array", "object"],
    )
    reject = (
        None, False, True,
        -1, 0, 1, -0.5, 0.0, 0.5,
        "", "foo",
        [], ["foo", "bar"],
        {}, {"foo": "bar"},
    )
