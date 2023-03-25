### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema keyword: contains"""

from unittest import TestCase

from .test_keyword import KeywordTestBuilder

class TestContains(TestCase, metaclass=KeywordTestBuilder):
    """Test JSON Schema keyword contains."""
    keyword = 'contains'
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
