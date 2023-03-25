### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema format: ipv6"""

from unittest import TestCase

from rsk_mt.jsonschema.formats import IPv6

from .test_format import FormatTestBuilder

class TestIPv6(TestCase, metaclass=FormatTestBuilder):
    """Test JSON Schema format ipv6."""
    constructor = IPv6
    name = 'ipv6'
    validate = (
        'string',
    )
    accept = (
        "FEDC:BA98:7654:3210:FEDC:BA98:7654:3210",
        "1080:0:0:0:8:800:200C:417A",
        "1080::8:800:200C:417A",
        "FF01:0:0:0:0:0:0:101",
        "FF01::101",
        "0:0:0:0:0:0:0:1",
        "::1",
        "0:0:0:0:0:0:0:0",
        "::",
        "0:0:0:0:0:0:13.1.68.3",
        "::13.1.68.3",
        "0:0:0:0:0:FFFF:129.144.52.38",
        "::FFFF:129.144.52.38",
    )
    reject = (
        "", "string",
    )
    invalid = (
        None,
        False, True,
        -1, 0, 1,
        -1.5, 0.0, 1.5,
        [], ["foo", "bar", "baz"],
        {}, {"foo": "bar"},
    )
