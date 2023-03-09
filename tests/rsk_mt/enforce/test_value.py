### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for rsk_mt.enforce.value."""

import json
from decimal import Decimal

from unittest import TestCase
from nose2.tools import params

from rsk_mt.enforce.value import (
    ValueType,
    Any, Null, Boolean, Integer, Number, String,
    Sequence, SequenceOf, Mapping, MappingOf,
    Enum, Constrained, Choice,
)
from rsk_mt.enforce.encoding import (
    ValueTypeEncoder,
    Json,
)

from .. import (
    make_fqname,
    make_params_values,
    make_values_not_in,
)

class _ValueTypeTestBuilder(type):
    """Build tests for rsk_mt.enforce.value.ValueType implementations.

    Specify this class as metaclass and provide:
    `value_type` - the ValueType under test
    `constructor` - a callable returning a ValueType instance
    `check_success` - an iterable of values for check success
    `call_success` - an iterable of values for __call__ success
    `cast_success` - an iterable of (lexical, canonical) pairs for cast success
    `encode_overrides` - an iterable of (value, override) pairs for encode
    `decode_overrides` - an iterable of (value, override) pairs for decode

    By default, this class expects :attr:`test_values` to fail or error. The
    concrete test class must include each value it supports in the corresponding
    *_success attribute.
    """
    # commonly serializable stock test values
    test_values = (
        None,
        False, True,
        -123, 0, 789,
        -0.5, 0.0, 0.5,
        "", "a string",
        (), (1, 2, 3),
        [], [4, 5, 6],
        {}, {"abc": 789},
    )
    def __new__(mcs, name, bases, dct):
        value_type = dct['value_type']
        fqname = make_fqname(value_type)
        # get values for testing
        constructor = dct['constructor']
        check_success = dct.get('check_success', ())
        call_success = dct.get('call_success', ())
        cast_success = dct.get('cast_success', ())
        encode_overrides = dct.get('encode_overrides', ())
        decode_overrides = dct.get('decode_overrides', ())
        # derived values for testing
        check_not_success = make_values_not_in(mcs.test_values, check_success)
        call_error = make_values_not_in(mcs.test_values, call_success)
        cast_error = make_values_not_in(mcs.test_values, call_success + tuple(
            pair[0] for pair in cast_success
        ))
        # build out class for testing `constructor`
        dct.update({
            'test_check_success': mcs.make_test_check_success(
                constructor, fqname,
                make_params_values(check_success),
            ),
            'test_check_not_success': mcs.make_test_check_not_success(
                constructor, fqname,
                make_params_values(check_not_success),
            ),
            'test_call_success': mcs.make_test_call_success(
                constructor, fqname,
                make_params_values(call_success),
            ),
            'test_call_error': mcs.make_test_call_error(
                constructor, fqname,
                make_params_values(call_error),
            ),
            'test_cast_canonical': mcs.make_test_cast_canonical(
                constructor, fqname,
                make_params_values(call_success),
            ),
            'test_cast_lexical': mcs.make_test_cast_lexical(
                constructor, fqname,
                make_params_values(cast_success),
            ),
            'test_cast_error': mcs.make_test_cast_error(
                constructor, fqname,
                make_params_values(cast_error),
            ),
            'expect_encoded': mcs.make_expect(encode_overrides),
            'expect_decoded': mcs.make_expect(decode_overrides),
            'test_json_encode_error': mcs.make_test_json_encode_error(
                constructor, fqname,
                make_params_values(call_error),
            ),
            'test_json_encode_canonical': mcs.make_test_json_encode_canonical(
                constructor, fqname,
                make_params_values(call_success),
            ),
            'test_json_decode_canonical': mcs.make_test_json_decode_canonical(
                constructor, fqname,
                make_params_values(call_success),
            ),
            'test_json_encode_lexical': mcs.make_test_json_encode_lexical(
                constructor, fqname,
                make_params_values(cast_success),
            ),
            'test_json_decode_lexical': mcs.make_test_json_decode_lexical(
                constructor, fqname,
                make_params_values(cast_success),
            ),
        })
        return super().__new__(mcs, name, bases, dct)
    # make helpers
    @staticmethod
    def make_expect(overrides):
        """Make a function selecting an override or default value."""
        @staticmethod
        def method(value):
            """Return `value` but prefer an override for `value`."""
            for pair in overrides:
                if pair[0] == value:
                    return pair[1]
            return value
        return method
    # make functions for use as TestCase methods
    @staticmethod
    def make_test_check_success(constructor, fqname, values):
        """Make a function testing for check success."""
        @params(*values)
        def method(self, value):
            """Test check success."""
            self.assertEqual(constructor().check(value), True)
        method.__doc__ = f'Test {fqname} check success'
        return method
    @staticmethod
    def make_test_check_not_success(constructor, fqname, values):
        """Make a function testing for check 'not success'."""
        @params(*values)
        def method(self, value):
            """Test check not success."""
            self.assertIn(constructor().check(value), (False, None))
        method.__doc__ = f'Test {fqname} check not success'
        return method
    @staticmethod
    def make_test_call_success(constructor, fqname, values):
        """Make a function testing for call success."""
        @params(*values)
        def method(self, value):
            """Test call success."""
            self.assertEqual(constructor()(value), value)
        method.__doc__ = f'Test {fqname} call success'
        return method
    @staticmethod
    def make_test_call_error(constructor, fqname, values):
        """Make a function testing for call error."""
        @params(*values)
        def method(self, value):
            """Test call error."""
            self.assertRaises((TypeError, ValueError), constructor(), value)
        method.__doc__ = f'Test {fqname} call error'
        return method
    @staticmethod
    def make_test_cast_canonical(constructor, fqname, values):
        """Make a function testing for cast canonical success."""
        @params(*values)
        def method(self, value):
            """Test cast canonical success."""
            self.assertEqual(constructor().cast(value), value)
        method.__doc__ = f'Test {fqname} cast canonical'
        return method
    @staticmethod
    def make_test_cast_lexical(constructor, fqname, pairs):
        """Make a function testing for cast lexical success."""
        @params(*pairs)
        def method(self, lexical, canonical):
            """Test cast lexical success."""
            self.assertEqual(constructor().cast(lexical), canonical)
        method.__doc__ = f'Test {fqname} cast lexical'
        return method
    @staticmethod
    def make_test_cast_error(constructor, fqname, values):
        """Make a function testing for cast error."""
        @params(*values)
        def method(self, value):
            """Test cast error."""
            self.assertRaises(
                (TypeError, ValueError),
                constructor().cast,
                value,
            )
        method.__doc__ = f'Test {fqname} cast error'
        return method
    @staticmethod
    def make_test_json_encode_error(constructor, fqname, values):
        """Make a function testing for JSON encode error."""
        @params(*values)
        def method(self, value):
            """Test JSON encode error."""
            value_type = constructor()
            serializers = tuple(value_type.outcasts())
            encoder = ValueTypeEncoder(Json(serializers), value_type)
            self.assertRaises((TypeError, ValueError), encoder.encode, value)
        method.__doc__ = f'Test {fqname} JSON encode error'
        return method
    @staticmethod
    def make_test_json_encode_canonical(constructor, fqname, values):
        """Make a function testing for JSON encode canonical success."""
        @params(*values)
        def method(self, value):
            """Test JSON encode canonical success."""
            value_type = constructor()
            serializers = tuple(value_type.outcasts())
            encoder = ValueTypeEncoder(Json(serializers), value_type)
            self.assertEqual(
                json.loads(encoder.encode(value)),
                self.expect_encoded(value),
            )
        method.__doc__ = f'Test {fqname} JSON encode canonical'
        return method
    @staticmethod
    def make_test_json_decode_canonical(constructor, fqname, values):
        """Make a function testing for JSON decode canonical success."""
        @params(*values)
        def method(self, value):
            """Test JSON decode canonical success."""
            value_type = constructor()
            serializers = tuple(value_type.outcasts())
            encoder = ValueTypeEncoder(Json(serializers), value_type)
            self.assertEqual(
                encoder.decode(encoder.encode(value)),
                self.expect_decoded(value),
            )
        method.__doc__ = f'Test {fqname} JSON decode canonical'
        return method
    @staticmethod
    def make_test_json_encode_lexical(constructor, fqname, pairs):
        """Make a function testing for JSON encode lexical success."""
        @params(*pairs)
        def method(self, lexical, canonical):
            """Test JSON encode lexical success."""
            value_type = constructor()
            serializers = tuple(value_type.outcasts())
            encoder = ValueTypeEncoder(Json(serializers), value_type)
            self.assertEqual(
                json.loads(encoder.encode(lexical)),
                self.expect_encoded(canonical),
            )
        method.__doc__ = f'Test {fqname} JSON encode lexical'
        return method
    @staticmethod
    def make_test_json_decode_lexical(constructor, fqname, pairs):
        """Make a function testing for JSON decode lexical success."""
        @params(*pairs)
        def method(self, lexical, canonical):
            """Test JSON decode lexical success."""
            value_type = constructor()
            serializers = tuple(value_type.outcasts())
            encoder = ValueTypeEncoder(Json(serializers), value_type)
            self.assertEqual(
                encoder.decode(encoder.encode(lexical)),
                self.expect_decoded(canonical),
            )
        method.__doc__ = f'Test {fqname} JSON decode lexical'
        return method

class TestValueType(TestCase, metaclass=_ValueTypeTestBuilder):
    """Tests for rsk_mt.enforce.value.ValueType."""
    value_type = constructor = ValueType

class TestAny(TestCase, metaclass=_ValueTypeTestBuilder):
    """Tests for rsk_mt.enforce.value.Any."""
    value_type = constructor = Any
    check_success = call_success = _ValueTypeTestBuilder.test_values
    encode_overrides = decode_overrides = (
        ((), []),
        ((1, 2, 3), [1, 2, 3]),
    )

class TestNull(TestCase, metaclass=_ValueTypeTestBuilder):
    """Tests for rsk_mt.enforce.value.Null."""
    value_type = constructor = Null
    check_success = call_success = (
        None,
    )

class TestBoolean(TestCase, metaclass=_ValueTypeTestBuilder):
    """Tests for rsk_mt.enforce.value.Boolean."""
    value_type = constructor = Boolean
    check_success = call_success = (
        False, True,
    )

class TestInteger(TestCase, metaclass=_ValueTypeTestBuilder):
    """Tests for rsk_mt.enforce.value.Integer."""
    value_type = constructor = Integer
    check_success = call_success = (
        -123, 0, 789,
    )

class TestNumber(TestCase, metaclass=_ValueTypeTestBuilder):
    """Tests for rsk_mt.enforce.value.Number."""
    value_type = constructor = Number
    check_success = call_success = (
        -123, 0, 789,
        -0.5, 0.0, 0.5,
        Decimal('0.01'), Decimal(), Decimal('9.99'),
    )
    encode_overrides = decode_overrides = (
        (Decimal('0.01'), 0.01),
        (Decimal('9.99'), 9.99),
    )

class TestString(TestCase, metaclass=_ValueTypeTestBuilder):
    """Tests for rsk_mt.enforce.value.String."""
    value_type = constructor = String
    check_success = call_success = (
        "", "a string",
    )

class TestSequence(TestCase, metaclass=_ValueTypeTestBuilder):
    """Tests for rsk_mt.enforce.value.Sequence."""
    value_type = constructor = Sequence
    check_success = call_success = (
        (), (1, 2, 3),
        [], [4, 5, 6],
    )
    encode_overrides = decode_overrides = (
        ((), []),
        ((1, 2, 3), [1, 2, 3]),
    )

class TestSequenceOf(TestCase, metaclass=_ValueTypeTestBuilder):
    """Tests for rsk_mt.enforce.value.SequenceOf."""
    value_type = SequenceOf
    constructor = lambda: SequenceOf(Boolean())
    call_success = (
        (), (True, False),
        [], [False, False, False],
    )
    check_success = call_success + (
        (1, 2, 3),
        [4, 5, 6],
    )
    encode_overrides = decode_overrides = (
        ((), []),
        ((True, False), [True, False]),
        ((1, 2, 3), [1, 2, 3]),
    )

class TestMapping(TestCase, metaclass=_ValueTypeTestBuilder):
    """Tests for rsk_mt.enforce.value.Mapping."""
    value_type = constructor = Mapping
    check_success = call_success = (
        {}, {"abc": 789},
    )

class TestMappingOf(TestCase, metaclass=_ValueTypeTestBuilder):
    """Tests for rsk_mt.enforce.value.MappingOf."""
    value_type = MappingOf
    constructor = lambda: MappingOf({'abc': Boolean()}, {'def': Integer()})
    call_success = (
        {"abc": False}, {"abc": True, "def": 77},
    )
    check_success = call_success + (
        {}, {"abc": 789},
    )

class TestEnum(TestCase, metaclass=_ValueTypeTestBuilder):
    """Tests for rsk_mt.enforce.value.Enum."""
    value_type = Enum
    constructor = lambda: Enum([True, -7, 'foo'])
    call_success = (
        True, -7, "foo",
    )
    check_success = call_success + (
        False,
        -123, 0, 789,
        "", "a string",
    )

class TestConstrained(TestCase, metaclass=_ValueTypeTestBuilder):
    """Tests for rsk_mt.enforce.value.Constrained."""
    value_type = Constrained
    constructor = lambda: Constrained(Integer(), (lambda v: v > 0,))
    call_success = (
        789,
    )
    check_success = call_success + (
        -123, 0,
    )

class TestChoice(TestCase, metaclass=_ValueTypeTestBuilder):
    """Tests for rsk_mt.enforce.value.Choice."""
    value_type = Choice
    constructor = lambda: Choice([Integer(), Mapping()])
    check_success = call_success = (
        -123, 0, 789,
        {}, {"abc": 789},
    )
