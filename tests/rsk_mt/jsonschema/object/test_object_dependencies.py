### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for JSON Schema object dependencies"""

from urllib.parse import urlunsplit
from os.path import abspath

from unittest import TestCase

from rsk_mt.jsonschema.schema import RootSchema

from .test_object import Procedures

DEFAULT_URI = urlunsplit(('file', '', abspath(__file__), '', ''))

class TestDependenciesInstance(TestCase, Procedures):
    """Test JSON Schema object dependencies on whole instance."""
    schema = """{
        "type": "object",
        "properties": {
            "foo": {
                "type": "number"
            }
        },
        "dependencies": {
            "bar": {
                "properties": {
                    "foo": {
                        "multipleOf": 2
                    }
                },
                "patternProperties": {
                    "^b.*": {
                        "type": "string"
                    }
                }
            }
        }
    }"""
    def __init__(self, *args):
        super().__init__(*args)
        root = RootSchema.loads(self.schema, DEFAULT_URI)
        self._value_type = root.get_schema('#')
    def test_accept(self):
        """Test JSON Schema object dependencies instance accepts value"""
        # dependencies not triggered
        val = {'foo': 7}
        self.assertEqual(self._value_type(val), val)
        # dependencies triggered
        val = {'foo': 8, 'bar': 'quux'}
        self.assertEqual(self._value_type(val), val)
    def test_reject(self):
        """Test JSON Schema object dependencies instance rejects value"""
        # dependencies not triggered
        val = {'foo': 8, 'bar': True}
        self.assertRaises(TypeError, self._value_type, val)
        # dependencies triggered
        val = {'foo': 7, 'bar': 'quux'}
        self.assertRaises(ValueError, self._value_type, val)
    def test_setitem(self):
        """Test JSON Schema object dependencies instance setitem"""
        val = {'foo': 7}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # __setitem__ rejects, dependencies triggered
        self.assertRaises(KeyError, self.proc_setitem, dct, 'bar', 'quux', None)
        # __setitem__ accepts, dependencies not triggered
        self.proc_setitem(dct, 'baz', 'quux', {'foo': 7, 'baz': 'quux'})
        # __setitem__ accepts change of dependency target pair
        self.proc_setitem(dct, 'foo', 8, {'foo': 8, 'baz': 'quux'})
        # __setitem__ accepts, dependencies triggered
        after = {'foo': 8, 'baz': 'quux', 'bar': 'thud'}
        self.proc_setitem(dct, 'bar', 'thud', after)
        # __setitem__ rejects change of dependency target pair
        self.assertRaises(KeyError, self.proc_setitem, dct, 'foo', 7, None)
        # __setitem__ accepts modification of dependency target pair
        after = {'foo': 10, 'baz': 'quux', 'bar': 'thud'}
        self.proc_setitem(dct, 'foo', 10, after)
    def test_delitem(self):
        """Test JSON Schema object dependencies instance setitem"""
        val = {'foo': 8, 'bar': 'quux', 'baz': 'thud'}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # __delitem__ deletes dependency target pair with active dependency
        self.proc_delitem(dct, 'baz', {'foo': 8, 'bar': 'quux'})
        # __delitem__ deletes dependency source pair
        self.proc_delitem(dct, 'bar', {'foo': 8})
        # __delitem__ deletes dependency target pair with no active dependency
        self.proc_delitem(dct, 'foo', {})
    def test_clear(self):
        """Test JSON Schema object dependencies instance clear"""
        val = {'foo': 8, 'bar': 'quux', 'baz': 'thud'}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # TODO: should be all pairs? dependency does not make mandatory
        # clear() clears no pairs
        self.proc_clear(dct, val)
    def test_pop(self):
        """Test JSON Schema object dependencies instance pop"""
        val = {'foo': 8, 'bar': 'quux', 'baz': 'thud'}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # pop() pops dependency target pair with active dependency
        self.proc_pop(dct, 'foo', 8, {'bar': 'quux', 'baz': 'thud'})
        # pop() pops dependency source pair
        self.proc_pop(dct, 'bar', 'quux', {'baz': 'thud'})
        # pop() pops dependency target pair with no active dependency
        self.proc_pop(dct, 'baz', 'thud', {})
    def test_popitem(self):
        """Test JSON Schema object dependencies instance popitem"""
        val = {'foo': 4, 'bar': 'quux', 'baz': 'thud'}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # TODO: should be all pairs? dependency does not make mandatory
        # popitem() pops no pairs
        self.proc_popitem_no_pairs(dct)
    def test_update(self):
        """Test JSON Schema object dependencies instance update"""
        val = {'foo': 1}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # update() rejects, dependencies triggered
        other = {'bar': 'quux'}
        self.assertRaises(ValueError, self.proc_update, dct, other, None)
        # update() accepts, dependencies triggered
        other = {'foo': 8, 'bar': 'quux'}
        self.proc_update(dct, other, other)
        # update() rejects, dependencies triggered
        other = {'foo': 7}
        self.assertRaises(ValueError, self.proc_update, dct, other, None)

class TestDependenciesPresence(TestCase, Procedures):
    """Test JSON Schema object dependencies on property presence."""
    schema = """{
        "type": "object",
        "properties": {
            "foo": {
                "type": "number"
            },
            "bar": {
                "type": "string"
            }
        },
        "dependencies": {
            "bar": ["foo"]
        }
    }"""
    def __init__(self, *args):
        super().__init__(*args)
        root = RootSchema.loads(self.schema, DEFAULT_URI)
        self._value_type = root.get_schema('#')
    def test_accept(self):
        """Test JSON Schema object dependencies presence accepts value"""
        # dependencies not triggered
        val = {'foo': 7}
        self.assertEqual(self._value_type(val), val)
        # dependencies not triggered
        val = {'foo': 8, 'bar': 'quux'}
        self.assertEqual(self._value_type(val), val)
    def test_reject(self):
        """Test JSON Schema object dependencies presence rejects value"""
        # dependencies not triggered
        val = {'foo': 8, 'bar': True}
        self.assertRaises(TypeError, self._value_type, val)
        # dependencies triggered
        val = {'bar': 'quux'}
        self.assertRaises(ValueError, self._value_type, val)
    def test_setitem(self):
        """Test JSON Schema object dependencies presence setitem"""
        val = {}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # __setitem__ rejects, dependencies triggered
        self.assertRaises(KeyError, self.proc_setitem, dct, 'bar', 'quux', None)
        # __setitem__ accepts, dependencies not triggered
        self.proc_setitem(dct, 'foo', 8, {'foo': 8})
        self.proc_setitem(dct, 'foo', 10, {'foo': 10})
        # __setitem__ accepts, dependencies triggered
        self.proc_setitem(dct, 'bar', 'quux', {'foo': 10, 'bar': 'quux'})
        # __setitem__ rejects, dependencies triggered
        self.assertRaises(TypeError, self.proc_setitem, dct, 'foo', 'baz', None)
        # __setitem__ accepts, dependencies triggered
        self.proc_setitem(dct, 'foo', 3, {'foo': 3, 'bar': 'quux'})
    def test_delitem(self):
        """Test JSON Schema object dependencies presence delitem"""
        val = {'foo': 8, 'bar': 'quux', 'baz': 'thud'}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # __delitem__ deletes independent pair
        self.proc_delitem(dct, 'baz', {'foo': 8, 'bar': 'quux'})
        # __delitem__ deletes dependency source pair
        self.proc_delitem(dct, 'bar', {'foo': 8})
        # __delitem__ deletes dependency target pair with no active dependency
        self.proc_delitem(dct, 'foo', {})
    def test_clear(self):
        """Test JSON Schema object dependencies presence clear"""
        val = {'foo': 8, 'bar': 'quux', 'baz': 'thud'}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # TODO: should be all pairs? dependency does not make mandatory
        # clear() clears no pairs
        self.proc_clear(dct, val)
    def test_pop(self):
        """Test JSON Schema object dependencies presence pop"""
        val = {'foo': 8, 'bar': 'quux'}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # pop() rejects pop dependency target pair with active dependency
        self.assertRaises(KeyError, self.proc_pop, dct, 'foo', None, None)
        # pop() pops dependency source pair
        self.proc_pop(dct, 'bar', 'quux', {'foo': 8})
        # pop() pops dependency target pair with no active dependency
        self.proc_pop(dct, 'foo', 8, {})
    def test_popitem(self):
        """Test JSON Schema object dependencies presence popitem"""
        val = {'foo': 4, 'bar': 'quux', 'baz': 'thud'}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # TODO: should be all pairs? dependency does not make mandatory
        # popitem() pops no pairs
        self.proc_popitem_no_pairs(dct)
    def test_update(self):
        """Test JSON Schema object dependencies presence update"""
        val = {}
        dct = self._value_type(val)
        self.assertEqual(dct, val)
        # update() rejects, dependencies triggered
        other = {'bar': 'quux'}
        self.assertRaises(ValueError, self.proc_update, dct, other, None)
        # update() accepts, dependencies triggered
        other = {'foo': 8, 'bar': 'quux'}
        self.proc_update(dct, other, other)
        # update() rejects, dependencies triggered
        other = {'foo': 'bar'}
        self.assertRaises(TypeError, self.proc_update, dct, other, None)
