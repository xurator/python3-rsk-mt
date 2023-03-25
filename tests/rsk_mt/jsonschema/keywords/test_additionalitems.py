### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema keyword: additionalItems"""

from unittest import TestCase

from .test_keyword import KeywordTestBuilder

class TestAdditionalItems(TestCase, metaclass=KeywordTestBuilder):
    """Test JSON Schema keyword additionalItems."""
    keyword = 'additionalItems'
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
