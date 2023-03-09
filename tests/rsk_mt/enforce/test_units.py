### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for rsk_mt.enforce.units."""

from random import randint
from decimal import Decimal

from unittest import TestCase
from nose2.tools import params

from rsk_mt.enforce.units import (
    Units,
    Weight,
    Energy,
)

from .. import make_fqname

class TestUnits(TestCase):
    """Tests for rsk_mt.enforce.units.Units."""
    def test_units_abstract(self):
        """Test rsk_mt.enforce.units.Units is an abstract class"""
        self.assertRaises(NotImplementedError, Units)

class _UnitsTestBuilder(type):
    """Build tests for rsk_mt.enforce.units.Units implementations.

    Specify this class as metaclass and provide:
    `constructor` - a callable returning a Units instance
    `conversions` - an iterable of 4-tuples to test conversions

    Each 4-tuple is (from value, from units, to value, to units)
    """
    def __new__(mcs, name, bases, dct):
        constructor = dct['constructor']
        fqname = make_fqname(constructor)
        # build out class for testing `constructor`
        dct.update({
            'test_unsupported': mcs.make_test_unsupported(
                constructor, fqname,
            ),
            'test_unsupported_default': mcs.make_test_unsupported_default(
                constructor, fqname,
            ),
            'test_restriction': mcs.make_test_restriction(
                constructor, fqname,
            ),
            'test_bad_convert': mcs.make_test_bad_convert(
                constructor, fqname,
            ),
            'test_null_convert': mcs.make_test_null_convert(
                constructor, fqname,
            ),
            'test_convert': mcs.make_test_convert(
                constructor, fqname,
                dct['conversions'],
            ),
        })
        return super().__new__(mcs, name, bases, dct)
    # make functions for use as TestCase methods
    @staticmethod
    def make_test_unsupported(constructor, fqname):
        """Make a function testing unsupported units are rejected."""
        def method(self):
            """Test `constructor` rejects unsupported units."""
            self.assertRaises(ValueError, constructor, only=('foo',))
            self.assertRaises(ValueError, constructor, default='bar')
        method.__doc__ = f'Test {fqname} rejects unsupported units'
        return method
    @staticmethod
    def make_test_unsupported_default(constructor, fqname):
        """Make a function testing unsupported default is rejected."""
        def method(self):
            """Test `constructor` rejects unsupported default units."""
            non_default_units = constructor.supported.canonical[1:]
            # restricting `only` in this way leaves default not in supported
            self.assertRaises(ValueError, constructor, only=non_default_units)
        method.__doc__ = f'Test {fqname} rejects unsupported default units'
        return method
    @staticmethod
    def make_test_restriction(constructor, fqname):
        """Make a function testing restriction of units."""
        def method(self):
            """Test `constructor` restriction of units."""
            supported = constructor.supported.canonical
            unrestricted = constructor()
            restricted = constructor(only=supported[1:], default=supported[-1])
            # `unrestricted` supports all units
            self.assertEqual(unrestricted.units, supported)
            # `unrestricted` uses first supported units as default units
            self.assertEqual(unrestricted.default_units, supported[0])
            # `unrestricted` accepts alternative default units
            self.assertEqual(
                constructor(default=supported[-1]).default_units,
                supported[-1],
            )
            # `restricted` uses only specified units
            self.assertEqual(restricted.units, supported[1:])
            # `restricted` accepts alternative default units
            self.assertEqual(restricted.default_units, supported[-1])
        method.__doc__ = f'Test {fqname} restriction of units'
        return method
    @staticmethod
    def make_test_bad_convert(constructor, fqname):
        """Make a function testing bad conversions are rejected."""
        def method(self):
            """Test `constructor` rejects bad conversions."""
            instance = constructor()
            # rejects conversion from unsupported units
            self.assertRaises(ValueError, instance.convert, 10, from_='foo')
            # rejects conversion to unsupported units
            self.assertRaises(ValueError, instance.convert, 10, to_='bar')
        method.__doc__ = f'Test {fqname} rejects bad conversions'
        return method
    @staticmethod
    def make_test_null_convert(constructor, fqname):
        """Make a function testing a random null conversion."""
        def method(self):
            """Test `constructor` with random null conversion."""
            rnd = randint(-10, 10)
            self.assertEqual(constructor().convert(rnd), rnd)
        method.__doc__ = f'Test {fqname} implements null conversion'
        return method
    @staticmethod
    def make_test_convert(constructor, fqname, required):
        """Make a function testing `required` conversions."""
        @params(*required)
        def method(self, f_val, f_units, t_val, t_units):
            """Test `constructor` with required conversions."""
            self.assertEqual(
                constructor().convert(f_val, from_=f_units, to_=t_units),
                t_val,
            )
            rounder = constructor(ndigits=3)
            self.assertEqual(
                rounder.convert(f_val, from_=f_units, to_=t_units),
                round(t_val, 3),
            )
        method.__doc__ = f'Test {fqname} implements required conversion'
        return method

class TestWeight(TestCase, metaclass=_UnitsTestBuilder):
    """Tests for rsk_mt.enforce.units.Weight."""
    constructor = Weight
    conversions = (
        ### specific null conversions
        (1, None, 1, 'kg'),
        (2, 'kg', 2, None),
        (3, 'kg', 3, 'kg'),
        (4, 'lb', 4, 'lb'),
        ### useful conversions
        (5, None, 5 * 2.20462, 'lb'),
        (6, 'kg', 6 * 2.20462, 'lb'),
        (7, 'lb', 7 / 2.20462, None),
        (8, 'lb', 8 / 2.20462, 'kg'),
    )

class TestEnergy(TestCase, metaclass=_UnitsTestBuilder):
    """Tests for rsk_mt.enforce.units.Energy."""
    constructor = Energy
    conversions = (
        ### specific null conversions
        (9000, None, 9000, 'J'),
        (Decimal(9000), None, Decimal(9000), 'J'),
        (8000, 'J', 8000, None),
        (Decimal(8000), 'J', Decimal(8000), None),
        (7000, 'J', 7000, 'J'),
        (Decimal(7000), 'J', Decimal(7000), 'J'),
        (6000, 'kcal', 6000, 'kcal'),
        (Decimal(6000), 'kcal', Decimal(6000), 'kcal'),
        ### useful conversions
        (5000, None, 5000 / 4190, 'kcal'),
        (Decimal(5000), None, Decimal(5000) / Decimal(4190), 'kcal'),
        (4000, 'J', 4000 / 4190, 'kcal'),
        (Decimal(4000), 'J', Decimal(4000) / Decimal(4190), 'kcal'),
        (3000, 'kWh', 3000 * 3600000, None),
        (Decimal(3000), 'kWh', Decimal(3000) * Decimal(3600000), None),
        (2e6, 'J', 2e6 / 3.6e6, 'kWh'),
        (Decimal(2e6), 'J', Decimal(2e6) / Decimal(3.6e6), 'kWh'),
    )
