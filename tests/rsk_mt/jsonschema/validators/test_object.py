### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema validator: object"""

from unittest import TestCase

from rsk_mt.enforce.value import (
    String,
    Number,
    Enum,
    ValueType,
)
from rsk_mt.jsonschema.validators import Object

from .test_validator import (
    ValidatorTestBuilder,
    MockRoot,
    MockSchema,
)

class SchemaFalse(ValueType):
    """Implementation of JSON Schema specified as JSON value false."""
    def __call__(self, val):
        raise ValueError(val)
    @staticmethod
    def debug(val, results): # pylint: disable=unused-argument
        """Return False: all values are invalid against this Schema."""
        return False

class TestObject(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator object."""
    validation = Object
    spec = {}
    base_uri = 'test://object/'
    root = MockRoot(base_uri)
    accept = (
        {},
        {"foo": "A"},
        {"foo": "A", "bar": 77},
        {"foo": "A", "bar": 77, "baz": [1, 2, 3]},
    )
    reject = (
        None,
        False, True,
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
    )
    debug = (
        ({}, True, {}),
        (-3, False, {}),
    )
    def test_generator(self):
        """Test JSON Schema validator object accepts generator."""
        self.assertEqual(
            {"foo": 1, "bar": 2},
            # pylint: disable=no-member
            self.validator(
                (pair for pair in (("foo", 1), ("bar", 2)))
            ),
        )

class TestMaxProperties(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator object maxProperties."""
    validation = Object
    spec = {
        'maxProperties': 2,
    }
    base_uri = 'test://object/maxProperties/'
    root = MockRoot(base_uri)
    accept = (
        {},
        {"foo": "A"},
        {"foo": "A", "bar": 77},
    )
    reject = (
        None,
        False, True,
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {"foo": "A", "bar": 77, "baz": [1, 2, 3]},
    )

class TestMinProperties(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator object minProperties."""
    validation = Object
    spec = {
        'minProperties': 2,
    }
    base_uri = 'test://object/minProperties/'
    root = MockRoot(base_uri)
    accept = (
        {"foo": "A", "bar": 77},
        {"foo": "A", "bar": 77, "baz": [1, 2, 3]},
    )
    reject = (
        None,
        False, True,
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {},
        {"foo": "A"},
    )

class TestProperties(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator object properties."""
    validation = Object
    spec = {
        'properties': {
            'foo': {
                'type': 'string',
            },
            'bar': {
                'type': 'number',
            },
            'baz': {
                'type': 'string',
            },
        },
        'required': ['foo', 'bar'],
    }
    base_uri = 'test://object/properties/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(base_uri, '/properties/foo', String()),
        MockSchema(base_uri, '/properties/bar', Number()),
        MockSchema(base_uri, '/properties/baz', String()),
    ))
    accept = (
        {"foo": "A", "bar": 77},
    )
    reject = (
        None,
        False, True,
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {},
        {"foo": "A"},
        {"foo": "A", "bar": 77, "baz": [1, 2, 3]},
    )

class TestPatternProperties(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator object patternProperties."""
    validation = Object
    spec = {
        'properties': {
            'overriding': {
                'type': 'number',
            },
        },
        'patternProperties': {
            '^x-.*': {
                'type': 'string',
            },
        },
        'additionalProperties': False,
        'required': ['x-rated'],
    }
    base_uri = 'test://object/patternProperties/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(base_uri, '/properties/overriding', Number()),
        MockSchema(base_uri, '/patternProperties/^x-.*', String()),
        MockSchema(base_uri, '/additionalProperties', SchemaFalse()),
    ))
    accept = (
        {"x-rated": "foo"},
        {"x-rated": "foo", "overriding": 99},
        {"x-rated": "foo", "x-men": "bar"},
        {"x-rated": "foo", "overriding": 99, "x-men": "bar"},
    )
    reject = (
        None,
        False, True,
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {},
        {"foo": "A"},
        {"foo": "A", "bar": 77},
        {"foo": "A", "bar": 77, "baz": [1, 2, 3]},
        {"overriding": 99},
        {"x-men": "bar"},
        {"overriding": 99, "x-men": "bar"},
    )
    debug = (
        (
            {"x-rated": "foo", "overriding": 99, "x-men": "bar"},
            True,
            {
                '': {
                    base_uri + '#': {
                        'properties': True,
                        'patternProperties': True,
                        'required': True,
                    },
                },
            },
        ),
    )

class TestAdditionalPropertiesTrue(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator object additionalProperties true."""
    validation = Object
    spec = {
        'properties': {
            'foo': {
                'type': 'string',
            },
            'bar': {
                'type': 'number',
            },
        },
        'required': ['bar'],
        'additionalProperties': True,
    }
    base_uri = 'test://object/additionalProperties/true/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(base_uri, '/properties/foo', String()),
        MockSchema(base_uri, '/properties/bar', Number()),
    ))
    accept = (
        {"foo": "A", "bar": 77},
        {"foo": "A", "bar": 77, "baz": [1, 2, 3]},
    )
    reject = (
        None,
        False, True,
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {},
        {"foo": "A"},
    )

class TestAdditionalPropertiesFalse(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator object additionalProperties false."""
    validation = Object
    spec = {
        'properties': {
            'foo': {
                'type': 'string',
            },
            'bar': {
                'type': 'number',
            },
        },
        'required': ['bar'],
        'additionalProperties': False,
    }
    base_uri = 'test://object/additionalProperties/false/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(base_uri, '/properties/foo', String()),
        MockSchema(base_uri, '/properties/bar', Number()),
        MockSchema(base_uri, '/additionalProperties', SchemaFalse()),
    ))
    accept = (
        {"foo": "A", "bar": 77},
    )
    reject = (
        None,
        False, True,
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {},
        {"foo": "A"},
        {"foo": "A", "bar": 77, "baz": [1, 2, 3]},
    )

class TestAdditionalPropertiesTyped(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator object additionalProperties typed."""
    validation = Object
    spec = {
        'properties': {
            'foo': {
                'type': 'string',
            },
            'bar': {
                'type': 'number',
            },
        },
        'required': ['foo'],
        'additionalProperties': {
            'type': 'number',
        },
    }
    base_uri = 'test://object/additionalProperties/typed/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(base_uri, '/properties/foo', String()),
        MockSchema(base_uri, '/properties/bar', Number()),
        MockSchema(base_uri, '/additionalProperties', Number()),
    ))
    accept = (
        {"foo": "A"},
        {"foo": "A", "bar": 77},
        {"foo": "A", "baz": 66},
    )
    reject = (
        None,
        False, True,
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {},
        {"foo": "A", "bar": 77, "baz": [1, 2, 3]},
    )
    debug = (
        (
            {"foo": "A", "bar": 77, "baz": [1, 2, 3]},
            False,
            {
                '': {
                    base_uri + '#': {
                        'properties': True,
                        'additionalProperties': False,
                        'required': True,
                    },
                },
            }
        ),
    )

class TestAdditionalPropertiesEmpty(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator object additonalProperties empty."""
    validation = Object
    spec = {
        'properties': {
            'foo': {
                'type': 'string',
            },
            'bar': {
                'type': 'number',
            },
        },
        'required': ['bar'],
        'additionalProperties': {},
    }
    base_uri = 'test://object/additionalProperties/empty/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(base_uri, '/properties/foo', String()),
        MockSchema(base_uri, '/properties/bar', Number()),
    ))
    accept = (
        {"foo": "A", "bar": 77},
        {"foo": "A", "bar": 77, "baz": [1, 2, 3]},
    )
    reject = (
        None,
        False, True,
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {},
        {"foo": "A"},
    )

class TestRequiredOver(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator object required over-specified."""
    validation = Object
    spec = {
        'properties': {
            'foo': {
                'type': 'string',
            },
        },
        'required': ['foo', 'bar'],
        'additionalProperties': False,
    }
    base_uri = 'test://object/required/over/'
    root = MockRoot(base_uri)
    accept = ()
    reject = (
        None,
        False, True,
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {},
        {"foo": "A"},
        {"foo": "A", "bar": 77},
        {"foo": "A", "bar": 77, "baz": [1, 2, 3]},
    )

class TestDependencies(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator object dependencies."""
    validation = Object
    spec = {
        'dependencies': {
            'foo': {
                'type': 'number',
            },
        }
    }
    base_uri = 'test://object/dependencies/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(base_uri, '/dependencies/foo', Number()),
    ))
    accept = (
        {},
        {"bar": 9},
        {"baz": [1, 2, 3]},
        {"bar": 9, "baz": [1, 2, 3]},
        {"X": "Y"},
    )
    reject = (
        None,
        False, True,
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {"foo": "A"},
        {"foo": "A", "bar": 77},
        {"foo": "A", "baz": [1, 2, 3]},
        {"foo": "A", "bar": 77, "baz": [1, 2, 3]},
    )
    debug = (
        (
            {"foo": "A"},
            False,
            {
                '': {
                    base_uri + '#': {
                        'dependencies': False,
                    },
                },
            },
        ),
    )

class TestDependenciesPresence(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator object dependencies presence."""
    validation = Object
    spec = {
        'dependencies': {
            'foo': ['bar', 'baz']
        }
    }
    base_uri = 'test://object/dependencies/presence/'
    root = MockRoot(base_uri)
    accept = (
        {},
        {"foo": "A", "bar": 77, "baz": [1, 2, 3]},
        {"foo": False, "bar": "baz", "baz": "qux", "qux": False},
        {"bar": 9},
        {"baz": [1, 2, 3]},
        {"bar": 9, "baz": [1, 2, 3]},
        {"X": "Y"}
    )
    reject = (
        None,
        False, True,
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {"foo": "A"},
        {"foo": "A", "bar": 77},
        {"foo": "A", "baz": [1, 2, 3]},
    )
    debug = (
        (
            {"foo": "A"},
            False,
            {
                '': {
                    base_uri + '#': {
                        'dependencies': False,
                    },
                },
            },
        ),
    )

class TestPropertyNames(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator object propertyNames."""
    validation = Object
    spec = {
        'propertyNames': {
            'enum': ['foo', 'bar'],
        },
    }
    base_uri = 'test://object/propertyNames/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(
            base_uri, '/propertyNames',
            Enum(spec['propertyNames']['enum']),
        ),
    ))
    accept = (
        {},
        {"foo": "A"},
        {"foo": "A", "bar": 77},
    )
    reject = (
        None,
        False, True,
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {"X": "Y"},
        {"foo": "A", "bar": 77, "baz": [1, 2, 3]},
    )

class TestPropertyNamesOver(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator object propertyNames over-specified."""
    validation = Object
    spec = {
        'properties': {
            'foo': {
                'type': 'string',
            },
        },
        'propertyNames': {
            'enum': ['foo', 'bar'],
        },
        'additionalProperties': False,
    }
    base_uri = 'test://object/propertyNames/over/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(base_uri, '/properties/foo', String()),
        MockSchema(
            base_uri, '/propertyNames',
            Enum(spec['propertyNames']['enum']),
        ),
        MockSchema(base_uri, '/additionalProperties', SchemaFalse()),
    ))
    accept = (
        {},
        {"foo": "A"},
    )
    reject = (
        None,
        False, True,
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {"X": "Y"},
        {"foo": "A", "bar": 77, "baz": [1, 2, 3]},
        {"foo": "A", "bar": 77},
    )

class TestPropertyNamesOver2(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator object propertyNames over-specified 2."""
    validation = Object
    spec = {
        'patternProperties': {
            '^b.*': {
                'type': 'string',
            }
        },
        'propertyNames': {
            'enum': ['foo', 'bar'],
        },
        'additionalProperties': False,
    }
    base_uri = 'test://object/propertyNames/over/2/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(base_uri, '/patternProperties/^b.*', String()),
        MockSchema(
            base_uri, '/propertyNames',
            Enum(spec['propertyNames']['enum']),
        ),
        MockSchema(base_uri, '/additionalProperties', SchemaFalse()),
    ))
    accept = (
        {},
        {"bar": "B"},
    )
    reject = (
        None,
        False, True,
        -3, -2, -1, 0, 1, 2, 3,
        -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,
        "", "foo", "foobar",
        (), ("foo", "bar", "foo"),
        {"X": "Y"},
        {"foo": "A"},
        {"bar": 77},
        {"baz": "C"},
        {"foo": "A", "bar": 77},
        {"foo": "A", "bar": "B"},
        {"bar": "B", "baz": "C"},
        {"bar": "B", "baz": [1, 2, 3]},
        {"foo": "A", "bar": "B", "baz": "C"},
        {"foo": "A", "bar": 77, "baz": [1, 2, 3]},
    )
