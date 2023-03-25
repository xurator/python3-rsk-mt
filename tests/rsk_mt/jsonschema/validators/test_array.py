### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema validator: array"""

from unittest import TestCase

from rsk_mt.enforce.value import (String, Number, Enum)
from rsk_mt.jsonschema.validators import Array

from .test_validator import (
    ValidatorTestBuilder,
    MockRoot,
    MockSchema,
)

class TestArray(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator array."""
    validation = Array
    spec = {}
    base_uri = 'test://array/'
    root = MockRoot(base_uri)
    accept = (
        (), ("foo",), (1,), ("foo", 2), ("foo", "bar", "foo"),
    )
    reject = (
        None,
        False, True,
        "", "foo", "foobar",
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        {}, {"foo": "bar"},
    )
    debug = (
        ((), True, {}),
        (None, False, {}),
    )
    def test_generator(self):
        """Test JSON Schema validator array accepts generator."""
        self.assertEqual(
            (3, 2, 1),
            # pylint: disable=no-member
            self.validator(
                (i for i in (1 + 1 + 1, 1 + 1, 1))
            ),
        )

class TestItems(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator array items."""
    validation = Array
    spec = {
        'items': {
            'type': 'string',
        },
    }
    base_uri = 'test://array/items/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(base_uri, '/items', String()),
    ))
    accept = (
        (), ("foo",), ("foo", "bar", "foo"),
    )
    reject = (
        None,
        False, True,
        "", "foo", "foobar",
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        (1,), ("foo", 2),
        {}, {"foo": "bar"},
    )
    debug = (
        (
            ("foo",),
            True,
            {
                '': {
                    base_uri + '#': {
                        'items': True,
                    },
                },
            },
        ),
        (
            (1,),
            False,
            {
                '': {
                    base_uri + '#': {
                        'items': False,
                    },
                },
            },
        ),
    )

class TestAdditionalItemsForbidden(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator array additionalItems forbidden."""
    validation = Array
    spec = {
        'items': [{
            'type': 'string',
        }],
        'additionalItems': False,
    }
    base_uri = 'test://array/additionalItems/forbidden'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(base_uri, '/items/0', String()),
    ))
    accept = (
        (), ("foo",),
    )
    reject = (
        None,
        False, True,
        "", "foo", "foobar",
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        (1,), ("foo", 2), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )
    debug = (
        (
            ("foo", "bar"),
            False,
            {
                '': {
                    base_uri + '#': {
                        'items': True,
                        'additionalItems': False,
                    },
                },
            },
        ),
    )

class TestAdditionalItems(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator array additionalItems."""
    validation = Array
    spec = {
        'items': [{
            'type': 'string',
        }],
        'additionalItems': True,
    }
    base_uri = 'test://array/additionalItems/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(base_uri, '/items/0', String()),
    ))
    accept = (
        (), ("foo",), ("foo", 2), ("foo", "bar", "foo"),
    )
    reject = (
        None,
        False, True,
        "", "foo", "foobar",
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        (1,),
        {}, {"foo": "bar"},
    )

class TestAdditionalItemsTyped(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator array items additionalItems typed."""
    validation = Array
    spec = {
        'items': [{
            'type': 'string',
        }],
        'additionalItems': {
            'type': 'number',
        },
    }
    base_uri = 'test://array/additionalItems/typed/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(base_uri, '/items/0', String()),
        MockSchema(base_uri, '/additionalItems', Number()),
    ))
    accept = (
        (), ("foo",), ("foo", 2),
    )
    reject = (
        None,
        False, True,
        "", "foo", "foobar",
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        (1,), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )

class TestMaxItems(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator array maxItems."""
    validation = Array
    spec = {
        'maxItems': 2,
    }
    base_uri = 'test://array/maxItems/'
    root = MockRoot(base_uri)
    accept = (
        (), ("foo",), (1,), ("foo", 2),
    )
    reject = (
        None,
        False, True,
        "", "foo", "foobar",
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )

class TestMinItems(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator array minItems."""
    validation = Array
    spec = {
        'minItems': 2,
    }
    base_uri = 'test://array/minItems/'
    root = MockRoot(base_uri)
    accept = (
        ("foo", 2), ("foo", "bar", "foo"),
    )
    reject = (
        None,
        False, True,
        "", "foo", "foobar",
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        (), ("foo",), (1,),
        {}, {"foo": "bar"},
    )

class TestUniqueItems(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator array uniqueItems."""
    validation = Array
    spec = {
        'uniqueItems': True,
    }
    base_uri = 'test://array/uniqueItems/'
    root = MockRoot(base_uri)
    accept = (
        (), ("foo",), (1,), ("foo", 2),
    )
    reject = (
        None,
        False, True,
        "", "foo", "foobar",
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )

class TestContains(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator array contains."""
    validation = Array
    spec = {
        'items': [{
            'type': 'string',
        }],
        'contains': {
            'const': 'foo',
        },
    }
    base_uri = 'test://array/contains/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(base_uri, '/items/0', String()),
        MockSchema(base_uri, '/contains', Enum(('foo',))),
    ))
    accept = (
        ("foo",), ("foo", 2), ("foo", "bar", "foo"),
    )
    reject = (
        None,
        False, True,
        "", "foo", "foobar",
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        (), (1,),
        {}, {"foo": "bar"},
    )
    debug = (
        (
            ("foo", "bar", "foo"),
            True,
            {
                '': {
                    base_uri + '#': {
                        'items': True,
                        'contains': True,
                    },
                },
            },
        ),
    )

class TestCombined(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator array combined."""
    validation = Array
    spec = {
        'items': {
            'type': 'string',
        },
        'additionalItems': False,
        'maxItems': 3,
        'minItems': 1,
        'uniqueItems': True,
    }
    base_uri = 'test://array/combined/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(base_uri, '/items', String()),
    ))
    accept = (
        ("foo",),
    )
    reject = (
        None,
        False, True,
        "", "foo", "foobar",
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        (), (1,), ("foo", 2), ("foo", "bar", "foo"),
        {}, {"foo": "bar"},
    )
    debug = (
        (
            ("foo",),
            True,
            {
                '': {
                    base_uri + '#': {
                        'items': True,
                        'maxItems': True,
                        'minItems': True,
                        'uniqueItems': True,
                    },
                },
            }
        ),
        (
            ("foo", "bar", "foo"),
            False,
            {
                '': {
                    base_uri + '#': {
                        'items': True,
                        'maxItems': True,
                        'minItems': True,
                        'uniqueItems': False,
                    },
                },
            },
        ),
    )
