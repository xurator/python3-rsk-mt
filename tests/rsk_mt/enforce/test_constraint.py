### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for rsk_mt.enforce.constraint."""

from sys import maxsize

from unittest import TestCase
from nose2.tools import params

from rsk_mt.enforce.constraint import (
    parse_yang_range,
    Constraint,
    Length,
    Range,
    Pattern,
)

from .. import (
    make_fqname,
    make_params_values,
    make_params_pairs,
)

# arbitrary test values
_MIN = -7
_MAX = 243

class TestParseYangRange(TestCase):
    """Tests for rsk_mt.enforce.constraint.parse_yang_range."""
    @staticmethod
    def parse(string):
        """Parse YANG range from `string`."""
        return parse_yang_range(string, _MIN, _MAX)
    @params(
        '',
        'bad',
        '..',
        ' 3..',
        '.. 4',
        '0 .. 4 .. 5',
        '|',
        '|..',
    )
    def test_parse_error(self, string):
        """Test rsk_mt.enforce.constraint.parse_yang_range parse error"""
        self.assertRaises(ValueError, self.parse, string)
    @params(
        ### single fixed bound
        ('-99', [[-99]]),
        ('0', [[0]]),
        ('56', [[56]]),
        ('min', [[_MIN]]),
        ('max', [[_MAX]]),
        ### single range bound
        ('min .. max', [[_MIN, _MAX]]),
        ('min .. -98', [[_MIN, -98]]),
        ('min .. 0', [[_MIN, 0]]),
        ('min .. 57', [[_MIN, 57]]),
        ('-97 .. max', [[-97, _MAX]]),
        ('0 .. max', [[0, _MAX]]),
        ('58 .. max', [[58, _MAX]]),
        ('-96 .. 59', [[-96, 59]]),
        ### complex bounds
        ('min .. -95 | 27 | 60 .. max', [[_MIN, -95], [27], [60, _MAX]]),
        ('-0x0A .. 0o13', [[-10, 11]]),
    )
    def test_parse_success(self, input_, output):
        """Test rsk_mt.enforce.constraint.parse_yang_range parse success"""
        self.assertEqual(self.parse(input_), output)

class TestConstraint(TestCase):
    """Tests for rsk_mt.enforce.constraint.Constraint."""
    def test_abstract(self):
        """Test rsk_mt.enforce.constraint.Constraint is abstract"""
        self.assertRaises(NotImplementedError, Constraint(), 'any value')

class _ConstraintTestBuilder(type):
    """Build tests for rsk_mt.enforce.constraint.Constraint implementations.

    Specify this class as metaclass and provide:
    `constructor` - a callable returning a Constraint instance
    `construct_error` - an iterable of values `constructor` must reject
    `call_failure` - an iterable of (arg, values) pairs for call failure
    `call_success` - an iterable of (arg, values) pairs for call success

    For call failure (or success), a Constraint instance created with `arg` must
    fail (or pass) each value in `values`.
    """
    def __new__(mcs, name, bases, dct):
        constructor = dct['constructor']
        fqname = make_fqname(constructor)
        # build out class for testing `constructor`
        dct.update({
            'test_construct_error': mcs.make_test_construct_error(
                constructor, fqname,
                make_params_values(dct['construct_error']),
            ),
            'test_call_failure': mcs.make_test_call(
                constructor, fqname,
                make_params_pairs(dct['call_failure']),
                False,
            ),
            'test_call_success': mcs.make_test_call(
                constructor, fqname,
                make_params_pairs(dct['call_success']),
                True,
            ),
        })
        return super().__new__(mcs, name, bases, dct)
    # make functions for use as TestCase methods
    @staticmethod
    def make_test_construct_error(constructor, fqname, values):
        """Make a function testing for expected construct errors."""
        @params(*values)
        def method(self, value):
            """Test constructor error."""
            self.assertRaises((TypeError, ValueError), constructor, value)
        method.__doc__ = f'Test {fqname} construct error'
        return method
    @staticmethod
    def make_test_call(constructor, fqname, pairs, expect):
        """Make a function testing for expected call results."""
        @params(*pairs)
        def method(self, arg, value):
            """Test call gives result `expect`"""
            self.assertEqual(constructor(arg)(value), expect)
        method.__doc__ = f'Test {fqname} call gives result {expect}'
        return method

class TestLength(TestCase, metaclass=_ConstraintTestBuilder):
    """Tests for rsk_mt.enforce.constraint.Length."""
    constructor = Length
    construct_error = (
        None, False, True, 1, -2.4, (), [], {},
    )
    call_failure = (
        ([[0]], (None, False, True, 1, -2.4, 'f', (1,), [None], {'a': 'b'})),
        ([[0, 1]], ('fo', (2, 3), [None, False], {'c': 'd', 'e': 'f'})),
        ([[0, 1], [3]], ('quux', (6, 7, 8, 9), [0, 0, 0, 0], {0: 1, 2: 3})),
        ([[0, 1], [3, maxsize]], ('ba', (4, 5), [True, None], {1: 2, 3: 4})),
    )
    call_success = (
        ([[0]], ('', (), [], {})),
        ([[0, 1]], ('', 'f', (), (2,), [], [None], {}, {'c': 'd'})),
        ([[0, 1], [3]], ('baz', (7, 8, 9), [0, 0, 0], {0: 1, 2: 3, 4: 5})),
        ([[0, 1], [3, maxsize]], (
            'bar', 'quux',
            (4, 5, 6), (7, 8, 9, 10, 11),
            [False, False, False], [None, None, None, None, None, None, None],
            {'g': 'h', 'i': 'j', 'k': 'l'},
        )),
    )

class TestLengthYang(TestCase, metaclass=_ConstraintTestBuilder):
    """Tests for rsk_mt.enforce.constraint.Length.yang."""
    constructor = Length.yang
    construct_error = TestLength.construct_error
    call_failure = (
        ('0', TestLength.call_failure[0][1]),
        ('min', TestLength.call_failure[0][1]),
        ('min..1', TestLength.call_failure[1][1]),
        ('min.. 1 | 3', TestLength.call_failure[2][1]),
        ('0 .. 1 | 3.. max', TestLength.call_failure[3][1]),
    )
    call_success = (
        ('0', TestLength.call_success[0][1]),
        ('min', TestLength.call_success[0][1]),
        ('min..1', TestLength.call_success[1][1]),
        ('min.. 1 | 3', TestLength.call_success[2][1]),
        ('0 .. 1 | 3.. max', TestLength.call_success[3][1]),
    )

class TestRange(TestCase, metaclass=_ConstraintTestBuilder):
    """Tests for rsk_mt.enforce.constraint.Range."""
    constructor = Range
    construct_error = (
        None, False, True, 1, -2.4, (), [], {},
    )
    call_failure = (
        ([[1]], (None, 'foo', (1,), [-3.4], {7: 8})),
        ([[-1 - maxsize]], ((-1 - maxsize) + 1, maxsize)),
        ([[-10, 0]], (-11, 1)),
        ([[0]], (-1, 0x1, 0o1)),
        ([[0, 10]], (-1, 11, 0x0B, 0o13)),
        ([[0, 10], [12, 20]], (-1, 11, 21, 0x0B, 0x15, 0o13, 0o25)),
        ([[maxsize]], (-1 - maxsize, maxsize - 1)),
    )
    call_success = (
        ([[-1 - maxsize]], (-1 - maxsize,)),
        ([[-10, 0]], (-10, -9, -1, 0)),
        ([[0]], (0, 0x0, 0o0)),
        ([[0, 10]], (0, 1, 9, 10, 0x0, 0x01, 0x09, 0x0A, 0o0, 0o1, 0o11, 0o12)),
        ([[0, 10], [12, 20]], (
            12, 0xC, 0o14, 13, 0xD, 0o15, 19, 0x13, 0o23, 20, 0x14, 0o24,
        )),
        ([[maxsize]], (maxsize,)),
    )

class TestRangeYang(TestCase, metaclass=_ConstraintTestBuilder):
    """Tests for classmethod rsk_mt.enforce.constraint.Range.yang."""
    constructor = Range.yang
    construct_error = TestRange.construct_error
    call_failure = (
        ('1', TestRange.call_failure[0][1]),
        ('min', TestRange.call_failure[1][1]),
        ('-10..0', TestRange.call_failure[2][1]),
        ('0', TestRange.call_failure[3][1]),
        ('0 .. 10', TestRange.call_failure[4][1]),
        ('0..10 | 12 ..20', TestRange.call_failure[5][1]),
        ('max', TestRange.call_failure[6][1]),
    )
    call_success = (
        ('min', TestRange.call_success[0][1]),
        ('-10..0', TestRange.call_success[1][1]),
        ('0', TestRange.call_success[2][1]),
        ('0 .. 10', TestRange.call_success[3][1]),
        ('0..10 | 12 ..20', TestRange.call_success[4][1]),
        ('max', TestRange.call_success[5][1]),
    )

class TestPattern(TestCase, metaclass=_ConstraintTestBuilder):
    """Tests for rsk_mt.enforce.constraint.Pattern."""
    constructor = Pattern
    construct_error = (
        None, False, True, 1, -2.4, (), [], {},
    )
    call_failure = (
        ('abc', (None, False, True, 1, -2.4, (), [], {})),
        ('abc', ('ab', 'bc', 'def')),
        ('^bar', ('baz', 'foobar')),
        ('baz$', ('bar', 'bazquux')),
    )
    call_success = (
        ('abc', ('abc', 'abcd', 'dabc')),
        ('^bar', ('bar', 'barbaz')),
        ('baz$', ('baz', 'barbaz')),
    )
