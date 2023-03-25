### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema format: hostname"""

from unittest import TestCase

from rsk_mt.jsonschema.formats import Hostname

from .test_format import FormatTestBuilder

class TestHostname(TestCase, metaclass=FormatTestBuilder):
    """Test JSON Schema format hostname."""
    constructor = Hostname
    name = 'hostname'
    validate = (
        'string',
    )
    accept = (
        "string",
        ".",
        "a." * 127,
        "A." * 127,
        "0." * 127,
        "a-a." * 63,
        "A-A." * 63,
        "0-0." * 63,
        ("a" * 63 + ".") * 3 + ("a" * 61 + "."),
        ("A" * 63 + ".") * 3 + ("A" * 61 + "."),
        ("0" * 63 + ".") * 3 + ("0" * 61 + "."),
        ("a" + "-" * 61 + "a" + ".") * 3 + ("a" + "-" * 59 + "a" + "."),
    )
    reject = (
        "",
        "a." * 127 + 'a',
        "A." * 127 + 'A',
        "0." * 127 + '0',
        "a." * 128,
        "A." * 128,
        "0." * 128,
        "a-a." * 64,
        "A-A." * 64,
        "0-0." * 64,
        ("a" * 63 + ".") * 3 + ("a" * 62),
        ("A" * 63 + ".") * 3 + ("A" * 62),
        ("0" * 63 + ".") * 3 + ("0" * 62),
        ("a" * 63 + ".") * 3 + ("a" * 62 + "."),
        ("A" * 63 + ".") * 3 + ("A" * 62 + "."),
        ("0" * 63 + ".") * 3 + ("0" * 62 + "."),
        ("a" + "-" * 62 + "a"),
    )
    invalid = (
        None,
        False, True,
        -1, 0, 1,
        -1.5, 0.0, 1.5,
        [], ["foo", "bar", "baz"],
        {}, {"foo": "bar"},
    )
