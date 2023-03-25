### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema format: uri-reference"""

from unittest import TestCase

from rsk_mt.jsonschema.formats import UriReference

from .test_format import FormatTestBuilder

class TestUriReference(TestCase, metaclass=FormatTestBuilder):
    """Test JSON Schema format uri-reference."""
    constructor = UriReference
    name = 'uri-reference'
    validate = (
        'string',
    )
    accept = (
        "", "string",
        "foo://example.com:8042/over/there?name=ferret#nose",
        "urn:example:animal:ferret:nose",
        "http://foo?bar=baz",
        "file:///etc/hostname",
        "//example.com:8042/over/there",
        "://example.com:8042/over/there",
        "/over/there",
        "there",
        "?name=ferret",
        "#nose",
    )
    reject = (
        "foo://",
        "foo://?bar=baz",
        "http://foo//bar",
        "urn:",
        "urn:?foo=bar",
        "file:////etc/hostname",
    )
    invalid = (
        None,
        False, True,
        -1, 0, 1,
        -1.5, 0.0, 1.5,
        [], ["foo", "bar", "baz"],
        {}, {"foo": "bar"},
    )
