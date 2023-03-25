### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for JSON Schema object minProperties"""

from urllib.parse import urlunsplit
from os.path import abspath

from unittest import TestCase

from rsk_mt.jsonschema.schema import RootSchema

from .test_object import Procedures

DEFAULT_URI = urlunsplit(('file', '', abspath(__file__), '', ''))

class TestMinProperties(TestCase, Procedures):
    """Test JSON Schema object minProperties."""
    schema = """{
        "type": "object",
        "minProperties": 2
    }"""
    def __init__(self, *args):
        super().__init__(*args)
        root = RootSchema.loads(self.schema, DEFAULT_URI)
        self._value_type = root.get_schema('#')
    def test_accept(self):
        """Test JSON Schema object minProperties accepts value"""
        val = {'A': 1, 'B': 2}
        self.assertEqual(self._value_type(val), val)
    def test_reject(self):
        """Test JSON Schema object minProperties rejects value"""
        val = {'A': 1}
        self.assertRaises(ValueError, self._value_type, val)
    def test_delitem(self):
        """Test JSON Schema object minProperties delitem"""
        val = {'A': 3, 'B': 2, 'C': 1}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # __delitem__ deletes pair
        self.proc_delitem(dct, 'B', {'A': 3, 'C': 1})
        # __delitem__ rejects delete pair
        self.assertRaises(KeyError, self.proc_delitem, dct, 'B', None)
    def test_clear(self):
        """Test JSON Schema object minProperties clear"""
        val = {'A': 1, 'B': 2, 'C': 3}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # clear() clears no pairs
        self.proc_clear(dct, {'A': 1, 'B': 2, 'C': 3})
    def test_pop(self):
        """Test JSON Schema object minProperties pop"""
        val = {'A': 3, 'B': 2, 'C': 1}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # pop() pops free key
        self.proc_pop(dct, 'C', 1, {'A': 3, 'B': 2})
        # pop() rejects pop
        self.assertRaises(KeyError, dct.pop, 'A')
    def test_popitem(self):
        """Test JSON Schema object minProperties popitem"""
        val = {'A': 1, 'B': 2, 'C': 3}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # popitem() pops no pairs
        self.proc_popitem_no_pairs(dct)
