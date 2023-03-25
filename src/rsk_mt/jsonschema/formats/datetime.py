### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation`_ `date and time`_ formats using :mod:`datetime`.

.. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
.. _date and time: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-7.3.1
.. _date-time: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-7.3.1
.. _date: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-7.3.1
.. _time: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-7.3.1
.. _RFC 3339: https://tools.ietf.org/html/rfc3339#section-5.6
"""
# pylint: enable=line-too-long

import re
from datetime import (datetime, timedelta, timezone, date, time)

from . import Format

FULL_DATE = '-'.join((
    r'(?P<year>\d{4})',
    r'(?P<month>\d{2})',
    r'(?P<day>\d{2})',
))
PARTIAL_TIME = ':'.join((
    r'(?P<hour>\d{2})',
    r'(?P<minute>\d{2})',
    r'(?P<second>\d{2})(\.(?P<usecond>\d+))?',
))
TIME_OFFSET = r'(Z|(?P<tzsign>[\+\-])(?P<tzhour>\d{2}):(?P<tzminute>\d{2}))'
FULL_TIME = PARTIAL_TIME + TIME_OFFSET

class DateTime(Format):
    """Semantic validation of `date-time`_ strings per `RFC 3339`_."""
    name = 'date-time'
    regexp = re.compile(r'^' + FULL_DATE + r'T' + FULL_TIME + r'$')
    def validates(self, primitive):
        return primitive == 'string'
    def __call__(self, val):
        try:
            match = self.regexp.match(val)
        except TypeError:
            return False
        if not match:
            return False
        parsed = {}
        for (key, value) in match.groupdict().items():
            try:
                parsed[key] = int(value, base=10)
            except (TypeError, ValueError):
                parsed[key] = value
        return self.test_parsed(parsed)
    def test_parsed(self, parsed):
        """Return True if `parsed` pairs are valid for format, else False."""
        (year, month, day) = self.date(parsed)
        (hour, minute, second, microsecond) = self.time(parsed)
        tzinfo = self.tzinfo(parsed)
        if tzinfo is False:
            return False
        try:
            datetime(
                year, month, day,
                hour, minute, second, microsecond,
                tzinfo,
            )
        except (ValueError, OverflowError):
            return False
        else:
            return True
    @staticmethod
    def date(parsed):
        """Return date from `parsed` as (year, month, day)."""
        return (parsed['year'], parsed['month'], parsed['day'])
    @staticmethod
    def time(parsed):
        """Return time from `parsed` as (hour, minute, second, microsecond)."""
        microsecond = 0 if parsed['usecond'] is None else parsed['usecond']
        return (parsed['hour'], parsed['minute'], parsed['second'], microsecond)
    @staticmethod
    def tzinfo(parsed):
        """Return the timezone in `parsed`.

        If `parsed` does not contain a timezone specification, return None. If
        `parsed` contains a bad timezone specification, return False. Otherwise
        return a timezone object.
        """
        tzhour = parsed['tzhour']
        tzminute = parsed['tzminute']
        if tzhour is None:
            return None
        if (tzhour >= 24) or (tzminute >= 60):
            return False
        delta = (60 * tzhour) + tzminute
        if parsed['tzsign'] == '-':
            delta *= -1
        return timezone(timedelta(minutes=delta))

class Date(DateTime):
    """Semantic validation of `date`_ strings per `RFC 3339`_."""
    name = 'date'
    regexp = re.compile(r'^' + FULL_DATE + r'$')
    def test_parsed(self, parsed):
        (year, month, day) = self.date(parsed)
        try:
            date(year, month, day)
        except ValueError:
            return False
        else:
            return True

class Time(DateTime):
    """Semantic validation of `time`_ strings per `RFC 3339`_."""
    name = 'time'
    regexp = re.compile(r'^' + FULL_TIME + r'$')
    def test_parsed(self, parsed):
        (hour, minute, second, microsecond) = self.time(parsed)
        tzinfo = self.tzinfo(parsed)
        if tzinfo is False:
            return False
        try:
            time(hour, minute, second, microsecond, tzinfo)
        except (ValueError, OverflowError):
            return False
        else:
            return True
