### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for JSON Schema metadata"""

import json
from os.path import abspath
from urllib.parse import urlunsplit

from unittest import TestCase

from rsk_mt.jsonschema.schema import RootSchema

DEFAULT_URI = urlunsplit(('file', '', abspath(__file__), '', ''))

# https://tools.ietf.org/html/draft-handrews-json-schema-01#section-8.1
# https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-10

class TestMetadata(TestCase):
    """JSON Schema metadata tests for rsk_mt.jsonschema.schema.RootSchema."""
    def __init__(self, *args):
        super().__init__(*args)
        schema = json.dumps({
            'title': 'metadata',
            'description': 'Test description.',
            'default': {
                'a': 1,
            },
        })
        self._root = RootSchema.loads(schema, DEFAULT_URI)
    def test_title(self):
        """Test JSON Schema metadata title"""
        self.assertEqual(self._root.title, 'metadata')
    def test_description(self):
        """Test JSON Schema metadata description"""
        self.assertEqual(self._root.description, 'Test description.')
    def test_default(self):
        """Test JSON Schema metadata default"""
        self.assertEqual(self._root.default, {'a': 1})
