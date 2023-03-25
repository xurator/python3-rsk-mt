### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema keyword: enum"""

from unittest import TestCase

from .test_keyword import KeywordTestBuilder

class TestEnum(TestCase, metaclass=KeywordTestBuilder):
    """Test JSON Schema keyword enum."""
    keyword = 'enum'
    accept = (
        [], ["foo", "bar"],
    )
    reject = (
        None, False, True,
        -1, 0, 1, -0.5, 0.0, 0.5,
        "", "foo",
        {}, {"foo": "bar"},
    )
