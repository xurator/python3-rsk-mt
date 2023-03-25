### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for JSON Schema application base classes"""

from os.path import abspath
from urllib.parse import urlunsplit

from unittest import TestCase

from rsk_mt.jsonschema.schema import (
    RootSchema,
    Support,
)

DEFAULT_URI = urlunsplit(('file', '', abspath(__file__), '', ''))

# Test application bases support

class BaseMath():
    """Application base: some math support."""
    @property
    def total(self):
        """Return the numeric sum of all items in this tuple."""
        return sum(self)
    def power_up(self, power):
        """Return a new tuple, with each item in self raised to `power`."""
        # pylint: disable=not-an-iterable
        return self.__class__(_ ** power for _ in self)

class BaseMagic():
    """Application base: mutable manipulation."""
    # pylint: disable=unsubscriptable-object
    # pylint: disable=unsupported-assignment-operation
    # pylint: disable=unsupported-delete-operation
    def __init__(self):
        # create a new pair from specified key and val (or default val)
        self[self['key']] = self['val']
    @property
    def magic(self):
        """Return the value of the magic pair."""
        return self[self['key']]
    def scrub(self):
        """Delete magic pair."""
        del self[self['key']]

class TestBases(TestCase):
    """Test JSON Schema application bases."""
    # pylint: disable=no-member
    def __init__(self, *args):
        super().__init__(*args)
        # "SHOULD be number, but isn't": this is not illegal in JSON Schema
        schema = """{
            "$id": "http://example.com/bases.json",
            "oneOf": [{
                "$ref": "#number-list"
            }, {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string"
                    },
                    "val": {
                        "type": "number",
                        "default": "SHOULD be number, but isn't"
                    }
                },
                "required": ["key"]
            }],
            "definitions": {
                "number-list": {
                    "$id": "#number-list",
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                }
            }
        }"""
        support = Support(bases={
            # application bases for a specialised tuple
            'http://example.com/bases.json#number-list': (BaseMath,),
            # application bases for a specialised dict
            'http://example.com/bases.json#/oneOf/1': (BaseMagic,),
        })
        self._root = RootSchema.loads(schema, DEFAULT_URI, support=support)
    def test_tuple_property(self):
        """Test JSON Schema application bases tuple property"""
        val = [-2, -1.5, 0, 10.6]
        obj = self._root(val)
        self.assertIsInstance(obj, tuple)
        self.assertIsInstance(obj, BaseMath)
        self.assertEqual(list(obj), val)
        self.assertEqual(obj.total, 7.1)
    def test_tuple_method(self):
        """Test JSON Schema application bases tuple method"""
        val = (1, -2, 3)
        obj = self._root(val)
        self.assertIsInstance(obj, tuple)
        self.assertIsInstance(obj, BaseMath)
        self.assertEqual(obj, val)
        self.assertEqual(obj.power_up(3), (1, -8, 27))
        self.assertEqual(obj.power_up(3).power_up(3), (1, -512, 19683))
    def test_dict_init(self):
        """Test JSON Schema application bases dict __init__"""
        # only provide 'key'
        # we expect __init__ to magically set Schema default at key
        val = {'key': 'foo'}
        dct = self._root(val)
        self.assertIsInstance(dct, dict)
        self.assertIsInstance(dct, BaseMagic)
        self.assertEqual(dct, {
            'key': 'foo',
            'foo': "SHOULD be number, but isn't",
        })
        # provide 'key' and 'val'
        # we expect __init__ to magically set supplied val at key
        val = {'key': 'bar', 'val': 69}
        dct = self._root(val)
        self.assertIsInstance(dct, dict)
        self.assertIsInstance(dct, BaseMagic)
        self.assertEqual(dct, {
            'key': 'bar',
            'val': 69,
            'bar': 69,
        })
    def test_dict_property(self):
        """Test JSON Schema application bases dict property"""
        val = {'key': 'baz', 'val': -7.123}
        dct = self._root(val)
        self.assertIsInstance(dct, dict)
        self.assertIsInstance(dct, BaseMagic)
        self.assertEqual(dct, {
            'key': 'baz',
            'val': -7.123,
            'baz': -7.123,
        })
        self.assertEqual(dct.magic, -7.123)
    def test_dict_method(self):
        """Test JSON Schema application bases dict method"""
        val = {'key': 'baz', 'val': -7.123}
        dct = self._root(val)
        self.assertIsInstance(dct, dict)
        self.assertIsInstance(dct, BaseMagic)
        self.assertEqual(dct, {
            'key': 'baz',
            'val': -7.123,
            'baz': -7.123,
        })
        dct.scrub()
        self.assertEqual(dct, {
            'key': 'baz',
            'val': -7.123,
        })
        self.assertEqual(dct.get('baz', 'deleted'), 'deleted')
