### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema keyword: items"""

from unittest import TestCase

from .test_keyword import KeywordTestBuilder

class TestItems(TestCase, metaclass=KeywordTestBuilder):
    """Test JSON Schema keyword items."""
    keyword = 'items'
    accept = (
        False, True,
        {}, {"foo": "bar"},
        [], [False], [True], [{}], [True, {"foo": "bar"}],
    )
    reject = (
        None,
        -1, 0, 1, -0.5, 0.0, 0.5,
        "", "foo",
        ["foo", "bar"],
    )
