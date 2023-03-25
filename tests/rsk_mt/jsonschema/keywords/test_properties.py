### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema keyword: properties"""

from unittest import TestCase

from .test_keyword import KeywordTestBuilder

class TestProperties(TestCase, metaclass=KeywordTestBuilder):
    """Test JSON Schema keyword properties."""
    keyword = 'properties'
    accept = (
        {},
        {"foo": {}},
        {"foo": {"bar": "baz"}},
    )
    reject = (
        None, False, True,
        -1, 0, 1, -0.5, 0.0, 0.5,
        "", "foo",
        [], ["foo", "bar"],
        {"foo": "bar"},
    )
