### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for JSON Schema object properties"""

from urllib.parse import urlunsplit
from os.path import abspath

from unittest import TestCase

from rsk_mt.jsonschema.schema import RootSchema

from .test_object import Procedures

DEFAULT_URI = urlunsplit(('file', '', abspath(__file__), '', ''))

class TestProperties(TestCase, Procedures):
    """Test JSON Schema object properties."""
    schema = """{
        "type": "object",
        "properties": {
            "foo": {
                "type": "number"
            },
            "bar": {
                "type": "string",
                "default": "baz"
            },
            "quux": {
                "type": "boolean"
            }
        }
    }"""
    def __init__(self, *args):
        super().__init__(*args)
        root = RootSchema.loads(self.schema, DEFAULT_URI)
        self._value_type = root.get_schema('#')
    def test_accept(self):
        """Test JSON Schema object properties accepts value"""
        val = {'foo': 7, 'quux': False}
        self.assertEqual(self._value_type(val), val)
    def test_reject(self):
        """Test JSON Schema object properties rejects value"""
        val = {'foo': 'bar'}
        self.assertRaises(TypeError, self._value_type, val)
    def test_getitem(self):
        """Test JSON Schema object properties getitem"""
        val = {'foo': 7}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        self.assertEqual(dct['foo'], 7)
        # __getitem__ uses properties default value
        self.assertEqual(dct['bar'], 'baz')
        # __getitem__ rejects keys with no value and no default
        self.assertRaises(KeyError, lambda d, k: d[k], dct, 'quux')
        self.assertRaises(KeyError, lambda d, k: d[k], dct, 'thud')
    def test_setitem(self):
        """Test JSON Schema object properties setitem"""
        val = {'foo': 7}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # __setitem__ rejects value
        self.assertRaises(TypeError, self.proc_setitem, dct, 'foo', 'bad', None)
        # __setitem__ accepts value
        self.proc_setitem(dct, 'quux', True, {'foo': 7, 'quux': True})
        # __setitem__ modifies value
        self.proc_setitem(dct, 'foo', -9, {'foo': -9, 'quux': True})
        # __setitem__ sets additional value
        after = {'foo': -9, 'quux': True, 'thud': {'any': 'thing'}}
        self.proc_setitem(dct, 'thud', {'any': 'thing'}, after)
        # __setitem__ modifies additional value
        after = {'foo': -9, 'quux': True, 'thud': ['modified']}
        self.proc_setitem(dct, 'thud', ['modified'], after)
    def test_delitem(self):
        """Test JSON Schema object properties delitem"""
        val = {'foo': -9, 'quux': False, 'thud': [1, 2, 3]}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # __delitem__
        self.proc_delitem(dct, 'quux', {'foo': -9, 'thud': [1, 2, 3]})
        # __delitem__
        self.assertRaises(KeyError, self.proc_delitem, dct, 'quux', None)
        # __delitem__
        self.proc_delitem(dct, 'thud', {'foo': -9})
        # __delitem__
        self.assertRaises(KeyError, self.proc_delitem, dct, 'thud', None)
    def test_clear(self):
        """Test JSON Schema object properties clear"""
        val = {'foo': 3, 'bar': 'ABC', 'quux': True, 'thud': None}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # clear() clears all pairs
        self.proc_clear(dct, {})
    def test_pop(self):
        """Test JSON Schema object properties pop"""
        val = {'foo': 3, 'bar': 'ABC', 'thud': None}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # pop()
        self.proc_pop(dct, 'foo', 3, {'bar': 'ABC', 'thud': None})
        # pop()
        self.assertRaises(KeyError, dct.pop, 'quux')
    def test_popitem(self):
        """Test JSON Schema object properties popitem"""
        val = {'foo': 3, 'quux': False}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # popitem()
        self.proc_popitem_all_pairs(dct)
    def test_update(self):
        """Test JSON Schema object properties update"""
        val = {'foo': 1}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # update()
        self.proc_update(dct, {'bar': 'string'}, {'foo': 1, 'bar': 'string'})
        # update()
        other = {'bar': False}
        self.assertRaises(TypeError, self.proc_update, dct, other, None)
