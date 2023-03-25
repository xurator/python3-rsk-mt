### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema keyword: multipleOf"""

from unittest import TestCase

from .test_keyword import KeywordTestBuilder

class TestMultipleOf(TestCase, metaclass=KeywordTestBuilder):
    """Test JSON Schema keyword multipleOf."""
    keyword = 'multipleOf'
    accept = (
        0.5, 1,
    )
    reject = (
        None, False, True,
        -1, 0, -0.5, 0.0,
        "", "foo",
        [], ["foo", "bar"],
        {}, {"foo": "bar"},
    )
