### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema keyword: uniqueItems"""

from unittest import TestCase

from .test_keyword import KeywordTestBuilder

class TestUniqueItems(TestCase, metaclass=KeywordTestBuilder):
    """Test JSON Schema keyword uniqueItems."""
    keyword = 'uniqueItems'
    accept = (
        False, True,
    )
    reject = (
        None,
        -1, 0, 1, -0.5, 0.0, 0.5,
        "", "foo",
        [], ["foo", "bar"],
        {}, {"foo": "bar"},
    )
