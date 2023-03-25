### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema keyword: maxItems"""

from unittest import TestCase

from .test_keyword import KeywordTestBuilder

class TestMaxItems(TestCase, metaclass=KeywordTestBuilder):
    """Test JSON Schema keyword maxItems."""
    keyword = 'maxItems'
    accept = (
        0, 1,
    )
    reject = (
        None, False, True,
        -1, -0.5, 0.0, 0.5,
        "", "foo",
        [], ["foo", "bar"],
        {}, {"foo": "bar"},
    )
