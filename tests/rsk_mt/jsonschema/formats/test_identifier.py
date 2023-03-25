### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema format: location-independent-$id"""

from unittest import TestCase

from rsk_mt.jsonschema.formats import LocationIndependentId

from .test_format import FormatTestBuilder

class TestLocationIndependentId(TestCase, metaclass=FormatTestBuilder):
    """Test JSON Schema format location-independent-$id."""
    constructor = LocationIndependentId
    name = 'location-independent-$id'
    validate = (
        'string',
    )
    accept = (
        "#A", "#z",
        "#Aa", "#zZ",
        "#A0", "#z9",
        "#A-", "#z-",
        "#A_", "#z_",
        "#A:", "#z:",
        "#A.", "#z.",
    )
    reject = (
        "foo",
        "#",
        "#1",
        "#-",
        "#_",
        "#:",
        "#.",
        "#A^",
        "#A$",
    )
    invalid = (
        None,
        False, True,
        -1, 0, 1,
        -1.5, 0.0, 1.5,
        [], ["foo", "bar", "baz"],
        {}, {"foo": "bar"},
    )
