### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema keyword: then"""

from unittest import TestCase

from .test_keyword import KeywordTestBuilder

class TestThen(TestCase, metaclass=KeywordTestBuilder):
    """Test JSON Schema keyword then."""
    keyword = 'then'
    accept = (
        False, True,
        {}, {"foo": "bar"},
    )
    reject = (
        None,
        -1, 0, 1, -0.5, 0.0, 0.5,
        "", "foo",
        [], ["foo", "bar"],
    )
