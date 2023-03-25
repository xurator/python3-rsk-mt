### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema keyword: contentEncoding"""

from unittest import TestCase

from .test_keyword import KeywordTestBuilder

class TestContentEncoding(TestCase, metaclass=KeywordTestBuilder):
    """Test JSON Schema keyword contentEncoding."""
    keyword = 'contentEncoding'
    accept = (
        "", "foo",
    )
    reject = (
        None, False, True,
        -1, 0, 1, -0.5, 0.0, 0.5,
        [], ["foo", "bar"],
        {}, {"foo": "bar"},
    )
