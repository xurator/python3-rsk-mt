### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema validator: string"""

from unittest import TestCase

from rsk_mt.enforce.constraint import Pattern
from rsk_mt.jsonschema.validators import String

from .test_validator import (
    ValidatorTestBuilder,
    MockRoot,
)

class Foo(Pattern): # pylint: disable=too-few-public-methods
    """A duck-typed custom application format for 'foo' strings."""
    name = 'foo'
    def __init__(self):
        Pattern.__init__(self, 'foo')
    @staticmethod
    def validates(primitive):
        """Return True is `primitive` is 'string'."""
        return primitive == 'string'

class TestString(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator string."""
    validation = String
    spec = {}
    base_uri = 'test://string/'
    root = MockRoot(base_uri)
    accept = (
        "", "foo", "foobar",
    )
    reject = (
        None,
        False, True,
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        (), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )

class TestMaxLength(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator string maxLength."""
    validation = String
    spec = {
        'maxLength': 5,
    }
    base_uri = 'test://string/maxLength/'
    root = MockRoot(base_uri)
    accept = (
        "", "foo",
    )
    reject = (
        None,
        False, True,
        "foobar",
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        (), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )

class TestMinLength(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator string minLength."""
    validation = String
    spec = {
        'minLength': 5,
    }
    base_uri = 'test://string/minLength/'
    root = MockRoot(base_uri)
    accept = (
        "foobar",
    )
    reject = (
        None,
        False, True,
        "", "foo",
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        (), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )

class TestPattern(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator string pattern."""
    validation = String
    spec = {
        'pattern': 'oob',
    }
    base_uri = 'test://string/pattern/'
    root = MockRoot(base_uri)
    accept = (
        "foobar",
    )
    reject = (
        None,
        False, True,
        "", "foo",
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        (), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )

class TestFormatIgnored(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator string format ignored."""
    validation = String
    spec = {
        'format': 'bad',
    }
    base_uri = 'test://string/format/ignored/'
    root = MockRoot(base_uri)
    accept = (
        "", "foo", "foobar",
    )
    reject = (
        None,
        False, True,
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        (), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )

class TestFormat(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator string format."""
    validation = String
    spec = {
        'format': 'foo',
    }
    base_uri = 'test://string/format/'
    root = MockRoot(base_uri, formats={'foo': Foo()})
    accept = (
        "foo", "foobar",
    )
    reject = (
        None,
        False, True,
        "",
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        (), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )

class TestCombined(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator string combined."""
    validation = String
    spec = {
        'maxLength': 10,
        'minLength': 1,
        'pattern': 'bar',
        'format': 'foo',
    }
    base_uri = 'test://string/combined/'
    root = MockRoot(base_uri, formats={'foo': Foo()})
    accept = (
        "foobar",
    )
    reject = (
        None,
        False, True,
        "", "foo",
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        (), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )
