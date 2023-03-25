### SPDX-License-Identifier: GPL-2.0-or-later

"""Tests for JSON Schema keyword: pattern"""

from unittest import TestCase

from .test_keyword import KeywordTestBuilder

class TestPattern(TestCase, metaclass=KeywordTestBuilder):
    """Test JSON Schema keyword pattern."""
    keyword = 'pattern'
    accept = (
        "", "foo",
    )
    reject = (
        None, False, True,
        -1, 0, 1, -0.5, 0.0, 0.5,
        [], ["foo", "bar"],
        {}, {"foo": "bar"},
    )
