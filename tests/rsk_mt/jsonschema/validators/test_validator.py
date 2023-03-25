### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for JSON Schema validators"""

from unittest import TestCase
from nose2.tools import params

from rsk_mt.jsonschema.schema import Results
from rsk_mt.jsonschema.validators.validator import equal

from ... import (
    make_fqname,
    make_params_values,
)

class MockRoot():
    """Mock root schema."""
    def __init__(self, base_uri, subschemas=(), formats=()):
        self._schemas = {s.ref: s for s in (MockSchema(base_uri),) + subschemas}
        self._formats = dict(formats)
    @staticmethod
    def get_bases(ref): # pylint: disable=unused-argument
        """Return an empty tuple => no custom bases."""
        return ()
    def get_format(self, name):
        """Return the format for `name`."""
        return self._formats.get(name)
    def get_schema(self, ref):
        """Return the value type for reference `ref`."""
        return self._schemas[ref]

class MockSchema():
    """Mock schema."""
    def __init__(self, base_uri, pointer='', value_type=None):
        self._base_uri = base_uri
        self._pointer = pointer
        self._value_type = value_type
    @property
    def pointer(self):
        """Return JSON pointer."""
        return self._pointer
    @property
    def ref(self):
        """Return URI-encoded JSON pointer."""
        return '#' + self.pointer
    @property
    def uri(self):
        """Return URI."""
        return self._base_uri + self.ref
    def absolute_ref(self, *args):
        """Return ref of subschema at `args`."""
        return self.ref + '/' + '/'.join([str(_) for _ in args])
    def check(self, val):
        """Value type check `val`."""
        return self._value_type.check(val)
    def __call__(self, val):
        """Value type enforce `val`."""
        return self._value_type(val)
    def validate(self, val):
        """Test whether `val` is valid."""
        try:
            self(val)
        except (TypeError, ValueError):
            return False
        else:
            return True
    def debug(self, val, results): # pylint: disable=unused-argument
        """Debug whether `val` is valid."""
        try:
            self(val)
        except (TypeError, ValueError):
            return False
        else:
            return True

class ValidatorTestBuilder(type):
    """"Build tests for rsk_mt.jsonschema.validators.Validator implementations.

    Specify this class as metaclass and provide:
    `validation` - a constructor taking a JSON Schema value (Python value)
    `schema` - the JSON Schema value
    """
    def __new__(cls, name, bases, dct):
        validation = dct['validation']
        fqname = make_fqname(validation)
        spec = dct['spec']
        root = dct['root']
        validator = validation(spec).validator(root, root.get_schema('#'))
        # build out class for testing `validator`
        dct.update({
            'validator': validator,
            'test_accept': cls.make_test_accept(
                validator, fqname,
                make_params_values(dct['accept']),
            ),
            'test_reject': cls.make_test_reject(
                validator, fqname,
                make_params_values(dct['reject']),
            ),
        })
        if 'debug' in dct:
            dct.update({
                'test_debug': cls.make_test_debug(
                    validator, fqname,
                    make_params_values(dct['debug']),
                ),
            })
        return super().__new__(cls, name, bases, dct)
    # make functions for use as TestCase methods
    @staticmethod
    def make_test_accept(validator, fqname, values):
        """Make a function testing `validator` accepts `values`."""
        @params(*values)
        def method(self, value):
            """Test validator accepts `value`."""
            self.assertEqual(validator(value), value)
        method.__doc__ = f'Test {fqname} accepts value'
        return method
    @staticmethod
    def make_test_reject(validator, fqname, values):
        """Make a function testing `validator` rejects `values`."""
        @params(*values)
        def method(self, value):
            """Test validator rejects `value`."""
            self.assertRaises((TypeError, ValueError), validator, value)
        method.__doc__ = f'Test {fqname} rejects value'
        return method
    @staticmethod
    def make_test_debug(validator, fqname, triples):
        """Make a function testing `validator` debugs (value, valid, detail)."""
        @params(*triples)
        def method(self, triple):
            """Test validator debugs `triple`"""
            (value, valid, detail) = triple
            results = Results.build()
            self.assertEqual(valid, validator.debug(value, results))
            self.assertEqual(detail, results)
        method.__doc__ = f'Test {fqname} debugs'
        return method

class TestEqual(TestCase):
    """Test rsk_mt.jsonschema.validators.equal"""
    def test_identity(self):
        """Test values for identity equality"""
        for val in (False, True, (1, 2, 3)):
            self.assertTrue(equal(val, val))
    def test_equality(self):
        """Test values for value equality"""
        for (val1, val2) in (
                (0, 0.0),
                (1.0, 1),
                ({'a': 'b'}, {'a': 'b'}),
                ([1, 2, 3], [1, 2, 3]),
                (({1: 2}, {3: 4}), ({1: 2}, {3: 4})),
            ):
            self.assertTrue(equal(val1, val2))
    def test_not_equal(self):
        """Test values for value inequality"""
        for (val1, val2) in (
                (False, 0),
                (True, 1),
                ((1, 2, 3), [1, 2, 3]),
            ):
            self.assertFalse(equal(val1, val2))
