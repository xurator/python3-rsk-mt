### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for JSON Schema object required"""

from urllib.parse import urlunsplit
from os.path import abspath

from unittest import TestCase

from rsk_mt.jsonschema.schema import RootSchema

from .test_object import Procedures

DEFAULT_URI = urlunsplit(('file', '', abspath(__file__), '', ''))

class TestRequired(TestCase, Procedures):
    """Test JSON Schema object required."""
    schema = """{
        "type": "object",
        "required": ["foo", "baz"]
    }"""
    def __init__(self, *args):
        super().__init__(*args)
        root = RootSchema.loads(self.schema, DEFAULT_URI)
        self._value_type = root.get_schema('#')
    def test_accept(self):
        """Test JSON Schema object required accepts value"""
        val = {'foo': True, 'baz': False}
        self.assertEqual(self._value_type(val), val)
    def test_reject(self):
        """Test JSON Schema object required rejects value"""
        val = {'foo': 'A', 'bar': 3}
        self.assertRaises(ValueError, self._value_type, val)
    def test_delitem(self):
        """Test JSON Schema object required delitem"""
        val = {'foo': True, 'bar': False, 'baz': 'string'}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # __delitem__
        self.proc_delitem(dct, 'bar', {'foo': True, 'baz': 'string'})
        # __delitem__
        self.assertRaises(KeyError, self.proc_delitem, dct, 'foo', None)
    def test_clear(self):
        """Test JSON Schema object required clear"""
        val = {'foo': True, 'bar': False, 'baz': 'string'}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # clear() clears all unrequired pairs
        self.proc_clear(dct, {'foo': True, 'baz': 'string'})
    def test_pop(self):
        """Test JSON Schema object required pop"""
        val = {'foo': True, 'bar': False, 'baz': 's'}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # pop()
        self.proc_pop(dct, 'bar', False, {'foo': True, 'baz': 's'})
        # pop()
        self.assertRaises(KeyError, dct.pop, 'foo')
    def test_popitem(self):
        """Test JSON Schema object required popitem"""
        val = {'foo': True, 'bar': False, 'baz': 's'}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # popitem()
        popped = {}
        while True:
            try:
                (key, val) = dct.popitem()
            except KeyError:
                break
            else:
                popped[key] = val
        self.assertEqual(popped, {'bar': False})
        self.assertEqual(dct, {'foo': True, 'baz': 's'})
