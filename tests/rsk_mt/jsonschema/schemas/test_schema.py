### SPDX-License-Identifier: GPL-2.0-or-later

"""File-based test cases for rsk_mt.jsonschema.schema"""

import json
import os.path
from os.path import join as joinpath
from os import walk as walkdir

from unittest import TestCase
from nose2.tools import params

from rsk_mt.jsonschema.schema import (
    RootSchema,
    Results,
)

BASEPATH = os.path.dirname(__file__)
DIRNAMES = tuple(
    d for d in tuple(walkdir(BASEPATH))[0][1] if not d.startswith('__')
)

# https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6

class TestSchema(TestCase):
    """File-based tests for rsk_mt.jsonschema.schema."""
    def load_schema(self, dirname):
        """Return a RootSchema from the schema file at `path`."""
        schema_file = joinpath(BASEPATH, dirname, 'schema.json')
        schema = RootSchema.load(schema_file)
        self.assertEqual(schema.binary, False)
        return schema
    @staticmethod
    def accept_values(dirname):
        """Return the values from the accept file at `path`."""
        accept_file = joinpath(BASEPATH, dirname, 'accept.json')
        with open(accept_file, encoding='utf-8') as fid:
            return json.load(fid)
    @staticmethod
    def reject_values(dirname):
        """Return the values from the reject file at `path`."""
        reject_file = joinpath(BASEPATH, dirname, 'reject.json')
        with open(reject_file, encoding='utf-8') as fid:
            return json.load(fid)
    @staticmethod
    def debug_values(dirname):
        """Return the values from the debug file at `path`."""
        debug_file = joinpath(BASEPATH, dirname, 'debug.json')
        with open(debug_file, encoding='utf-8') as fid:
            return json.load(fid)
    @params(*DIRNAMES)
    def test_accept(self, dirname):
        """Test rsk_mt.jsonschema.schema with schema.json and accept.json"""
        schema = self.load_schema(dirname)
        for val in self.accept_values(dirname):
            jval = json.dumps(val)
            self.assertEqual(json.dumps(schema(val)), jval)
            self.assertEqual(json.dumps(schema.cast(val)), jval)
            self.assertEqual(schema.validate(val), True)
            self.assertEqual(schema.encode(val), jval)
            self.assertEqual(json.dumps(schema.decode(json.dumps(val))), jval)
    @params(*DIRNAMES)
    def test_reject(self, dirname):
        """Test rsk_mt.jsonschema.schema with schema.json and reject.json"""
        schema = self.load_schema(dirname)
        for val in self.reject_values(dirname):
            jval = json.dumps(val)
            self.assertRaises((TypeError, ValueError), schema, val)
            self.assertRaises((TypeError, ValueError), schema.cast, val)
            self.assertEqual(schema.validate(val), False)
            self.assertRaises((TypeError, ValueError), schema.encode, val)
            self.assertRaises((TypeError, ValueError), schema.decode, jval)
    @params(*DIRNAMES)
    def test_debug(self, dirname):
        """Test rsk_mt.jsonschema.schema with schema.json and debug.json"""
        schema = self.load_schema(dirname)
        for dct in self.debug_values(dirname):
            results = Results.build()
            value = dct['value']
            returns = dct['returns']
            self.assertEqual(schema.debug(value, results), returns)
            self.assertEqual(results, dct['results'])
