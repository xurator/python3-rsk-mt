### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema keyword: dependencies"""

from unittest import TestCase

from .test_keyword import KeywordTestBuilder

class TestDependencies(TestCase, metaclass=KeywordTestBuilder):
    """Test JSON Schema keyword dependencies."""
    keyword = 'dependencies'
    accept = (
        {},
        {"foo": {"bar": "baz"}},
        {"foo": ["bar", "baz"]},
    )
    reject = (
        None, False, True,
        -1, 0, 1, -0.5, 0.0, 0.5,
        "", "foo",
        [], ["foo", "bar"],
        {"foo": "bar"},
        {"foo": ["bar", 1]},
    )
