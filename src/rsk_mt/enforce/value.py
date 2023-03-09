### SPDX-License-Identifier: GPL-2.0-or-later

"""Enforcement of value types."""

from decimal import Decimal

class ValueType():
    """A base class for value types.

    A value type provides a restriction on the type and value of acceptable
    values within some context. A value type is defined as a set of values,
    the canonical values of the value type. Each canonical value is a single
    Python value of fixed type.

    A value type may define alternative representations for each canonical
    value. The complete set of values which map to the canonical values is
    termed the lexical values of the value type. The set of lexical values
    is the canonical values and their alternative representations (the union
    of two sets which are disjoint sets by definition). By default a value
    type has no alternative representations.

    A value type may define :meth:`outcasts` to help handle canonical values
    which are not commonly serializable. (Any value which cannot be directly
    encoded by :func:`json.dumps` is considered not commonly serializable.)
    """
    def check(self, val): # pylint: disable=unused-argument,no-self-use
        """Check if the type of `val` is acceptable for a canonical value.

        Return True if the type of `val`, but not necessarily the value of
        `val`, is acceptable for a canonical value. Return False if the type of
        `val` is definitely not acceptable. Return None to defer the decision to
        this instance's `__call__` method.
        """
        return None
    def __call__(self, val):
        """Enforce the canonical values on `val`.

        If `val` is a canonical value, then return `val` or a value that has an
        equal value. Raise :class:`TypeError` or :class:`ValueError` otherwise.
        """
        if self.check(val):
            return val
        raise TypeError(val)
    def cast(self, val):
        """Map lexical value `val` to a canonical value.

        Return the canonical value to which lexical value `val` maps. Raise
        :class:`TypeError` or :class:`ValueError` if `val` does not map to a
        canonical value.
        """
        return self(val)
    def outcasts(self): # pylint: disable=no-self-use
        """Return outcasts to enable conversion to commonly serializable values.

        Return an iterable of 2-tuples, (type, outcast), where `outcast` is a
        function which returns a commonly serializable value given a value of
        `type`. Note that `outcast` is not required to check whether a value it
        is passed is a canonical or lexical value of this value type.
        """
        return ()

class Any(ValueType):
    """A value type accepting any value.

    All values are canonical values of this value type.
    """
    def check(self, val):
        return True

class Null(ValueType):
    """A value type accepting null values.

    The sole canonical value is None.
    """
    def check(self, val):
        return val is None
    def __call__(self, val):
        if val is None:
            return val
        raise ValueError(val)

class Boolean(ValueType):
    """A value type accepting boolean values.

    The set of canonical values is all booleans.
    """
    def check(self, val):
        return isinstance(val, bool)

class Integer(ValueType):
    """A value type accepting integer values.

    The set of canonical values is all integers.
    """
    def check(self, val):
        return isinstance(val, int) and not isinstance(val, bool)

class Number(ValueType):
    """A value type accepting numeric values.

    The set of canonical values is all numbers.
    """
    numeric_types = (Decimal, float, int)
    def check(self, val):
        return isinstance(val, self.numeric_types) and not isinstance(val, bool)
    def outcasts(self):
        return ((Decimal, float),)

class String(ValueType):
    """A value type accepting string values.

    The set of canonical values is all strings.
    """
    def check(self, val):
        return isinstance(val, str)

class Sequence(ValueType):
    """A value type accepting sequence values.

    The set of canonical values is all list values and all tuple values.
    """
    def check(self, val):
        return isinstance(val, (list, tuple))

class SequenceOf(Sequence):
    """A value type accepting sequence values whose items are of `value_type`.

    The set of canonical values is all empty sequence values and all non-empty
    sequence values whose items are of `value_type`.
    """
    def __init__(self, value_type):
        super().__init__()
        self._value_type = value_type
    def __call__(self, val):
        val = super().__call__(val)
        for item in val:
            self._value_type(item)
        return val
    def outcasts(self):
        return self._value_type.outcasts()

class Mapping(ValueType):
    """A value type accepting mapping values.

    The set of canonical values is all dict values.
    """
    def check(self, val):
        return isinstance(val, dict)

class MappingOf(Mapping):
    """A value type accepting conforming mapping values.

    The set of canonical values is defined by `mandatory` and `optional`, which
    are both expected to be mappings of keys to value types. A canonical value
    must have a value at each key in `mandatory` and may have a value at each
    key in `optional`. The value at each key must conform to the corresponding
    value type in `mandatory` or `optional`. If the same key is specified in
    both `mandatory` and `optional` then the value type in `mandatory` is used.
    """
    def __init__(self, mandatory=(), optional=()):
        super().__init__()
        mandatory = dict(mandatory)
        optional = dict(optional)
        self._mandatory_keys = frozenset(mandatory)
        self._permitted_keys = frozenset(set(mandatory).union(set(optional)))
        self._value_types = optional
        self._value_types.update(mandatory)
    def check(self, val):
        return isinstance(val, dict)
    def __call__(self, val):
        val = super().__call__(val)
        supplied_keys = frozenset(val)
        missing_keys = self._mandatory_keys - supplied_keys
        unexpected_keys = supplied_keys - self._permitted_keys
        if not missing_keys and not unexpected_keys:
            for key in val:
                self._value_types[key](val[key])
            return val
        raise ValueError(val)
    def outcasts(self):
        for value_type in self._value_types.values():
            yield from value_type.outcasts()

# complex value types

class Enum(ValueType):
    """A value type accepting only values in iterable `accept`.

    The set of canonical values is the values in `accept`.
    """
    def __init__(self, accept=(), outcasts=()):
        super().__init__()
        self._canonical = tuple(accept)
        self._outcasts = outcasts
    @property
    def canonical(self):
        """A tuple of the canonical values."""
        return self._canonical
    def check(self, val):
        return any(isinstance(val, cval.__class__) for cval in self.canonical)
    def __call__(self, val):
        if val in self.canonical:
            return val
        raise ValueError(val)
    def outcasts(self):
        return self._outcasts

class Constrained(ValueType):
    """A value type accepting values of `value_type` with `constraints`."""
    def __init__(self, value_type, constraints=()):
        super().__init__()
        self._value_type = value_type
        self._constraints = tuple(constraints)
    def outcasts(self):
        return self._value_type.outcasts()
    def check(self, val):
        return self._value_type.check(val)
    def __call__(self, val):
        val = self._value_type(val)
        for constraint in self._constraints:
            if not constraint(val):
                raise ValueError(val)
        return val
    def cast(self, val):
        val = self._value_type.cast(val)
        return self(val)

class Choice(ValueType):
    """A value type accepting values of a choice from `value_types`.

    The set of canonical values is the union of the canonical values of the
    `value_types`.
    """
    def __init__(self, value_types=()):
        super().__init__()
        self._value_types = tuple(value_types)
    def check(self, val):
        return any(value_type.check(val) for value_type in self._value_types)
    def __call__(self, val):
        for value_type in self._value_types:
            try:
                return value_type(val)
            except (TypeError, ValueError):
                pass
        raise ValueError(val)
    def cast(self, val):
        for value_type in self._value_types:
            try:
                return value_type.cast(val)
            except (TypeError, ValueError):
                pass
        raise ValueError(val)
    def outcasts(self):
        for value_type in self._value_types:
            yield from value_type.outcasts()
