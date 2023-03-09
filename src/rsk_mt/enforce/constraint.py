### SPDX-License-Identifier: GPL-2.0-or-later

"""Enforcement of value constraints."""

from sys import maxsize
import re

def test_ge(reference):
    """Return a function testing for greater than or equal to `reference`."""
    return lambda val: reference <= val

def test_le(reference):
    """Return a function testing for less than or equal to `reference`."""
    return lambda val: val <= reference

def test_and(constraint_a, constraint_b):
    """Return a function testing for `constraint_a` and `constraint_b`."""
    return lambda val: constraint_a(val) and constraint_b(val)

def test_or(constraint_a, constraint_b):
    """Return a function testing for `constraint_a` or `constraint_b`."""
    return lambda val: constraint_a(val) or constraint_b(val)

def test_pattern(regexp):
    """Return a function testing for implicitly unanchored `regexp` match."""
    return lambda val: regexp.search(val) is not None

def parse_yang_range(spec, min_, max_):
    """Parse `spec`, a YANG range specification.

    Parse `spec`, a YANG `RFC 6020 <https://tools.ietf.org/html/rfc6020>`_ range
    specification (section 9.2.4), into a list of lists, where each nested list
    contains either a single fixed bound or a pair of bounds defining a range,
    and each bound is an integer. A bound may be encoded in `spec` as an integer
    (using any base representation that Python accepts), string 'min' or string
    'max'. A bound has value `min_` when specified as string 'min' and value
    `max_` when specified as string 'max'.
    """
    def parse_int(val):
        """Return an integer from `val`."""
        try:
            return int(val, base=0)
        except TypeError:
            return int(val)
    def parse_bound(string):
        """Return an integer bound parsed from `string`."""
        try:
            return parse_int(string)
        except (TypeError, ValueError):
            if string == 'min':
                return parse_int(min_)
            if string == 'max':
                return parse_int(max_)
        raise ValueError(f'failed to parse YANG range bound from {string}')
    def parse_range(string):
        """Return a list with a single bound or pair of bounds from `string`."""
        return [parse_bound(_.strip()) for _ in string.split('..', 1)]
    try:
        return [parse_range(_.strip()) for _ in spec.split('|')]
    except AttributeError:
        raise TypeError(spec) from None

class Constraint():
    """A(n abstract) base class for value constraints.

    A constraint provides a restriction on the range of acceptable values within
    some context. A constraint is defined as a boolean function: values which
    map to True pass the constraint; values which map to False do not. Defining
    a constraint as a boolean function allows complex constraints to be built as
    logical decision trees.
    """
    def __call__(self, val):
        """Return True if `val` passes this constraint, False otherwise."""
        raise NotImplementedError

class Length(Constraint):
    """A value length constraint.

    A constraint passing values with acceptable length as defined by `accept`.
    Each item in iterable `accept` must be an iterable of 1 integer (a value
    length to pass) or an iterable of 2 integers (an inclusive range of value
    lengths to pass). (If `accept` has any other value structure, then the
    behaviour is undefined.)
    """
    def __init__(self, accept):
        super().__init__()
        self._test = None
        for item in accept:
            # use only numeric comparisons which
            # raise TypeError for non-numeric values
            try:
                (lower, upper) = item
            except ValueError:
                lower = upper = item[0]
            test = test_and(test_ge(lower), test_le(upper))
            self._test = test_or(self._test, test) if self._test else test
        if self._test is None:
            raise ValueError(accept)
    def __call__(self, val):
        try:
            return self._test(len(val))
        except TypeError:
            return False
    @classmethod
    def yang(cls, spec):
        """Return a length constraint from `spec`, a YANG range specification.

        Return an instance of `cls` enforcing a length constraint per `spec`, a
        YANG `RFC 6020 <https://tools.ietf.org/html/rfc6020>`_ range string for
        which 'min' means a value length of zero and 'max' means the maximum
        supported length on this platform.
        """
        return cls(parse_yang_range(spec, 0, maxsize))

class Range(Constraint):
    """A value range constraint.

    A constraint passing values with an acceptable numeric value as defined by
    `accept`. Each item in iterable `accept` must be an iterable of 1 number (a
    value to pass) or an iterable of 2 numbers (an inclusive range of values to
    pass). (If `accept` has any other value structure, then the behaviour is
    undefined.)
    """
    def __init__(self, accept):
        super().__init__()
        self._test = None
        for item in accept:
            # use only numeric comparisons which
            # raise TypeError for non-numeric values
            try:
                (lower, upper) = item
            except ValueError:
                lower = upper = item[0]
            test = test_and(test_ge(lower), test_le(upper))
            self._test = test_or(self._test, test) if self._test else test
        if self._test is None:
            raise ValueError(accept)
    def __call__(self, val):
        try:
            return self._test(val)
        except TypeError:
            return False
    @classmethod
    def yang(cls, spec):
        """Return a range constraint from `spec`, a YANG range specification.

        Return a instance of `cls` enforcing a range constraint per `spec`, a
        YANG `RFC 6020 <https://tools.ietf.org/html/rfc6020>`_ range string for
        which 'min' and 'max' mean the minimum and maximum supported integer
        values on this platform respectively.
        """
        return cls(parse_yang_range(spec, -1 - maxsize, maxsize))

class Pattern(Constraint):
    """A string pattern constraint.

    A constraint passing string values which match regular expression string
    `expr`, which is implicitly unanchored.
    """
    def __init__(self, expr):
        super().__init__()
        regexp = re.compile(expr)
        self._test = test_pattern(regexp)
    def __call__(self, val):
        try:
            return self._test(val)
        except TypeError:
            return False
