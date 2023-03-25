### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema keyword: allOf"""

from unittest import TestCase

from .test_keyword import KeywordTestBuilder

class TestAllOf(TestCase, metaclass=KeywordTestBuilder):
    """Test JSON Schema keyword allOf."""
    keyword = 'allOf'
    accept = (
        [{}],
        [{}, {"foo": "bar"}],
    )
    reject = (
        None, False, True,
        -1, 0, 1, -0.5, 0.0, 0.5,
        "", "foo",
        [], ["foo", "bar"],
        {}, {"foo": "bar"},
    )
