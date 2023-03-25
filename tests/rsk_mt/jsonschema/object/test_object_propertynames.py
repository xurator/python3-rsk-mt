### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for JSON Schema object propertyNames"""

from urllib.parse import urlunsplit
from os.path import abspath

from unittest import TestCase

from rsk_mt.jsonschema.schema import RootSchema

from .test_object import Procedures

DEFAULT_URI = urlunsplit(('file', '', abspath(__file__), '', ''))

class TestPropertyNames(TestCase, Procedures):
    """Test JSON Schema object propertyNames."""
    schema = """{
        "type": "object",
        "additionalProperties": {
            "type": "integer"
        },
        "propertyNames": {
            "enum": ["foo", "bar"]
        }
    }"""
    def __init__(self, *args):
        super().__init__(*args)
        root = RootSchema.loads(self.schema, DEFAULT_URI)
        self._value_type = root.get_schema('#')
    def test_accept(self):
        """Test JSON Schema object propertyNames accepts value"""
        val = {'foo': 1, 'bar': 2}
        self.assertEqual(self._value_type(val), val)
    def test_reject(self):
        """Test JSON Schema object propertyNames rejects value"""
        val = {'bar': 'baz'}
        self.assertRaises(TypeError, self._value_type, val)
        val = {'quux': 1}
        self.assertRaises(ValueError, self._value_type, val)
    def test_setitem(self):
        """Test JSON Schema object propertyNames setitem"""
        val = {'foo': 1}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # __setitem__
        self.assertRaises(TypeError, self.proc_setitem, dct, 'bar', 'bad', None)
        # __setitem__
        self.assertRaises(KeyError, self.proc_setitem, dct, 'quux', 3, None)
        # __setitem__
        self.proc_setitem(dct, 'bar', 2, {'foo': 1, 'bar': 2})
        self.proc_setitem(dct, 'foo', -9, {'foo': -9, 'bar': 2})
    def test_update(self):
        """Test JSON Schema object propertyNames update"""
        val = {'foo': 1}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # update()
        self.proc_update(dct, {'bar': 2}, {'foo': 1, 'bar': 2})
        # update()
        other = {'foo': True}
        self.assertRaises(TypeError, self.proc_update, dct, other, None)
        # update()
        other = {'quux': 1}
        self.assertRaises(ValueError, self.proc_update, dct, other, None)
