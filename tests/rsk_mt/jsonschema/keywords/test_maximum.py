### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema keyword: maximum"""

from unittest import TestCase

from .test_keyword import KeywordTestBuilder

class TestMaximum(TestCase, metaclass=KeywordTestBuilder):
    """Test JSON Schema keyword maximum."""
    keyword = 'maximum'
    accept = (
        -1, 0, 1, -0.5, 0.0, 0.5,
    )
    reject = (
        None, False, True,
        "", "foo",
        [], ["foo", "bar"],
        {}, {"foo": "bar"},
    )
