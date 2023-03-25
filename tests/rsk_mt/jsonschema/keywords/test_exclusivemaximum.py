### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema keyword: exclusiveMaximum"""

from unittest import TestCase

from .test_keyword import KeywordTestBuilder

class TestExclusiveMaximum(TestCase, metaclass=KeywordTestBuilder):
    """Test JSON Schema keyword exclusiveMaximum."""
    keyword = 'exclusiveMaximum'
    accept = (
        -1, 0, 1, -0.5, 0.0, 0.5,
    )
    reject = (
        None, False, True,
        "", "foo",
        [], ["foo", "bar"],
        {}, {"foo": "bar"},
    )
