### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for rsk_mt.jsonschema.uri"""

from unittest import TestCase

from urllib.parse import (
    urlunsplit,
    urlsplit,
)

from rsk_mt.jsonschema.uri import TypeAbsoluteUri

class TypeAbsoluteUriTests(): # pylint: disable=no-member
    """Test cases for rsk_mt.jsonschema.uri.TypeAbsoluteUri."""
    dst = None
    src = {}
    grafted_src_path = None
    resolved_src_fragment = None
    resolved_src_path = None
    @staticmethod
    def _remove_scheme(uri):
        """Return a new value: `uri` without any scheme."""
        parts = urlsplit(uri)
        return urlunsplit(('',) + parts[1:5])
    @staticmethod
    def _set_fragment(uri, fragment):
        """Return a new value: `uri` with `fragment`."""
        parts = urlsplit(uri)
        return urlunsplit(parts[0:-1] + (fragment,))
    def test_without_scheme(self):
        """Test rsk_mt.jsonschema.uri.TypeAbsoluteUri rejects URI without scheme"""
        value_type = TypeAbsoluteUri()
        val = self._remove_scheme(self.src['abs'])
        self.assertRaises(ValueError, value_type, val)
    def test_with_fragment(self):
        """Test rsk_mt.jsonschema.uri.TypeAbsoluteUri rejects URI with fragment"""
        value_type = TypeAbsoluteUri()
        val = self._set_fragment(self.src['abs'], 'bad')
        self.assertRaises(ValueError, value_type, val)
    def test_absolute_uri(self):
        """Test rsk_mt.jsonschema.uri.TypeAbsoluteUri accepts absolute URI"""
        value_type = TypeAbsoluteUri()
        val = self.src['abs']
        self.assertEqual(value_type(val), val)
    def test_cast_uri(self):
        """Test rsk_mt.jsonschema.uri.TypeAbsoluteUri cast to absolute URI"""
        value_type = TypeAbsoluteUri()
        val = self.src['abs']
        # check empty fragment is removed
        self.assertEqual(value_type.cast(val + '#'), val)
    def test_graft_bad_dst(self):
        """Test rsk_mt.jsonschema.uri.TypeAbsoluteUri graft with bad dst"""
        value_type = TypeAbsoluteUri()
        dst = self._remove_scheme(self.dst)
        src = self.src['abs']
        self.assertRaises(ValueError, value_type.graft, dst, src)
    def test_graft_absolute_uri(self):
        """Test rsk_mt.jsonschema.uri.TypeAbsoluteUri graft src absolute URI"""
        value_type = TypeAbsoluteUri()
        dst = self.dst
        src = self.src['abs']
        self.assertEqual(value_type.graft(dst, src), src)
    def test_graft_fragment(self):
        """Test rsk_mt.jsonschema.uri.TypeAbsoluteUri graft src URI fragment"""
        value_type = TypeAbsoluteUri()
        dst = self.dst
        src = self.src['fragment']
        self.assertEqual(value_type.graft(dst, src), dst)
    def test_graft_path(self):
        """Test rsk_mt.jsonschema.uri.TypeAbsoluteUri graft src URI path"""
        value_type = TypeAbsoluteUri()
        dst = self.dst
        src = self.src['path']
        res = self.grafted_src_path
        if res:
            self.assertEqual(value_type.graft(dst, src), res)
        else:
            self.assertRaises(ValueError, value_type.graft, dst, src)
    def test_resolve_bad_dst(self):
        """Test rsk_mt.jsonschema.uri.TypeAbsoluteUri resolve with bad dst"""
        value_type = TypeAbsoluteUri()
        dst = self._remove_scheme(self.dst)
        src = self.src['abs']
        self.assertRaises(ValueError, value_type.resolve, dst, src)
    def test_resolve_absolute_uri(self):
        """Test rsk_mt.jsonschema.uri.TypeAbsoluteUri resolve absolute URI"""
        value_type = TypeAbsoluteUri()
        dst = self.dst
        src = self.src['abs']
        self.assertEqual(value_type.resolve(dst, src), src)
    def test_resolve_fragment(self):
        """Test rsk_mt.jsonschema.uri.TypeAbsoluteUri resolve URI fragment"""
        value_type = TypeAbsoluteUri()
        dst = self.dst
        src = self.src['fragment']
        res = self.resolved_src_fragment
        self.assertEqual(value_type.resolve(dst, src), res)
    def test_resolve_path(self):
        """Test rsk_mt.jsonschema.uri.TypeAbsoluteUri resolve URI path"""
        value_type = TypeAbsoluteUri()
        dst = self.dst
        src = self.src['path']
        res = self.resolved_src_path
        if res:
            self.assertEqual(value_type.resolve(dst, src), res)
        else:
            self.assertRaises(ValueError, value_type.resolve, dst, src)

class TestAbsoluteUrl(TestCase, TypeAbsoluteUriTests):
    """Test rsk_mt.jsonschema.uri.TypeAbsoluteUri for URLs."""
    dst = 'http://dst.example.co.uk/a/b/c?d=e'
    src = {
        'abs': 'ftp://src.example.co.uk/?f=g',
        'fragment': '#src',
        'path': '/src',
    }
    grafted_src_path = 'http://dst.example.co.uk/a/b/src?d=e'
    resolved_src_fragment = dst + src['fragment']
    resolved_src_path = grafted_src_path

class TestAbsoluteUrn(TestCase, TypeAbsoluteUriTests):
    """Test rsk_mt.jsonschema.uri.TypeAbsoluteUri for URNs."""
    dst = 'urn:dst:uk:co:example?A=B'
    src = {
        'abs': 'urn:src:uk:co:example?C=D',
        'fragment': '#src',
        'path': ':src',
    }
    grafted_src_path = None
    resolved_src_fragment = dst + src['fragment']
    resolved_src_path = None
