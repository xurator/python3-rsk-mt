### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema keyword: contentMediaType"""

from unittest import TestCase

from .test_keyword import KeywordTestBuilder

class TestContentMediaType(TestCase, metaclass=KeywordTestBuilder):
    """Test JSON Schema keyword contentMediaType."""
    keyword = 'contentMediaType'
    accept = (
        "", "foo",
    )
    reject = (
        None, False, True,
        -1, 0, 1, -0.5, 0.0, 0.5,
        [], ["foo", "bar"],
        {}, {"foo": "bar"},
    )
