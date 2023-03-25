### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for JSON Schema object maxProperties"""

from urllib.parse import urlunsplit
from os.path import abspath

from unittest import TestCase

from rsk_mt.jsonschema.schema import RootSchema

from .test_object import Procedures

DEFAULT_URI = urlunsplit(('file', '', abspath(__file__), '', ''))

class TestMaxProperties(TestCase, Procedures):
    """Test JSON Schema object maxProperties."""
    schema = """{
        "type": "object",
        "maxProperties": 2
    }"""
    def __init__(self, *args):
        super().__init__(*args)
        root = RootSchema.loads(self.schema, DEFAULT_URI)
        self._value_type = root.get_schema('#')
    def test_accept(self):
        """Test JSON Schema object maxProperties accepts value"""
        val = {'A': 1, 'B': 2}
        self.assertEqual(self._value_type(val), val)
    def test_reject(self):
        """Test JSON Schema object maxProperties rejects value"""
        val = {'A': 1, 'B': 2, 'C': 3}
        self.assertRaises(ValueError, self._value_type, val)
    def test_setitem(self):
        """Test JSON Schema object maxProperties setitem"""
        val = {'foo': 7}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # __setitem__ accepts new pair
        self.proc_setitem(dct, 'quux', True, {'foo': 7, 'quux': True})
        # __setitem__ accepts modify pair
        self.proc_setitem(dct, 'foo', -9, {'foo': -9, 'quux': True})
        # __setitem__ rejects new pair
        self.assertRaises(KeyError, self.proc_setitem, dct, 'bar', 3, None)
    def test_update(self):
        """Test JSON Schema object maxProperties update"""
        val = {'foo': 1}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # update() accepts new pair
        self.proc_update(dct, {'bar': 'string'}, {'foo': 1, 'bar': 'string'})
        # update() rejects new pair
        self.assertRaises(ValueError, self.proc_update, dct, {'baz': 3}, None)
