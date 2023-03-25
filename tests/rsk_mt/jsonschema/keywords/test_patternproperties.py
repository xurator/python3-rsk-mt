### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema keyword: patternProperties"""

from unittest import TestCase

from .test_keyword import KeywordTestBuilder

class TestPatternProperties(TestCase, metaclass=KeywordTestBuilder):
    """Test JSON Schema keyword patternProperties."""
    keyword = 'patternProperties'
    accept = (
        {},
        {"foo": {"bar": "baz"}},
    )
    reject = (
        None, False, True,
        -1, 0, 1, -0.5, 0.0, 0.5,
        "", "foo",
        [], ["foo", "bar"],
        {"foo": "bar"},
    )
