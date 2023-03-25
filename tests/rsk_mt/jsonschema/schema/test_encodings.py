### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for JSON Schema encodings"""

import json
from os.path import abspath
from urllib.parse import urlunsplit

from base64 import b64encode

from unittest import TestCase
from nose2.tools import params

from rsk_mt.enforce.constraint import Pattern

from rsk_mt.jsonschema.schema import (
    RootSchema,
    Support,
)

DEFAULT_URI = urlunsplit(('file', '', abspath(__file__), '', ''))

# https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-8

class TestBuiltInEncodings(TestCase):
    """Test JSON Schema built-in encodings."""
    def __init__(self, *args):
        super().__init__(*args)
        self._schema = """{
            "allOf": [
                {"type": "string"},
                {"contentEncoding": "base64"}
            ]
        }"""
        self._string = 'foobar'
        self._json_string = json.dumps(self._string)
        self._encoded = b64encode(self._string.encode()).decode()
        self._json_encoded = json.dumps(self._encoded)
    def test_enabled(self):
        """Test JSON Schema built-in encodings are enabled by default"""
        root = RootSchema.loads(self._schema, DEFAULT_URI)
        self.assertEqual(root.binary, False)
        self.assertEqual(root(''), '')
        self.assertRaises(ValueError, root, self._string)
        self.assertEqual(root(self._encoded), self._encoded)
        self.assertEqual(root.decode(self._json_encoded), self._encoded)
        self.assertEqual(root.encode(self._encoded), self._json_encoded)
    def test_disabled(self):
        """Test JSON Schema built-in encodings can be disabled"""
        encodings = {'base64': None}
        support = Support(encodings=encodings)
        root = RootSchema.loads(self._schema, DEFAULT_URI, support=support)
        self.assertEqual(root.binary, False)
        self.assertEqual(root(''), '')
        self.assertEqual(root(self._string), self._string)
        self.assertEqual(root.decode(self._json_string), self._string)
        self.assertEqual(root.encode(self._string), self._json_string)
        self.assertEqual(root(self._encoded), self._encoded)
        self.assertEqual(root.decode(self._json_encoded), self._encoded)
        self.assertEqual(root.encode(self._encoded), self._json_encoded)

# Test custom encodings support

class Hexadecimal(Pattern): # pylint: disable=too-few-public-methods
    """A duck-typed custom encoding for hexadecimal strings."""
    def __init__(self):
        Pattern.__init__(self, '^[0-9A-F]*$')
    def __call__(self, val):
        valid = super().__call__(val)
        if valid:
            valid = ((len(val) % 2) == 0)
        return valid

class TestCustomEncoding(TestCase):
    """Test JSON Schema custom encoding."""
    def __init__(self, *args):
        super().__init__(*args)
        self._schema = json.dumps({
            'type': 'string',
            'contentEncoding': 'hexadecimal',
        })
        self._encodings = {
            'hexadecimal': Hexadecimal(),
        }
    @params(
        'null',
        'false',
        'true',
        '7',
        '-0.3',
        '["AB", "CD"]',
        '{"EF": "01"}',
    )
    def test_reject_type(self, string):
        """Test JSON Schema custom encoding does not affect type check"""
        support = Support(encodings=self._encodings)
        root = RootSchema.loads(self._schema, DEFAULT_URI, support=support)
        self.assertEqual(root.binary, False)
        self.assertRaises(TypeError, root.decode, string)
    @params(
        '"foo"',
        '"A"',
        '"ABC"',
        '"ZZ"',
    )
    def test_reject_value(self, string):
        """Test JSON Schema custom encoding rejects value"""
        support = Support(encodings=self._encodings)
        root = RootSchema.loads(self._schema, DEFAULT_URI, support=support)
        self.assertEqual(root.binary, False)
        self.assertRaises(ValueError, root.decode, string)
    @params(
        '""',
        '"01"',
        '"AB"',
        '"0123456789ABCDEF"',
    )
    def test_accept(self, string):
        """Test JSON Schema custom encoding accepts value"""
        support = Support(encodings=self._encodings)
        root = RootSchema.loads(self._schema, DEFAULT_URI, support=support)
        self.assertEqual(root.binary, False)
        self.assertEqual(json.dumps(root.decode(string)), string)
        self.assertEqual(root.encode(json.loads(string)), string)
    @params(
        '"foo"',
        '"A"',
        '"ABC"',
        '"ZZ"',
        '""',
        '"01"',
        '"AB"',
        '"0123456789ABCDEF"',
    )
    def test_ignore(self, string):
        """Test JSON Schema custom encoding is ignored if no support"""
        root = RootSchema.loads(self._schema, DEFAULT_URI)
        self.assertEqual(root.binary, False)
        self.assertEqual(json.dumps(root.decode(string)), string)
        self.assertEqual(root.encode(json.loads(string)), string)
