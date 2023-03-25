### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for JSON Schema types"""

from nose2.tools import params

from ... import make_params_values

class TypeTestBuilder(type):
    """Build tests for rsk_mt.jsonschema.types.

    Specify this class as metaclass and provide:
    `type_name` - common type name
    `type_` - a callable type instance
    `accept` - an iterable of values this type must accept
    `reject` - an iterable of values this type must reject
    """
    def __new__(cls, name, bases, dct):
        type_ = dct['type_']
        type_name = dct['type_name']
        # build out class for testing `type_`
        dct.update({
            'test_accept': cls.make_test_accept(
                type_, type_name,
                make_params_values(dct['accept']),
            ),
            'test_reject': cls.make_test_reject(
                type_, type_name,
                make_params_values(dct['reject']),
            ),
        })
        return super().__new__(cls, name, bases, dct)
    # make functions for use as TestCase methods
    @staticmethod
    def make_test_accept(type_, type_name, values):
        """Make a function testing `type_` accepts `values`."""
        @params(*values)
        def method(self, value):
            """Test type accepts `value`."""
            self.assertEqual(type_(value), value)
        method.__doc__ = f'Test {type_name} accepts value'
        return method
    @staticmethod
    def make_test_reject(type_, type_name, values):
        """Make a function testing `type_` rejects `values`."""
        @params(*values)
        def method(self, value):
            """Test type rejects `value`."""
            self.assertRaises((TypeError, ValueError), type_, value)
        method.__doc__ = f'Test {type_name} rejects value'
        return method
