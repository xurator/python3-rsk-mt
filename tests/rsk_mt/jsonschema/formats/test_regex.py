### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema format: regex"""

from unittest import TestCase

from rsk_mt.jsonschema.formats import Regex

from .test_format import FormatTestBuilder

class TestRegex(TestCase, metaclass=FormatTestBuilder):
    """Test JSON Schema format regex."""
    constructor = Regex
    name = 'regex'
    validate = (
        'string',
    )
    accept = (
        "", "string",
        "(foo){1,2}",
    )
    reject = (
        "fo(o",
        "foo)",
    )
    invalid = (
        None,
        False, True,
        -1, 0, 1,
        -1.5, 0.0, 1.5,
        [], ["foo", "bar", "baz"],
        {}, {"foo": "bar"},
    )
