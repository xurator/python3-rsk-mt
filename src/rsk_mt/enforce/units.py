### SPDX-License-Identifier: GPL-2.0-or-later

"""Enforcement of measurement units."""

from decimal import Decimal

from .value import Enum

class Units():
    """A(n abstract) base class for measurement units and conversions.

    A class deriving from this class must provide two class level attributes:

    Class attribute `supported` must provide an :class:`Enum` instance which
    declares supported units labels. The first label declares the default units.

    Class attribute `conversions` must provide a mapping hosting a function to
    convert between units for each supported conversion. Each key in
    `conversions` must be a label in `supported`. This label is the "from" units
    for the conversion (the units that the value to convert is supplied in). The
    corresponding value in `conversions` must be a mapping whose keys are also
    labels in `supported`. These are the "to" units for the conversion (the
    units that the value supplied must be converted to). The corresponding value
    in this inner mapping is a function taking a numeric value, the value to
    convert (in "from" units), and returning a numeric value, the converted
    value (in "to" units).

    Use keyword argument `only` to restrict the supported units.
    Use keyword argument `default` to specify the default units.
    Use keyword argument `ndigits` to :func:`round` converted values.
    """
    supported = Enum()
    conversions = {}
    def __init__(self, only=(), default=None, ndigits=None):
        if self.__class__ == Units:
            raise NotImplementedError
        if only:
            unsupported = frozenset(only) - frozenset(self.supported.canonical)
            if unsupported:
                raise ValueError(f'unsupported units: {", ".join(unsupported)}')
            supported_default = self.supported.canonical[0]
            if default is None and supported_default not in only:
                raise ValueError('new default units must be specified')
            units = Enum(only)
        else:
            units = self.supported
        default = default if default else units.canonical[0]
        try:
            units(default)
        except ValueError as err:
            raise ValueError(f'unsupported default units: {default}') from err
        self._units = units
        self._default = default
        self._ndigits = ndigits
    @property
    def units(self):
        """A tuple of supported units."""
        return self._units.canonical
    @property
    def default_units(self):
        """The default units."""
        return self._default
    def convert(self, val, from_=None, to_=None):
        """Convert `val` between `from_` and `to_` units.

        Both `from_` and `to_` treat :data:`None` as implying the default units.
        Always :func:`round` return values if configured to do so.
        """
        from_ = self._units(self.default_units if from_ is None else from_)
        to_ = self._units(self.default_units if to_ is None else to_)
        val = val if from_ == to_ else self.conversions[from_][to_](val)
        return val if self._ndigits is None else round(val, self._ndigits)
    @staticmethod
    def multiplier(const):
        """Return a function multiplying an input numeric value by `const`."""
        const_d = Decimal(const)
        def func(val):
            """Return `val` multiplied by `const`."""
            try:
                return val * const
            except TypeError:
                return val * const_d
        return func
    @staticmethod
    def divider(const):
        """Return a function dividing an input numeric value by `const`."""
        const_d = Decimal(const)
        def func(val):
            """Return `val` divided by `const`."""
            try:
                return val / const
            except TypeError:
                return val / const_d
        return func
    @classmethod
    def build(cls, clsname, relationships, default=None):
        """Build a derived class from specified units and conversions.

        Return a derived class named `clsname` providing supported units and
        conversions as specified by iterable `relationships`. Each item in
        `relationships` is a 3-tuple, (from units, to units, constant), where
        numeric constant is used to multiply a value presented in from units
        to get a value in to units. If `default` is None then use the first
        from units in `relationships` as the default units.
        """
        supported = []
        conversions = {}
        for (from_, to_, const) in relationships:
            if from_ not in supported:
                supported.append(from_)
            if to_ not in supported:
                supported.append(to_)
            try:
                conversions[from_][to_] = cls.multiplier(const)
            except KeyError:
                conversions[from_] = {to_: cls.multiplier(const)}
            try:
                conversions[to_][from_] = cls.divider(const)
            except KeyError:
                conversions[to_] = {from_: cls.divider(const)}
        if default is not None:
            supported.remove(default)
            supported.insert(0, default)
        return type(clsname, (cls,), {
            'supported': Enum(supported),
            'conversions': conversions,
        })

# pylint: disable=invalid-name

# some basic units for weight
Weight = Units.build('Weight', (
    ('kg', 'lb', 2.20462),
), default='kg')

# some basic units for energy
Energy = Units.build('Energy', (
    ('kcal', 'J', 4190),
    ('kWh', 'J', 3.6e6),
), default='J')
