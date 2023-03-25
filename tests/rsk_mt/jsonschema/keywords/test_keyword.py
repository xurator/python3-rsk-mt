### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for JSON Schema keywords"""

import json
from os.path import abspath
from urllib.parse import urlunsplit

from nose2.tools import params

from rsk_mt.jsonschema.schema import (
    RootSchema,
    SchemaError,
)

from ... import make_params_values

DEFAULT_URI = urlunsplit(('file', '', abspath(__file__), '', ''))

class KeywordTestBuilder(type):
    """Build tests for JSON Schema keywords.

    Specify this class as metaclass and provide:
    `keyword` - keyword string
    `accept` - an iterable of values a Schema must accept for this keyword
    `reject` - an iterable of values a Schema must reject for this keyword
    """
    def __new__(cls, name, bases, dct):
        keyword = dct['keyword']
        # build out class for testing `keyword`
        dct.update({
            'test_accept': cls.make_test_accept(
                keyword,
                make_params_values(dct['accept']),
            ),
            'test_reject': cls.make_test_reject(
                keyword,
                make_params_values(dct['reject']),
            ),
        })
        return super().__new__(cls, name, bases, dct)
    # make functions for use as TestCase methods
    @staticmethod
    def make_test_accept(keyword, values):
        """Make a function testing `keyword` accepts `values`."""
        @params(*values)
        def method(self, value):
            """Test keyword accepts `value`."""
            schema = json.dumps({keyword: value})
            self.assertIsNotNone(RootSchema.loads(schema, DEFAULT_URI))
        method.__doc__ = f'Test JSON Schema keyword {keyword} accepts value'
        return method
    @staticmethod
    def make_test_reject(keyword, values):
        """Make a function testing `keyword` rejects `values`."""
        @params(*values)
        def method(self, value):
            """Test keyword rejects `value`."""
            schema = json.dumps({keyword: value})
            self.assertRaises(SchemaError, RootSchema.loads, schema, DEFAULT_URI)
        method.__doc__ = f'Test JSON Schema keyword {keyword} rejects value'
        return method
