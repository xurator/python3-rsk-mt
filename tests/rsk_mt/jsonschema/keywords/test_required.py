### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema keyword: required"""

from unittest import TestCase

from .test_keyword import KeywordTestBuilder

class TestRequired(TestCase, metaclass=KeywordTestBuilder):
    """Test JSON Schema keyword required."""
    keyword = 'required'
    accept = (
        [],
        ["foo"],
        ["foo", "bar"],
    )
    reject = (
        None, False, True,
        -1, 0, 1, -0.5, 0.0, 0.5,
        "", "foo",
        [1], ["foo", 1],
        {}, {"foo": "bar"},
    )
