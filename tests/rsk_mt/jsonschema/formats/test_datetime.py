### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema formats: date-time, date, time"""

from unittest import TestCase

from rsk_mt.jsonschema.formats import (
    DateTime,
    Date,
    Time,
)

from .test_format import FormatTestBuilder

class TestDateTime(TestCase, metaclass=FormatTestBuilder):
    """Test JSON Schema format date-time."""
    constructor = DateTime
    name = 'date-time'
    validate = (
        'string',
    )
    accept = (
        ### RFC 3339 examples
        '1985-04-12T23:20:50.52Z',
        '1996-12-19T16:39:57-08:00',
        '1937-01-01T12:00:27.87+00:20',
    )
    reject = (
        "", "string",
        ### leap seconds cause a test failure
        '1990-12-31T23:59:60Z',
        '1990-12-31T15:59:60-08:00',
        ### legal structure, bad values
        '2017-13-01T00:00:00Z',
        '2017-01-32T00:00:00Z',
        '2017-01-01T24:00:00Z',
        '2017-01-01T00:60:00Z',
        '2017-01-01T00:00:60Z',
        '2017-01-01T00:00:00.9999999Z',
        '2017-01-01T00:00:00.9999999999999999999999999999999999999Z',
        '2017-01-01T00:00:00-24:00',
        '2017-01-01T00:00:00+00:60',
    )
    invalid = (
        None,
        False, True,
        -1, 0, 1,
        -1.5, 0.0, 1.5,
        [], ["foo", "bar", "baz"],
        {}, {"foo": "bar"},
    )

class TestDate(TestCase, metaclass=FormatTestBuilder):
    """Test JSON Schema format date."""
    constructor = Date
    name = 'date'
    validate = (
        'string',
    )
    accept = (
        '1985-04-12',
        '1996-12-19',
        '1937-01-01',
    )
    reject = (
        "", "string",
        ### legal structure, bad values
        '2017-13-01',
        '2017-01-32',
    )
    invalid = (
        None,
        False, True,
        -1, 0, 1,
        -1.5, 0.0, 1.5,
        [], ["foo", "bar", "baz"],
        {}, {"foo": "bar"},
    )

class TestTime(TestCase, metaclass=FormatTestBuilder):
    """Test JSON Schema format time."""
    constructor = Time
    name = 'time'
    validate = (
        'string',
    )
    accept = (
        ### RFC 3339 examples
        '23:20:50.52Z',
        '16:39:57-08:00',
        '12:00:27.87+00:20',
    )
    reject = (
        "", "string",
        ### legal structure, bad values
        '24:00:00Z',
        '00:60:00Z',
        '00:00:60Z',
        '00:00:00.9999999Z',
        '00:00:00.9999999999999999999999999999999999999Z',
        '00:00:00-24:00',
        '00:00:00+00:60',
    )
    invalid = (
        None,
        False, True,
        -1, 0, 1,
        -1.5, 0.0, 1.5,
        [], ["foo", "bar", "baz"],
        {}, {"foo": "bar"},
    )
