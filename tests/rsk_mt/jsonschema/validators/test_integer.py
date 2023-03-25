### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema validator: integer"""

from unittest import TestCase

from rsk_mt.jsonschema.validators import Integer

from .test_validator import (
    ValidatorTestBuilder,
    MockRoot,
)

class TestInteger(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator integer."""
    validation = Integer
    spec = {}
    base_uri = 'test://integer/'
    root = MockRoot(base_uri)
    accept = (
        -3, -2, -1, 0, 1, 2, 3,
    )
    reject = (
        None,
        False, True,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )

class TestMultipleOf(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator integer multipleOf."""
    validation = Integer
    spec = {
        'multipleOf': 2,
    }
    base_uri = 'test://integer/multipleOf/'
    root = MockRoot(base_uri)
    accept = (
        -2, 0, 2,
    )
    reject = (
        None,
        False, True,
        -3, -1, 1, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )

class TestMaximum(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator integer maximum."""
    validation = Integer
    spec = {
        'maximum': 2,
    }
    base_uri = 'test://integer/maximum/'
    root = MockRoot(base_uri)
    accept = (
        -3, -2, -1, 0, 1, 2,
    )
    reject = (
        None,
        False, True,
        3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )

class TestExclusiveMaximum(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator integer exclusiveMaximum."""
    validation = Integer
    spec = {
        'exclusiveMaximum': 2,
    }
    base_uri = 'test://integer/exclusiveMaximum/'
    root = MockRoot(base_uri)
    accept = (
        -3, -2, -1, 0, 1,
    )
    reject = (
        None,
        False, True,
        2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )

class TestMinimum(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator integer minimum."""
    validation = Integer
    spec = {
        'minimum': 2,
    }
    base_uri = 'test://integer/minimum/'
    root = MockRoot(base_uri)
    accept = (
        2, 3,
    )
    reject = (
        None,
        False, True,
        -3, -2, -1, 0, 1,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )

class TestExclusiveMinimum(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator integer exclusiveMinimum."""
    validation = Integer
    spec = {
        'exclusiveMinimum': 2,
    }
    base_uri = 'test://integer/exclusiveMinimum/'
    root = MockRoot(base_uri)
    accept = (
        3,
    )
    reject = (
        None,
        False, True,
        -3, -2, -1, 0, 1, 2,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )

class TestCombined(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator integer combined."""
    validation = Integer
    spec = {
        'multipleOf': 0.5,
        'maximum': 2,
        'exclusiveMinimum': -2,
    }
    base_uri = 'test://integer/combined/'
    root = MockRoot(base_uri)
    accept = (
        -1, 0, 1, 2,
    )
    reject = (
        None,
        False, True,
        -3, -2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )
