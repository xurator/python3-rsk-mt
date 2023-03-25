### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for JSON Schemas"""

import json
from os.path import abspath
from urllib.parse import urlunsplit

from unittest import TestCase
from nose2.tools import params

from rsk_mt.jsonschema.schema import (
    RootSchema,
    Support,
    Results,
)

# An absolute URI for general use in test cases.
DEFAULT_URI = urlunsplit(('file', '', abspath(__file__), '', ''))

SCHEMA_IDS = (
    'http://json-schema.org/schema#',
    'http://json-schema.org/hyper-schema#',
    'http://json-schema.org/draft-07/schema#',
    'http://json-schema.org/draft-07/hyper-schema#',
    'http://json-schema.org/draft-06/schema#',
    'http://json-schema.org/draft-06/hyper-schema#',
    'http://json-schema.org/draft-05/schema#',
    'http://json-schema.org/draft-05/hyper-schema#',
    'http://json-schema.org/draft-04/schema#',
    'http://json-schema.org/draft-04/hyper-schema#',
    'http://json-schema.org/draft-03/schema#',
    'http://json-schema.org/draft-03/hyper-schema#',
    'http://json-schema.org/draft-02/schema#',
    'http://json-schema.org/draft-02/hyper-schema#',
    'http://json-schema.org/draft-01/schema#',
    'http://json-schema.org/draft-01/hyper-schema#',
)
SUPPORTED_SCHEMA_IDS = (
    'http://json-schema.org/draft-07/schema#',
)
UNSUPPORTED_SCHEMA_IDS = tuple(sorted(
    frozenset(SCHEMA_IDS) - frozenset(SUPPORTED_SCHEMA_IDS)
))

class _MockSchema():
    """A mock Schema."""
    def __init__(self, ref, uri, base_uri):
        self._ref = ref
        self._uri = uri
        self._base_uri = base_uri
    @property
    def ref(self):
        """Return this instance's ref."""
        return self._ref
    @property
    def uri(self):
        """Return this instance's uri."""
        return self._uri
    @property
    def base_uri(self):
        """Return this instance's base uri."""
        return self._base_uri

class _Support(Support): # pylint: disable=too-few-public-methods
    """Support allowing one schema to be loaded."""
    def __init__(self, uri, root, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._uri = uri
        self._root = root
    def load_schema(self, uri):
        """Return the single schema."""
        if uri != self._uri:
            raise ValueError(uri)
        return self._root

class TestSchema(TestCase):
    """JSON Schema tests for rsk_mt.jsonschema.schema.(Root)Schema."""
    # https://tools.ietf.org/html/draft-handrews-json-schema-01#section-4.3.1
    # "A JSON Schema MUST be an object or a boolean."
    @params(
        'null',
        '1',
        '-3.21',
        '"foo"',
        '["foo", "bar"]',
    )
    def test_reject(self, string):
        """Test JSON Schema rejects bad schema"""
        self.assertRaises(ValueError, RootSchema.loads, string, DEFAULT_URI)
    @params(
        'false',
        'true',
        '{}', # empty object equivalent to true
    )
    def test_accept_boolean(self, schema):
        """Test JSON Schema accepts boolean schema"""
        root = RootSchema.loads(schema, DEFAULT_URI)
        self.assertIsNone(root.id_)
        self.assertIsNone(root.title)
        self.assertIsNone(root.description)
        self.assertRaises(KeyError, getattr, root, 'default')
        self.assertEqual(root.base_uri, DEFAULT_URI)
        self.assertEqual(root.uri, DEFAULT_URI)
        self.assertRaises(RuntimeError, setattr, root, 'uri', DEFAULT_URI)
        self.assertEqual(root.pointer, '')
        self.assertEqual(root.ref, '#')
        self.assertEqual(
            frozenset((DEFAULT_URI, DEFAULT_URI + '#')),
            frozenset(root.uris),
        )
        self.assertIsNotNone(root.implementation)
        self.assertEqual(root.get_bases('#'), ())
        self.assertIsNone(root.get_format('invalid'))
        self.assertIsNone(root.get_encoding('invalid'))
        self.assertIsNone(root.get_optimised('#'))
        self.assertRaises(KeyError, root.get_schema, '#/invalid')
        self.assertRaises(KeyError, root.get_schema, '#/invalid', load=False)
        self.assertRaises(ValueError, root.get_schema, 'http://invalid')
        self.assertRaises(
            ValueError,
            root.get_schema, 'http://invalid', load=False,
        )
        mock_uri = _MockSchema('invalid-ref', DEFAULT_URI, DEFAULT_URI)
        self.assertRaises(KeyError, root.declare, mock_uri)
        mock_ref = _MockSchema('#', 'invalid-uri', DEFAULT_URI)
        self.assertRaises(KeyError, root.declare, mock_ref)
    @params(
        None,
        False,
        True,
        1,
        -1.2,
        [],
        {},
    )
    def test_boolean_false(self, value):
        """Test JSON Schema boolean false schema"""
        schema = 'false'
        root = RootSchema.loads(schema, DEFAULT_URI)
        self.assertRaises(ValueError, root, value)
        self.assertRaises(ValueError, root.cast, value)
        self.assertEqual(root.validate(value), False)
        results = Results.build()
        self.assertEqual(root.debug(value, results), False)
        self.assertEqual(results, {})
    @params(
        None,
        False,
        True,
        1,
        -1.2,
        [],
        {},
    )
    def test_boolean_true(self, value):
        """Test JSON Schema boolean true schema"""
        for schema in ('true', '{}'):
            root = RootSchema.loads(schema, DEFAULT_URI)
            self.assertEqual(root(value), value)
            self.assertEqual(root.cast(value), value)
            self.assertEqual(root.validate(value), True)
            results = Results.build()
            self.assertEqual(root.debug(value, results), True)
            self.assertEqual(results, {})

    # https://tools.ietf.org/html/draft-handrews-json-schema-01#section-7
    @params(*UNSUPPORTED_SCHEMA_IDS)
    def test_unsupported_metaschema(self, schema_id):
        """Test JSON Schema rejects unsupported $schema"""
        schema = json.dumps({'$schema': schema_id})
        self.assertRaises(ValueError, RootSchema.loads, schema, DEFAULT_URI)
    @params(*SUPPORTED_SCHEMA_IDS)
    def test_supported_metaschema(self, schema_id):
        """Test JSON Schema accepts supported $schema"""
        schema = json.dumps({'$schema': schema_id})
        root = RootSchema.loads(schema, DEFAULT_URI)
        self.assertEqual(root.spec, {'$schema': schema_id})
    def test_no_metaschema(self):
        """Test JSON Schema accepts no $schema"""
        root = RootSchema.loads('{}', DEFAULT_URI)
        self.assertEqual(root.spec, {})
    @params(*SCHEMA_IDS)
    def test_subschema_metaschema(self, schema_id):
        """Test JSON Schema rejects subschema $schema"""
        schema = json.dumps({'not': {'$schema': schema_id}})
        self.assertRaises(ValueError, RootSchema.loads, schema, DEFAULT_URI)

    # https://tools.ietf.org/html/draft-handrews-json-schema-01#section-8.1
    def test_reject_uri(self):
        """Test JSON Schema rejects non absolute URI"""
        self.assertRaises(ValueError, RootSchema.loads, '{}', '#fragment')

    # https://tools.ietf.org/html/draft-handrews-json-schema-01#section-8.2
    def test_reject_id(self):
        """Test JSON Schema rejects non URI-reference $id"""
        # root $id is valid: nested $id is not a URI reference
        schema = json.dumps({
            '$id': 'http://example.com/root.json',
            'definitions': {
                'A': {
                    '$id': 'bad://',
                },
            },
        })
        self.assertRaises(ValueError, RootSchema.loads, schema, DEFAULT_URI)

    # https://tools.ietf.org/html/draft-handrews-json-schema-01#section-8.2.1
    def test_reject_root_id(self):
        """Test JSON Schema rejects non absolute URI $id"""
        schema = json.dumps({'$id': '//foo/bar'})
        self.assertRaises(ValueError, RootSchema.loads, schema, DEFAULT_URI)
    def test_accept_root_id(self):
        """Test JSON Schema accepts absolute URI $id"""
        schema = json.dumps({'$id': 'http://example.com/root.json'})
        root = RootSchema.loads(schema, DEFAULT_URI)
        self.assertEqual(root.base_uri, 'http://example.com/root.json')
        self.assertEqual(
            frozenset((
                'http://example.com/root.json',
                'http://example.com/root.json#',
            )),
            frozenset(root.uris),
        )
    def test_accept_root_id_empty_fragment(self):
        """Test JSON Schema accepts $id with empty fragment"""
        schema = json.dumps({'$id': 'http://example.com/root.json#'})
        root = RootSchema.loads(schema, DEFAULT_URI)
        self.assertEqual(root.base_uri, 'http://example.com/root.json#')
        self.assertEqual(
            frozenset((
                'http://example.com/root.json',
                'http://example.com/root.json#',
            )),
            frozenset(root.uris),
        )

    # https://tools.ietf.org/html/draft-handrews-json-schema-01#section-8.2.2
    def test_accept_subschema_id(self):
        """Test JSON Schema subschema accepts absolute URI $id"""
        schema = json.dumps({
            '$id': 'http://example.com/root.json',
            'definitions': {
                'A': {
                    '$id': 'http://example.com/other.json'
                },
            },
        })
        root = RootSchema.loads(schema, DEFAULT_URI)
        self.assertEqual(root.id_, 'http://example.com/root.json')
        self.assertEqual(root.base_uri, 'http://example.com/root.json')
        self.assertEqual(root.uri, 'http://example.com/root.json')
        self.assertEqual(root.pointer, '')
        self.assertEqual(root.ref, '#')
        self.assertEqual(root.relative_ref(root), '#')
        # pylint: disable=invalid-name
        ref_A = root.absolute_ref('definitions', 'A')
        self.assertEqual(ref_A, '#/definitions/A')
        schema_A = root.get_schema(ref_A)
        self.assertIsNotNone(schema_A)
        self.assertEqual(schema_A.id_, 'http://example.com/other.json')
        self.assertEqual(schema_A.base_uri, 'http://example.com/other.json')
        self.assertEqual(schema_A.uri, 'http://example.com/other.json')
        self.assertEqual(schema_A.pointer, '/definitions/A')
        self.assertEqual(schema_A.ref, '#/definitions/A')
        self.assertEqual(root.relative_ref(schema_A), '#/definitions/A')
        self.assertRaises(ValueError, schema_A.relative_ref, root)
        self.assertEqual(
            frozenset((
                'http://example.com/root.json',
                'http://example.com/root.json#',
                'http://example.com/root.json#/definitions/A',
                'http://example.com/other.json',
                'http://example.com/other.json#',
            )),
            frozenset(root.uris),
        )

    # https://tools.ietf.org/html/draft-handrews-json-schema-01#section-8.2.3
    def test_accept_subschema_locn_indep_id(self):
        """Test JSON Schema subschema accepts location independent $id"""
        schema = json.dumps({
            '$id': 'http://example.com/root.json',
            'definitions': {
                'A': {
                    '$id': '#Aa0-_:.'
                }
            }
        })
        root = RootSchema.loads(schema, DEFAULT_URI)
        self.assertEqual(
            frozenset((
                'http://example.com/root.json',
                'http://example.com/root.json#',
                'http://example.com/root.json#/definitions/A',
                'http://example.com/root.json#Aa0-_:.',
            )),
            frozenset(root.uris),
        )
    def test_reject_subschema_locn_indep_id(self):
        """Test JSON Schema rejects bad location independent $id"""
        schema = json.dumps({
            '$id': 'http://example.com/root.json',
            'definitions': {
                'A': {
                    '$id': '#£$%',
                },
            },
        })
        self.assertRaises(ValueError, RootSchema.loads, schema, DEFAULT_URI)
    def test_reject_dup_locn_indep_id(self):
        """Test JSON Schema rejects duplication location independent $id"""
        schema = json.dumps({
            '$id': 'http://example.com/root.json',
            'definitions': {
                'A': {
                    '$id': '#foo',
                },
                'B': {
                    '$id': '#foo',
                },
            },
        })
        self.assertRaises(KeyError, RootSchema.loads, schema, DEFAULT_URI)
        schema = json.dumps({
            '$id': 'http://example.com/root.json',
            'definitions': {
                'A': {
                    '$id': '#/definitions/A',
                },
            },
        })
        support = Support(formats={
            'location-independent-$id': None,
        })
        self.assertRaises(
            KeyError,
            RootSchema.loads, schema, DEFAULT_URI, support=support,
        )

    # https://tools.ietf.org/html/draft-handrews-json-schema-01#section-8.2.4
    # Use the specification example as a test case.
    def test_base_uri_dereferencing(self):
        """Test JSON Schema base URIs and dereferencing"""
        root = RootSchema.loads("""{
            "$id": "http://example.com/root.json",
            "definitions": {
                "A": { "$id": "#foo" },
                "B": {
                    "$id": "other.json",
                    "definitions": {
                        "X": { "$id": "#bar" },
                        "Y": { "$id": "t/inner.json" }
                    }
                },
                "C": {
                    "$id": "urn:uuid:ee564b8a-7a87-4125-8c96-e9f123d6766f"
                }
            }
        }""", DEFAULT_URI)
        self.assertEqual(root.id_, 'http://example.com/root.json')
        self.assertEqual(root.base_uri, 'http://example.com/root.json')
        self.assertEqual(root.uri, 'http://example.com/root.json')
        self.assertEqual(root.pointer, '')
        self.assertEqual(root.ref, '#')
        self.assertEqual(root.relative_ref(root), '#')
        for uri in (
                'http://example.com/root.json',
                'http://example.com/root.json#',
            ):
            self.assertIs(root, root.get_schema(uri))
        # pylint: disable=invalid-name
        ### /definitions/A
        ref_A = root.absolute_ref('definitions', 'A')
        self.assertEqual(ref_A, '#/definitions/A')
        schema_A = root.get_schema(ref_A)
        self.assertIsNotNone(schema_A)
        self.assertEqual(schema_A.id_, '#foo')
        self.assertEqual(schema_A.base_uri, 'http://example.com/root.json')
        self.assertEqual(schema_A.uri, 'http://example.com/root.json#foo')
        self.assertEqual(schema_A.pointer, '/definitions/A')
        self.assertEqual(schema_A.ref, '#/definitions/A')
        self.assertEqual(root.relative_ref(schema_A), '#/definitions/A')
        for uri in (
                'http://example.com/root.json#foo',
                'http://example.com/root.json#/definitions/A',
            ):
            self.assertIs(schema_A, root.get_schema(uri))
        ### /definitions/B
        ref_B = root.absolute_ref('definitions', 'B')
        self.assertEqual(ref_B, '#/definitions/B')
        schema_B = root.get_schema(ref_B)
        self.assertIsNotNone(schema_B)
        self.assertEqual(schema_B.id_, 'other.json')
        self.assertEqual(schema_B.base_uri, 'http://example.com/other.json')
        self.assertEqual(schema_B.uri, 'http://example.com/other.json')
        self.assertEqual(schema_B.pointer, '/definitions/B')
        self.assertEqual(schema_B.ref, '#/definitions/B')
        self.assertEqual(root.relative_ref(schema_B), '#/definitions/B')
        for uri in (
                'http://example.com/other.json',
                'http://example.com/other.json#',
                'http://example.com/root.json#/definitions/B',
            ):
            self.assertIs(schema_B, root.get_schema(uri))
        ### /definitions/B/definitions/X
        ref_X = schema_B.absolute_ref('definitions', 'X')
        self.assertEqual(ref_X, '#/definitions/B/definitions/X')
        schema_X = root.get_schema(ref_X)
        self.assertIsNotNone(schema_X)
        self.assertEqual(schema_X.id_, '#bar')
        self.assertEqual(schema_X.base_uri, 'http://example.com/other.json')
        self.assertEqual(schema_X.uri, 'http://example.com/other.json#bar')
        self.assertEqual(schema_X.pointer, '/definitions/B/definitions/X')
        self.assertEqual(schema_X.ref, '#/definitions/B/definitions/X')
        self.assertEqual(
            root.relative_ref(schema_X),
            '#/definitions/B/definitions/X',
        )
        self.assertEqual(schema_B.relative_ref(schema_X), '#/definitions/X')
        for uri in (
                'http://example.com/other.json#bar',
                'http://example.com/other.json#/definitions/X',
                'http://example.com/root.json#/definitions/B/definitions/X',
            ):
            self.assertIs(schema_X, root.get_schema(uri))
        ### /definitions/B/definitions/Y
        ref_Y = root.absolute_ref('definitions', 'B', 'definitions', 'Y')
        self.assertEqual(ref_Y, '#/definitions/B/definitions/Y')
        schema_Y = root.get_schema(ref_Y)
        self.assertIsNotNone(schema_Y)
        self.assertEqual(schema_Y.id_, 't/inner.json')
        self.assertEqual(schema_Y.base_uri, 'http://example.com/t/inner.json')
        self.assertEqual(schema_Y.uri, 'http://example.com/t/inner.json')
        self.assertEqual(schema_Y.pointer, '/definitions/B/definitions/Y')
        self.assertEqual(schema_Y.ref, '#/definitions/B/definitions/Y')
        self.assertEqual(
            root.relative_ref(schema_Y),
            '#/definitions/B/definitions/Y',
        )
        self.assertEqual(schema_B.relative_ref(schema_Y), '#/definitions/Y')
        for uri in (
                'http://example.com/t/inner.json',
                'http://example.com/t/inner.json#',
                'http://example.com/other.json#/definitions/Y',
                'http://example.com/root.json#/definitions/B/definitions/Y',
            ):
            self.assertIs(schema_Y, root.get_schema(uri))
        ### /definitions/C
        ref_C = root.absolute_ref('definitions', 'C')
        self.assertEqual(ref_C, '#/definitions/C')
        schema_C = root.get_schema(ref_C)
        self.assertIsNotNone(schema_C)
        urn_C = 'urn:uuid:ee564b8a-7a87-4125-8c96-e9f123d6766f'
        self.assertEqual(schema_C.id_, urn_C)
        self.assertEqual(schema_C.base_uri, urn_C)
        self.assertEqual(schema_C.uri, urn_C)
        self.assertEqual(schema_C.pointer, '/definitions/C')
        self.assertEqual(schema_C.ref, '#/definitions/C')
        self.assertEqual(root.relative_ref(schema_C), '#/definitions/C')
        for uri in (
                urn_C,
                urn_C + '#',
                'http://example.com/root.json#/definitions/C',
            ):
            self.assertIs(schema_C, root.get_schema(uri))
        self.assertEqual(
            frozenset((
                'http://example.com/root.json',
                'http://example.com/root.json#',
                'http://example.com/root.json#/definitions/A',
                'http://example.com/root.json#/definitions/B',
                'http://example.com/root.json#/definitions/B/definitions',
                'http://example.com/root.json#/definitions/B/definitions/X',
                'http://example.com/root.json#/definitions/B/definitions/Y',
                'http://example.com/root.json#/definitions/C',
                'http://example.com/root.json#foo',
                'http://example.com/other.json',
                'http://example.com/other.json#',
                'http://example.com/other.json#/definitions',
                'http://example.com/other.json#/definitions/X',
                'http://example.com/other.json#/definitions/Y',
                'http://example.com/other.json#bar',
                'http://example.com/t/inner.json',
                'http://example.com/t/inner.json#',
                urn_C,
                urn_C + '#',
            )),
            frozenset(root.uris),
        )

    # https://tools.ietf.org/html/draft-handrews-json-schema-01#section-8.3.1
    def test_external_reference_undefined(self):
        """Test JSON Schema rejects undefined external reference"""
        schema = json.dumps({
            '$id': 'http://example.com/root.json',
            '$ref': 'http://example.com/other.json'
        })
        self.assertRaises(ValueError, RootSchema.loads, schema, DEFAULT_URI)
    def test_external_reference_declare(self):
        """Test JSON Schema accepts declared external reference"""
        schema = json.dumps({
            '$id': 'http://example.com/root.json',
            '$ref': 'http://example.com/other.json'
        })
        root = RootSchema.loads(schema, DEFAULT_URI, define=False)
        self.assertIsNone(root.implementation)
        self.assertEqual(
            frozenset((
                'http://example.com/root.json',
                'http://example.com/root.json#',
            )),
            frozenset(root.uris),
        )

    # https://tools.ietf.org/html/draft-handrews-json-schema-01#section-8.3.2
    # Use the example as a test case.
    def test_references(self):
        """Test JSON Schema references"""
        other_uri = 'http://example.net/other.json'
        support = _Support(other_uri, RootSchema.loads("""{
            "$id": "http://example.net/other.json",
            "type": "integer"
        }""", other_uri))
        root = RootSchema.loads("""{
            "$id": "http://example.net/root.json",
            "items": {
                "type": "array",
                "items": { "$ref": "#item" }
            },
            "definitions": {
                "single": {
                    "$id": "#item",
                    "type": "object",
                    "additionalProperties": { "$ref": "other.json" }
                }
            }
        }""", DEFAULT_URI, support=support)
        self.assertEqual(
            root([[{'a': 1}, {'b': 2}, {'c': 3}]]),
            (({'a': 1}, {'b': 2}, {'c': 3}),),
        )
        ### implicit array at top-level restricts only arrays...
        self.assertEqual(
            root([]),
            (),
        )
        self.assertEqual(
            root([[]]),
            ((),),
        )
        self.assertEqual(
            root([[{'a': 1}]]),
            (({'a': 1},),),
        )
        self.assertEqual(
            root([[{'a': 1}, {'b': 2}, {'c': 3}]]),
            (({'a': 1}, {'b': 2}, {'c': 3}),),
        )
        self.assertEqual(
            root([[{'a': 1}, {'b': 2}], [{'c': 3}]]),
            (({'a': 1}, {'b': 2}), ({'c': 3},)),
        )
        self.assertEqual(
            root([[{'a': 1}, {'b': 2}], []]),
            (({'a': 1}, {'b': 2}), ()),
        )
        self.assertEqual(
            root([[], [{'a': 1}, {'b': 2}]]),
            ((), ({'a': 1}, {'b': 2})),
        )
        ### ...other value types are permitted to slip the net
        self.assertEqual(root(None), None)
        self.assertEqual(root(False), False)
        self.assertEqual(root(True), True)
        self.assertEqual(root(1), 1)
        self.assertEqual(root(1.5), 1.5)
        self.assertEqual(root('foo'), 'foo')
        self.assertEqual(root({}), {})
        self.assertEqual(root({'foo': 'bar'}), {'foo': 'bar'})
        ### ...only non-conforming arrays are rejected
        self.assertRaises(TypeError, root, [1])
        self.assertRaises(TypeError, root, [['a']])
        self.assertRaises(TypeError, root, [[[1]]])
        self.assertRaises(TypeError, root, [[{'a': 'b'}]])

    def test_internal_references_nested(self):
        """Test JSON Schema references with nested absolute URI $id"""
        root = RootSchema.loads("""{
            "$id": "http://example.com/root.json",
            "oneOf": [{
                "$id": "http://example.com/nested.json",
                "type": "object",
                "properties": {
                    "bar": {
                        "$id": "#bar",
                        "type": "boolean"
                    },
                    "baz": {
                        "$ref": "#bar"
                    }
                }
            }],
            "definitions": {
                "bar": {
                    "$id": "#bar",
                    "type": "string"
                }
            }
        }""", DEFAULT_URI)
        ### test object with boolean values conform to nested.json#bar
        self.assertEqual(root({"bar": False}), {'bar': False})
        self.assertEqual(root({"baz": True}), {'baz': True})
        ### test object with other values do not conform to nested.json#bar
        self.assertRaises(ValueError, root, {"bar": "foo"})
        self.assertRaises(ValueError, root, {"baz": [True]})
