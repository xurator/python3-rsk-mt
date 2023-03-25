### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for JSON Schema formats"""

from unittest import TestCase
from nose2.tools import params

from rsk_mt.jsonschema.formats import Format

from ... import (
    make_fqname,
    make_params_values,
)

PRIMITIVES = frozenset((
    'null',
    'boolean',
    'integer',
    'number',
    'string',
    'array',
    'object',
))

class TestFormat(TestCase):
    """Tests for rsk_mt.jsonschema.formats.Format."""
    def test_abstract(self):
        """Test rsk_mt.jsonschema.formats.Format is abstract"""
        self.assertRaises(NotImplementedError, Format().validates, None)
        self.assertRaises(NotImplementedError, Format(), None)

class FormatTestBuilder(type):
    """Build tests for rsk_mt.jsonschema.formats.Format implementations.

    Specify this class as metaclass and provide:
    `constructor` - a callable returning a Format instance
    `name` - the string name of the Format
    `validate` - an iterable of strings, the primitives this Format validates
    `accept` - an iterable of string values this Format must accept
    `reject` - an iterable of string values this Format must reject
    `invalid` - an iterable of other values this Format must reject
    """
    def __new__(cls, name, bases, dct):
        constructor = dct['constructor']
        fqname = make_fqname(constructor)
        # build out class for testing `constructor`
        dct.update({
            'test_name': cls.make_test_name(
                constructor, fqname,
                dct['name'],
            ),
            'test_validate': cls.make_test_validate(
                constructor, fqname,
                make_params_values(dct['validate']),
            ),
            'test_not_validate': cls.make_test_not_validate(
                constructor, fqname,
                make_params_values(PRIMITIVES - frozenset(dct['validate'])),
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
                make_params_values(dct['invalid']),
            ),
        })
        return super().__new__(cls, name, bases, dct)
    # make functions for use as TestCase methods
    @staticmethod
    def make_test_name(constructor, fqname, name):
        """Make a function testing format name attribute."""
        def method(self):
            """Test format name attribute."""
            self.assertEqual(constructor.name, name)
            self.assertEqual(constructor().name, name)
        method.__doc__ = f'Test {fqname} name attribute'
        return method
    @staticmethod
    def make_test_validate(constructor, fqname, primitives):
        """Make a function testing format validates `primitives`."""
        @params(*primitives)
        def method(self, primitive):
            """Test format validates `primitive`."""
            format_ = constructor()
            self.assertEqual(format_.validates(primitive), True)
        method.__doc__ = f'Test {fqname} validates primitive'
        return method
    @staticmethod
    def make_test_not_validate(constructor, fqname, primitives):
        """Make a function testing format does not validate `primitives`."""
        @params(*primitives)
        def method(self, primitive):
            """Test format does not validate `primitive`."""
            format_ = constructor()
            self.assertEqual(format_.validates(primitive), False)
        method.__doc__ = f'Test {fqname} does not validate primitive'
        return method
    @staticmethod
    def make_test_accept(constructor, fqname, values):
        """Make a function testing format accepts `values`."""
        @params(*values)
        def method(self, value):
            """Test format accepts `value`."""
            format_ = constructor()
            self.assertEqual(format_(value), True)
        method.__doc__ = f'Test {fqname} accepts value'
        return method
    @staticmethod
    def make_test_reject(constructor, fqname, values):
        """Make a function testing format rejects `values`."""
        @params(*values)
        def method(self, value):
            """Test format rejects `value`."""
            format_ = constructor()
            self.assertEqual(format_(value), False)
        method.__doc__ = f'Test {fqname} rejects value'
        return method
    @staticmethod
    def make_test_invalid(constructor, fqname, values):
        """Make a function testing format rejects invalid `values`."""
        @params(*values)
        def method(self, value):
            """Test format rejects invalid `value`."""
            format_ = constructor()
            self.assertEqual(format_(value), False)
        method.__doc__ = f'Test {fqname} rejects invalid `value`'
        return method
