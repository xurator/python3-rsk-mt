### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema format: uri"""

from unittest import TestCase

from rsk_mt.jsonschema.formats import Uri

from .test_format import FormatTestBuilder

class TestUri(TestCase, metaclass=FormatTestBuilder):
    """Test JSON Schema format uri."""
    constructor = Uri
    name = 'uri'
    validate = (
        'string',
    )
    accept = (
        "foo://example.com:8042/over/there?name=ferret#nose",
        "urn:example:animal:ferret:nose",
        "http://foo?bar=baz",
        "file:///etc/hostname",
    )
    reject = (
        "", "string",
        "foo://",
        "foo://?bar=baz",
        "//example.com:8042/over/there",
        "://example.com:8042/over/there",
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
