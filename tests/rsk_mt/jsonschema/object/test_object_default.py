### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for JSON Schema object default values"""

from urllib.parse import urlunsplit
from os.path import abspath

from unittest import TestCase

from rsk_mt.jsonschema.schema import RootSchema

DEFAULT_URI = urlunsplit(('file', '', abspath(__file__), '', ''))

class TestDefaultValues(TestCase):
    """Test JSON Schema object default values."""
    schema = """{
        "type": "object",
        "properties": {
            "bar": {
                "default": 1
            }
        },
        "patternProperties": {
            "^b": {
                "default": 2
            },
            "^ba": {
                "default": 3
            }
        },
        "additionalProperties": {
            "default": 4
        }
    }"""
    def __init__(self, *args):
        super().__init__(*args)
        root = RootSchema.loads(self.schema, DEFAULT_URI)
        self._value_type = root.get_schema('#')
    def test_getitem_properties(self):
        """Test JSON Schema object properties default getitem"""
        val = {}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        self.assertEqual(dct['bar'], 1)
        self.assertEqual(dct.get('bar'), None)
    def test_getitem_patternProperties(self): # pylint: disable=invalid-name
        """Test JSON Schema object patternProperties default getitem"""
        val = {}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # patternProperties key matches one default
        self.assertEqual(dct['boo'], 2)
        self.assertEqual(dct.get('boo'), None)
        # patternProperties key matches multiple defaults
        self.assertRaises(KeyError, lambda d, k: d[k], dct, 'baz')
    def test_getitem_additionalProperties(self): # pylint: disable=invalid-name
        """Test JSON Schema object additionalProperties default getitem"""
        val = {}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        self.assertEqual(dct['foo'], 4)
        self.assertEqual(dct.get('foo'), None)
