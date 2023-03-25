### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for rsk_mt.jsonschema.identifiers"""

from unittest import TestCase
from nose2.tools import params

from rsk_mt.jsonschema.identifiers import key_path_to_json_pointer

# https://tools.ietf.org/html/rfc6901#section-5

class TestJsonPointer(TestCase):
    """Test rsk_mt.jsonschema.identifiers.key_path_to_json_pointer."""
    @params(
        ((), ''),
        (('foo',), '/foo'),
        (('foo', 0), '/foo/0'),
        (('',), '/'),
        (('a/b',), '/a~1b'),
        (('c%d',), '/c%d'),
        (('e^f',), '/e^f'),
        (('g|h',), '/g|h'),
        (('i\\j',), '/i\\j'),
        (('k"l',), '/k"l'),
        ((' ',), '/ '),
        (('m~n',), '/m~0n'),
    )
    def test_encoding(self, key_path, json_pointer):
        """Test rsk_mt.jsonschema.identifiers.key_path_to_json_pointer"""
        self.assertEqual(key_path_to_json_pointer(key_path), json_pointer)
