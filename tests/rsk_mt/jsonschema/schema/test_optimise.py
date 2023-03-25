### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for JSON Schema application optimisation"""

from os.path import abspath
from urllib.parse import urlunsplit

from unittest import TestCase
from nose2.tools import params

from rsk_mt.jsonschema.schema import (
    RootSchema,
    Support,
    Results,
    Optimiser,
    Optimised,
)

DEFAULT_URI = urlunsplit(('file', '', abspath(__file__), '', ''))

class TestOptimised(TestCase):
    """Test base class rsk_mt.jsonschema.schema.Optimised"""
    @params(
        None,
        True,
        7,
        -0.3,
        '',
        'foo',
        'foobar',
        ['foo', 'bar'],
        {'foo': 'bar'},
    )
    def test_reject(self, val):
        """Test JSON Schema Optimised rejects value"""
        obj = Optimised()
        self.assertRaises(ValueError, obj.get_schema, val)

# Test application optimisation support

class Only():
    """A Schema implementation validating only values in `vals`.

    Debug results are reported against `schema`.
    """
    def __init__(self, vals, schema):
        self._vals = vals
        self._schema = schema
    def __call__(self, val):
        if val in self._vals:
            return val
        raise RuntimeError(val)
    def debug(self, val, results):
        """Populate `results` with a debug assertion result."""
        results.assertion(self._schema, 'kw', val in self._vals)

class ApplicationOptimised(Optimised): # pylint: disable=too-few-public-methods
    """Provide `only` as the schema implementation for all validation.

    `only` is a :class:`Only` instance.
    """
    def __init__(self, only):
        super().__init__()
        self._only = only
    def get_schema(self, val): # pylint: disable=unused-argument
        """Return the only schema."""
        return self._only

class ApplicationOptimiser(Optimiser): # pylint: disable=too-few-public-methods
    """Arrange for validation to accept `only` Python values."""
    def __init__(self, *only):
        super().__init__()
        self._only = only
    def optimised(self, uri, root):
        """Return a Validator substitute."""
        # kludge to get coverage of base implementation
        if super().optimised(uri, root) is not None:
            raise RuntimeError
        # create a Validator substitute, accepting `only` values
        return ApplicationOptimised(Only(self._only, root))

class TestApplicationOptimised(TestCase):
    """Test JSON Schema application optimisation.

    The schema states only string "foobar" is accepted: the "optimiser" performs
    abuse such that only a value equal to Python value False or 44 is accepted;
    any other value is rejected with RuntimeError.
    """
    only = (False, 44)
    def __init__(self, *args):
        super().__init__(*args)
        support = Support()
        support.set_optimiser(ApplicationOptimiser(*self.only))
        self._root = RootSchema.loads("""{
            "const": "foobar"
        }""", DEFAULT_URI, support=support)
    @params(
        None,
        True,
        7,
        -0.3,
        '',
        'foo',
        'foobar',
        ['foo', 'bar'],
        {'foo': 'bar'},
    )
    def test_reject(self, val):
        """Test JSON Schema application optimisation rejects value"""
        self.assertRaises(RuntimeError, self._root, val)
        results = Results.build()
        self._root.debug(val, results)
        self.assertEqual(results, {
            '': {
                DEFAULT_URI: {
                    'kw': False,
                }
            }
        })
    @params(*only)
    def test_accept(self, val):
        """Test JSON Schema application optimisation accepts value"""
        self.assertEqual(self._root(val), val)
        results = Results.build()
        self._root.debug(val, results)
        self.assertEqual(results, {
            '': {
                DEFAULT_URI: {
                    'kw': True,
                }
            }
        })
