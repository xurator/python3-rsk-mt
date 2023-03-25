### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for JSON Schema encodings"""

from unittest import TestCase
from nose2.tools import params

from rsk_mt.jsonschema.encodings import Encoding

from ... import (
    make_fqname,
    make_params_values,
)

class TestEncoding(TestCase):
    """Tests for rsk_mt.jsonschema.encodings.Encoding."""
    def test_abstract(self):
        """Test rsk_mt.jsonschema.encodings.Encoding is abstract"""
        self.assertRaises(NotImplementedError, Encoding(), None)

class EncodingTestBuilder(type):
    """Build tests for rsk_mt.jsonschema.encodings.Encoding implementations.

    Specify this class as metaclass and provide:
    `constructor` - a callable returning an Encoding instance
    `name` - the string name of the Encoding
    `accept` - an iterable of string values this Encoding must accept
    `reject` - an iterable of string values this Encoding must reject
    `invalid` - an iterable of other values this Encoding must reject
    """
    invalid = (
        None,
        False, True,
        -1, 0, 1,
        -1.5, 0.0, 1.5,
        (), ('foo', 'bar', 'baz'),
        [], ['foo', 'bar', 'baz'],
        {}, {'foo': 'bar'},
    )
    def __new__(cls, name, bases, dct):
        constructor = dct['constructor']
        fqname = make_fqname(constructor)
        # build out class for testing `constructor`
        dct.update({
            'test_name': cls.make_test_name(
                constructor, fqname,
                dct['name'],
            ),
            'test_accept': cls.make_test_accept(
                constructor, fqname,
                make_params_values(dct['accept']),
            ),
            'test_reject': cls.make_test_reject(
                constructor, fqname,
                make_params_values(dct['reject']),
            ),
            'test_invalid': cls.make_test_invalid(
                constructor, fqname,
                make_params_values(dct.get('invalid', cls.invalid)),
            ),
        })
        return super().__new__(cls, name, bases, dct)
    # make functions for use as TestCase methods
    @staticmethod
    def make_test_name(constructor, fqname, name):
        """Make a function testing encoding name attribute."""
        def method(self):
            """Test encoding name attribute."""
            self.assertEqual(constructor.name, name)
            self.assertEqual(constructor().name, name)
        method.__doc__ = f'Test {fqname} name attribute'
        return method
    @staticmethod
    def make_test_accept(constructor, fqname, values):
        """Make a function testing encoding accepts `values`."""
        @params(*values)
        def method(self, value):
            """Test encoding accepts `value`."""
            encoding = constructor()
            self.assertEqual(encoding(value), True)
        method.__doc__ = f'Test {fqname} accepts value'
        return method
    @staticmethod
    def make_test_reject(constructor, fqname, values):
        """Make a function testing encoding rejects `values`."""
        @params(*values)
        def method(self, value):
            """Test encoding rejects `value`."""
            encoding = constructor()
            self.assertEqual(encoding(value), False)
        method.__doc__ = f'Test {fqname} rejects value'
        return method
    @staticmethod
    def make_test_invalid(constructor, fqname, values):
        """Make a function testing encoding rejects invalid `values`."""
        @params(*values)
        def method(self, value):
            """Test encoding rejects invalid `value`."""
            encoding = constructor()
            self.assertEqual(encoding(value), False)
        method.__doc__ = f'Test {fqname} rejects invalid `value`'
        return method
