### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema keyword: const"""

from unittest import TestCase

from .test_keyword import KeywordTestBuilder

class TestConst(TestCase, metaclass=KeywordTestBuilder):
    """Test JSON Schema keyword const."""
    keyword = 'const'
    accept = (
        None, False, True,
        -1, 0, 1, -0.5, 0.0, 0.5,
        "", "foo",
        [], ["foo", "bar"],
        {}, {"foo": "bar"},
    )
    reject = ()
