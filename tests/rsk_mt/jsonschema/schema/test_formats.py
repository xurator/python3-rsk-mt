### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for JSON Schema formats"""

import json
from os.path import abspath
from urllib.parse import urlunsplit

from unittest import TestCase
from nose2.tools import params

from rsk_mt.enforce.constraint import Pattern

from rsk_mt.jsonschema.schema import (
    RootSchema,
    Support,
)

DEFAULT_URI = urlunsplit(('file', '', abspath(__file__), '', ''))

# https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-7

class TestBuiltInFormats(TestCase):
    """Test JSON Schema built-in formats."""
    def __init__(self, *args):
        super().__init__(*args)
        # not a comprehensive list of all supported formats
        self._schema = """{
            "allOf": [
                {"type": "string"},
                {"format": "date-time"},
                {"format": "email"},
                {"format": "hostname"},
                {"format": "ipv4"},
                {"format": "ipv6"},
                {"format": "uri"},
                {"format": "uri-reference"},
                {"format": "uri-template"},
                {"format": "json-pointer"}
            ]
        }"""
    def test_enabled(self):
        """Test JSON Schema built-in formats are enabled by default"""
        root = RootSchema.loads(self._schema, DEFAULT_URI)
        # no string can match all formats
        self.assertRaises(ValueError, root, '')
        self.assertRaises(ValueError, root, 'foobar')
    def test_disabled(self):
        """Test JSON Schema built-in formats can be disabled"""
        format_names = (
            'date-time',
            'email',
            'hostname',
            'ipv4',
            'ipv6',
            'uri',
            'uri-reference',
            'uri-template',
            'json-pointer',
        )
        formats = dict((fmt, None) for fmt in format_names)
        support = Support(formats=formats)
        root = RootSchema.loads(self._schema, DEFAULT_URI, support=support)
        self.assertEqual(root(''), '')
        self.assertEqual(root('foobar'), 'foobar')

# Test custom formats support

class EthernetInterface(Pattern): # pylint: disable=too-few-public-methods
    """A duck-typed custom format for ethernet interface strings."""
    def __init__(self):
        Pattern.__init__(self, '^eth[0-9]$')
    @staticmethod
    def validates(primitive):
        """Return True is `primitive` is 'string'."""
        return primitive == 'string'

class TestCustomFormat(TestCase):
    """Test JSON Schema custom format."""
    def __init__(self, *args):
        super().__init__(*args)
        self._schema = json.dumps({
            'type': 'string',
            'format': 'ethernet-interface',
        })
        self._formats = {
            'ethernet-interface': EthernetInterface(),
        }
    @params(
        'null',
        'false',
        'true',
        '7',
        '-0.3',
        '["eth0", "eth1", "eth2"]',
        '{"eth0": "eth1"}',
    )
    def test_reject_type(self, string):
        """Test JSON Schema custom format does not affect type check"""
        support = Support(formats=self._formats)
        root = RootSchema.loads(self._schema, DEFAULT_URI, support=support)
        self.assertRaises(TypeError, root.decode, string)
    @params(
        '"foo"',
        '" eth0"',
        '"eth0 "',
        '"eth01"',
    )
    def test_reject_value(self, string):
        """Test JSON Schema custom format rejects value"""
        support = Support(formats=self._formats)
        root = RootSchema.loads(self._schema, DEFAULT_URI, support=support)
        self.assertRaises(ValueError, root.decode, string)
    @params(
        '"eth0"',
        '"eth1"',
        '"eth2"',
        '"eth3"',
        '"eth4"',
        '"eth5"',
        '"eth6"',
        '"eth7"',
        '"eth8"',
        '"eth9"',
    )
    def test_accept(self, string):
        """Test JSON Schema custom format accepts value"""
        support = Support(formats=self._formats)
        root = RootSchema.loads(self._schema, DEFAULT_URI, support=support)
        self.assertEqual(json.dumps(root.decode(string)), string)
        self.assertEqual(root.encode(json.loads(string)), string)
    @params(
        '"foo"',
        '" eth0"',
        '"eth0 "',
        '"eth01"',
        '"eth0"',
        '"eth1"',
        '"eth2"',
        '"eth3"',
    )
    def test_ignore(self, string):
        """Test JSON Schema custom format is ignored if no support"""
        root = RootSchema.loads(self._schema, DEFAULT_URI)
        self.assertEqual(json.dumps(root.decode(string)), string)
        self.assertEqual(root.encode(json.loads(string)), string)
