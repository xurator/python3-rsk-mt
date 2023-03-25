### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema validator: number"""

from unittest import TestCase

from rsk_mt.jsonschema.validators import Number

from .test_validator import (
    ValidatorTestBuilder,
    MockRoot,
)

class TestNumber(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator number."""
    validation = Number
    spec = {}
    base_uri = 'test://number/'
    root = MockRoot(base_uri)
    accept = (
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
    )
    reject = (
        None,
        False, True,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )

class TestMultipleOf(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator number multipleOf."""
    validation = Number
    spec = {
        'multipleOf': 2,
    }
    base_uri = 'test://number/multipleOf/'
    root = MockRoot(base_uri)
    accept = (
        -2, 0, 2,
        -2.0, 0.0, 2.0,
    )
    reject = (
        None,
        False, True,
        -3, -1, 1, 3,
        -2.5, -1.5, -1.0, -0.5, 0.5, 1.0, 1.5, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )

class TestMaximum(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator number maximum."""
    validation = Number
    spec = {
        'maximum': 2,
    }
    base_uri = 'test://number/maximum/'
    root = MockRoot(base_uri)
    accept = (
        -3, -2, -1, 0, 1, 2,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0,
    )
    reject = (
        None,
        False, True,
        3,
        2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )

class TestExclusiveMaximum(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator number exclusiveMaximum."""
    validation = Number
    spec = {
        'exclusiveMaximum': 2,
    }
    base_uri = 'test://number/exclusiveMaximum/'
    root = MockRoot(base_uri)
    accept = (
        -3, -2, -1, 0, 1,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5,
    )
    reject = (
        None,
        False, True,
        2, 3,
        2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )

class TestMinimum(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator number minimum."""
    validation = Number
    spec = {
        'minimum': 2,
    }
    base_uri = 'test://number/minimum/'
    root = MockRoot(base_uri)
    accept = (
        2, 3,
        2.0, 2.5,
    )
    reject = (
        None,
        False, True,
        -3, -2, -1, 0, 1,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )

class TestExclusiveMinimum(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator number exclusiveMinimum."""
    validation = Number
    spec = {
        'exclusiveMinimum': 2,
    }
    base_uri = 'test://number/exclusiveMinimum/'
    root = MockRoot(base_uri)
    accept = (
        3,
        2.5,
    )
    reject = (
        None,
        False, True,
        -3, -2, -1, 0, 1, 2,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )

class TestCombined(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator number combined."""
    validation = Number
    spec = {
        'multipleOf': 0.5,
        'maximum': 2,
        'exclusiveMinimum': -2,
    }
    base_uri = 'test://number/combined/'
    root = MockRoot(base_uri)
    accept = (
        -1, 0, 1, 2,
        -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0,
    )
    reject = (
        None,
        False, True,
        -3, -2, 3,
        -2.5, -2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )
