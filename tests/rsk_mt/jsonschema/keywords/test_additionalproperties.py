### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema keyword: additionalProperties"""

from unittest import TestCase

from .test_keyword import KeywordTestBuilder

class TestAdditionalProperties(TestCase, metaclass=KeywordTestBuilder):
    """Test JSON Schema keyword additionalProperties."""
    keyword = 'additionalProperties'
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
