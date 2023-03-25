### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for JSON Schema object patternProperties"""

from urllib.parse import urlunsplit
from os.path import abspath

from unittest import TestCase

from rsk_mt.jsonschema.schema import RootSchema

from .test_object import Procedures

DEFAULT_URI = urlunsplit(('file', '', abspath(__file__), '', ''))

class TestPatternProperties(TestCase, Procedures):
    """Test JSON Schema object patternProperties."""
    schema = """{
        "type": "object",
        "patternProperties": {
            "^x-.*": {
                "type": "string",
                "default": "baz"
            },
            "^y-.*": {
                "type": "boolean"
            }
        }
    }"""
    def __init__(self, *args):
        super().__init__(*args)
        root = RootSchema.loads(self.schema, DEFAULT_URI)
        self._value_type = root.get_schema('#')
    def test_accept(self):
        """Test JSON Schema object patternProperties accepts value"""
        val = {'x-foo': 'bar', 'y-baz': True}
        self.assertEqual(self._value_type(val), val)
    def test_reject(self):
        """Test JSON Schema object patternProperties rejects value"""
        val = {'x-foo': 9, 'y-baz': True}
        self.assertRaises(TypeError, self._value_type, val)
    def test_getitem(self):
        """Test JSON Schema object patternProperties getitem"""
        val = {'foo': 7, 'x-foo': 'bar'}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        self.assertEqual(dct['foo'], 7)
        self.assertEqual(dct['x-foo'], 'bar')
        # __getitem__ uses patternProperties default value
        self.assertEqual(dct['x-missing'], 'baz')
        # __getitem__ rejects missing patternProperties with no default
        self.assertRaises(KeyError, lambda d, k: d[k], dct, 'y-quux')
        # __getitem__ rejects missing pair
        self.assertRaises(KeyError, lambda d, k: d[k], dct, 'thud')
    def test_setitem(self):
        """Test JSON Schema object patternProperties setitem"""
        val = {'foo': -9, 'x-foo': 'bar'}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # __setitem__ rejects patternProperties
        self.assertRaises(TypeError, self.proc_setitem, dct, 'x-foo', 1, None)
        # __setitem__ accepts setting patternProperties
        after = {'foo': -9, 'x-foo': 'bar', 'y-quux': True}
        self.proc_setitem(dct, 'y-quux', True, after)
        # __setitem__ accepts modifying patternProperties
        after = {'foo': -9, 'x-foo': 'mod', 'y-quux': True}
        self.proc_setitem(dct, 'x-foo', 'mod', after)
        # __setitem__ accepts setting other property
        after = {'foo': -9, 'x-foo': 'mod', 'y-quux': True, 'thud': ['a', 'b']}
        self.proc_setitem(dct, 'thud', ['a', 'b'], after)
        # __setitem__ accepts modifying other property
        after = {'foo': -9, 'x-foo': 'mod', 'y-quux': True, 'thud': ['changed']}
        self.proc_setitem(dct, 'thud', ['changed'], after)
    def test_delitem(self):
        """Test JSON Schema object patternProperties delitem"""
        val = {'foo': -9, 'x-foo': 'bar', 'y-quux': False}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # __delitem__ deletes patternProperties
        self.proc_delitem(dct, 'x-foo', {'foo': -9, 'y-quux': False})
        # __delitem__ errors on missing patternProperties key
        self.assertRaises(KeyError, self.proc_delitem, dct, 'x-foo', None)
        # __delitem__ deletes other properties
        self.proc_delitem(dct, 'foo', {'y-quux': False})
        # __delitem__ errors on missing other properties
        self.assertRaises(KeyError, self.proc_delitem, dct, 'foo', None)
    def test_clear(self):
        """Test JSON Schema object patternProperties clear"""
        val = {'foo': -9, 'x-foo': 'bar', 'y-quux': False}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # clear() clears all pairs including patternProperties
        self.proc_clear(dct, {})
    def test_pop(self):
        """Test JSON Schema object patternProperties pop"""
        val = {'foo': -9, 'x-foo': 'bar', 'y-quux': False}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # pop() pops other property
        self.proc_pop(dct, 'foo', -9, {'x-foo': 'bar', 'y-quux': False})
        # pop() pops patternProperties
        self.proc_pop(dct, 'x-foo', 'bar', {'y-quux': False})
        # pop() errors on missing property
        self.assertRaises(KeyError, dct.pop, 'quux')
        # pop() errors on missing patternProperties
        self.assertRaises(KeyError, dct.pop, 'y-foo')
    def test_popitem(self):
        """Test JSON Schema object patternProperties popitem"""
        val = {'foo': 3, 'x-foo': 'bar', 'y-quux': False}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # popitem() pops all pairs
        self.proc_popitem_all_pairs(dct)
    def test_update(self):
        """Test JSON Schema object patternProperties update"""
        val = {'x-foo': 'bar'}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # update() accepts patternProperties
        other = {'x-quux': 'bar', 'foo': ['any']}
        after = {'foo': ['any'], 'x-foo': 'bar', 'x-quux': 'bar'}
        self.proc_update(dct, other, after)
        # update() rejects patternProperties
        self.assertRaises(TypeError, self.proc_update, dct, {'x-q': 0}, None)
