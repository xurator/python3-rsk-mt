### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema validator: conditional (if/then/else)"""

from unittest import TestCase

from rsk_mt.enforce.value import (Number, Constrained, Any)
from rsk_mt.enforce.constraint import Range
from rsk_mt.jsonschema.validators import Conditional

from .test_validator import (
    ValidatorTestBuilder,
    MockRoot,
    MockSchema,
)

class TestIfThenElse(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator if/then/else"""
    validation = Conditional
    spec = {
        'if': {
            'type': 'number',
            'minimum': 3,
        },
        'then': {
            'type': 'number',
            'maximum': 9,
        },
        'else': {
            'type': 'number',
            'maximum': -7,
        },
    }
    base_uri = 'test://if-then-else/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(
            base_uri, '/if',
            Constrained(Number(), (
                Range.yang(f"{spec['if']['minimum']} .. max"),
            )),
        ),
        MockSchema(
            base_uri, '/then',
            Constrained(Number(), (
                Range.yang(f"min .. {spec['then']['maximum']}"),
            )),
        ),
        MockSchema(
            base_uri, '/else',
            Constrained(Number(), (
                Range.yang(f"min .. {spec['else']['maximum']}"),
            )),
        ),
    ))
    accept = (
        4,
        -8,
    )
    reject = (
        10,
        1,
    )
    debug = (
        (
            4,
            True,
            {
                '': {
                    base_uri + '#': {
                        'if': True,
                        'then': True,
                    },
                },
            },
        ),
        (
            1,
            False,
            {
                '': {
                    base_uri + '#': {
                        'if': False,
                        'else': False,
                    },
                },
            }
        ),
    )

class TestIfFalseElse(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator if/false/else"""
    validation = Conditional
    spec = {
        'if': {
            'type': 'number',
            'minimum': 3,
        },
        'then': False,
        'else': {
            'type': 'number',
            'maximum': -7,
        },
    }
    base_uri = 'test://if-false-else/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(
            base_uri, '/if',
            Constrained(Number(), (
                Range.yang(f"{spec['if']['minimum']} .. max"),
            )),
        ),
        MockSchema(
            base_uri, '/then',
            Constrained(Number(), (
                Range.yang("max .. min"),
            )),
        ),
        MockSchema(
            base_uri, '/else',
            Constrained(Number(), (
                Range.yang(f"min .. {spec['else']['maximum']}"),
            )),
        ),
    ))
    accept = (
        -8,
    )
    reject = (
        4,
        10,
        1,
    )

class TestIfTrueElse(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator if/true/else"""
    validation = Conditional
    spec = {
        'if': {
            'type': 'number',
            'minimum': 3,
        },
        'then': True,
        'else': {
            'type': 'number',
            'maximum': -7,
        },
    }
    base_uri = 'test://if-true-else/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(
            base_uri, '/if',
            Constrained(Number(), (
                Range.yang(f"{spec['if']['minimum']} .. max"),
            )),
        ),
        MockSchema(
            base_uri, '/then',
            Any(),
        ),
        MockSchema(
            base_uri, '/else',
            Constrained(Number(), (
                Range.yang(f"min .. {spec['else']['maximum']}"),
            )),
        ),
    ))
    accept = (
        4,
        -8,
        10,
    )
    reject = (
        1,
    )

class TestIfThenFalse(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator if/then/false"""
    validation = Conditional
    spec = {
        'if': {
            'type': 'number',
            'minimum': 3,
        },
        'then': {
            'type': 'number',
            'maximum': 9,
        },
        'else': False,
    }
    base_uri = 'test://if-then-false/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(
            base_uri, '/if',
            Constrained(Number(), (
                Range.yang(f"{spec['if']['minimum']} .. max"),
            )),
        ),
        MockSchema(
            base_uri, '/then',
            Constrained(Number(), (
                Range.yang(f"min .. {spec['then']['maximum']}"),
            )),
        ),
        MockSchema(
            base_uri, '/else',
            Constrained(Number(), (
                Range.yang("max .. min"),
            )),
        ),
    ))
    accept = (
        4,
    )
    reject = (
        -8,
        10,
        1,
    )

class TestIfThenTrue(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator if/then/true"""
    validation = Conditional
    spec = {
        'if': {
            'type': 'number',
            'minimum': 3,
        },
        'then': {
            'type': 'number',
            'maximum': 9,
        },
        'else': True,
    }
    base_uri = 'test://if-then-true/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(
            base_uri, '/if',
            Constrained(Number(), (
                Range.yang(f"{spec['if']['minimum']} .. max"),
            )),
        ),
        MockSchema(
            base_uri, '/then',
            Constrained(Number(), (
                Range.yang(f"min .. {spec['then']['maximum']}"),
            )),
        ),
        MockSchema(
            base_uri, '/else',
            Any(),
        ),
    ))
    accept = (
        4,
        -8,
        1,
    )
    reject = (
        10,
    )

class TestIfThen(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator if/then"""
    validation = Conditional
    spec = {
        'if': {
            'type': 'number',
            'minimum': 3,
        },
        'then': {
            'type': 'number',
            'maximum': 9,
        },
    }
    base_uri = 'test://if-then/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(
            base_uri, '/if',
            Constrained(Number(), (
                Range.yang(f"{spec['if']['minimum']} .. max"),
            )),
        ),
        MockSchema(
            base_uri, '/then',
            Constrained(Number(), (
                Range.yang(f"min .. {spec['then']['maximum']}"),
            )),
        ),
    ))
    accept = (
        4,
        -8,
        1,
    )
    reject = (
        10,
    )

class TestIfElse(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator if/else"""
    validation = Conditional
    spec = {
        'if': {
            'type': 'number',
            'minimum': 3,
        },
        'else': {
            'type': 'number',
            'maximum': -7,
        },
    }
    base_uri = 'test://if-else/'
    root = MockRoot(base_uri, subschemas=(
        MockSchema(
            base_uri, '/if',
            Constrained(Number(), (
                Range.yang(f"{spec['if']['minimum']} .. max"),
            )),
        ),
        MockSchema(
            base_uri, '/else',
            Constrained(Number(), (
                Range.yang(f"min .. {spec['else']['maximum']}"),
            )),
        ),
    ))
    accept = (
        4,
        -8,
        10,
    )
    reject = (
        1,
    )

class TestThenElse(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator then/else"""
    validation = Conditional
    spec = {
        'then': {
            'type': 'number',
            'maximum': 9,
        },
        'else': {
            'type': 'number',
            'maximum': -7,
        },
    }
    base_uri = 'test://then-else/'
    root = MockRoot(base_uri)
    accept = ()
    reject = ()
    def test_optimised_out(self):
        """Test rsk_mt.jsonschema.validators.conditional.Conditional then/else"""
        self.assertEqual(self.validator, None) # pylint: disable=no-member

class TestThen(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator then"""
    validation = Conditional
    spec = {
        'then': {
            'type': 'number',
            'maximum': 9,
        },
    }
    base_uri = 'test://then/'
    root = MockRoot(base_uri)
    accept = ()
    reject = ()
    def test_optimised_out(self):
        """Test rsk_mt.jsonschema.validators.conditional.Conditional then"""
        self.assertEqual(self.validator, None) # pylint: disable=no-member

class TestElse(TestCase, metaclass=ValidatorTestBuilder):
    """Test JSON Schema validator else"""
    validation = Conditional
    spec = {
        'else': {
            'type': 'number',
            'maximum': -7,
        },
    }
    base_uri = 'test://else/'
    root = MockRoot(base_uri)
    accept = ()
    reject = ()
    def test_optimised_out(self):
        """Test rsk_mt.jsonschema.validators.conditional.Conditional else"""
        self.assertEqual(self.validator, None) # pylint: disable=no-member
