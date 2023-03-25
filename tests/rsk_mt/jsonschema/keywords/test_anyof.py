### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema keyword: anyOf"""

from unittest import TestCase

from .test_keyword import KeywordTestBuilder

class TestAnyOf(TestCase, metaclass=KeywordTestBuilder):
    """Test JSON Schema keyword anyOf."""
    keyword = 'anyOf'
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
