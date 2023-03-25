### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for JSON Schema object additionalProperties"""

from urllib.parse import urlunsplit
from os.path import abspath

from unittest import TestCase

from rsk_mt.jsonschema.schema import RootSchema

from .test_object import Procedures

DEFAULT_URI = urlunsplit(('file', '', abspath(__file__), '', ''))

class TestAdditionalProperties(TestCase, Procedures):
    """Test JSON Schema object additionalProperties."""
    schema = """{
        "type": "object",
        "properties": {
            "foo": {
                "type": "string"
            }
        },
        "additionalProperties": {
            "type": "integer",
            "default": 0
        }
    }"""
    def __init__(self, *args):
        super().__init__(*args)
        root = RootSchema.loads(self.schema, DEFAULT_URI)
        self._value_type = root.get_schema('#')
    def test_accept(self):
        """Test JSON Schema object additionalProperties accepts value"""
        val = {'foo': 'bar', 'baz': 1}
        self.assertEqual(self._value_type(val), val)
    def test_reject(self):
        """Test JSON Schema object additionalProperties rejects value"""
        val = {'foo': 'bar', 'baz': 'bar'}
        self.assertRaises(TypeError, self._value_type, val)
    def test_getitem(self):
        """Test JSON Schema object additionalProperties getitem"""
        val = {'foo': 'bar', 'baz': 8}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        self.assertEqual(dct['foo'], 'bar')
        self.assertEqual(dct['baz'], 8)
        # __getitem__ uses additionalProperties default value
        self.assertEqual(dct['quux'], 0)
        self.assertEqual(dct['quuz'], 0)
        self.assertEqual(dct['corge'], 0)
    def test_setitem(self):
        """Test JSON Schema object additionalProperties setitem"""
        val = {'foo': 'bar'}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # __setitem__ rejects additionalProperties
        self.assertRaises(TypeError, self.proc_setitem, dct, 'baz', 'err', None)
        # __setitem__ accepts setting additionalProperties
        self.proc_setitem(dct, 'baz', 7, {'foo': 'bar', 'baz': 7})
        self.proc_setitem(dct, 'quux', -3, {'foo': 'bar', 'baz': 7, 'quux': -3})
        # __setitem__ accepts modifying additionalProperties
        self.proc_setitem(dct, 'baz', -4, {'foo': 'bar', 'baz': -4, 'quux': -3})
    def test_delitem(self):
        """Test JSON Schema object additionalProperties delitem"""
        val = {'foo': 'bar', 'baz': 9}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # __delitem__ deletes pair
        self.proc_delitem(dct, 'foo', {'baz': 9})
        # __delitem__ errors on missing key
        self.assertRaises(KeyError, self.proc_delitem, dct, 'foo', None)
        # __delitem__ deletes additionalProperties pair
        self.proc_delitem(dct, 'baz', {})
        # __delitem__ errors on missing additionalProperties key
        self.assertRaises(KeyError, self.proc_delitem, dct, 'baz', None)
    def test_clear(self):
        """Test JSON Schema object additionalProperties clear"""
        val = {'foo': 'bar', 'baz': 9}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # clear() clears all pairs including additionalProperties
        self.proc_clear(dct, {})
    def test_pop(self):
        """Test JSON Schema object additionalProperties pop"""
        val = {'foo': 'bar', 'baz': 9}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # pop() pops additionalProperties key
        self.proc_pop(dct, 'baz', 9, {'foo': 'bar'})
        # pop() errors on missing additionalProperties key
        self.assertRaises(KeyError, self.proc_pop, dct, 'quux', None, None)
    def test_popitem(self):
        """Test JSON Schema object additionalProperties popitem"""
        val = {'foo': 'bar', 'baz': 9}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # popitem() pops all pairs
        self.proc_popitem_all_pairs(dct)
    def test_update(self):
        """Test JSON Schema object additionalProperties update"""
        val = {'foo': 'bar'}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # update() updates additionalProperties
        other = {'baz': 2, 'quux': 4}
        after = {'foo': 'bar', 'baz': 2, 'quux': 4}
        self.proc_update(dct, other, after)
        # update() rejects additionalProperties
        other = {'thud': -1.4}
        self.assertRaises(TypeError, self.proc_update, dct, other, None)
