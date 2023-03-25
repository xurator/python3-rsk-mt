### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for rsk_mt.enforce.encoding"""

import os
from decimal import Decimal

from unittest import TestCase

from rsk_mt.enforce.encoding import (
    Encoder,
    ValueTypeEncoder,
    Json,
    JsonDecimal,
)
from rsk_mt.enforce.value import (
    Constrained,
    Integer,
)
from rsk_mt.enforce.constraint import (
    Range,
)

class TestEncoder(TestCase):
    """Tests for rsk_mt.enforce.encoding.Encoder."""
    def __init__(self, *args):
        super().__init__(*args)
        self._encoder = Encoder()
    def test_binary(self):
        """Test rsk_mt.enforce.encoding.Encoder binary attribute"""
        self.assertEqual(self._encoder.binary, None)
    def test_encode(self):
        """Test rsk_mt.enforce.encoding.Encoder encode is abstract"""
        self.assertRaises(NotImplementedError, self._encoder.encode, None)
    def test_decode(self):
        """Test rsk_mt.enforce.encoding.Encoder decode is abstract"""
        self.assertRaises(NotImplementedError, self._encoder.decode, None)

class TestValueTypeEncoder(TestCase):
    """Tests for rsk_mt.enforce.encoding.ValueTypeEncoder."""
    def __init__(self, *args):
        super().__init__(*args)
        encoder = Json()
        value_type = Constrained(Integer(), (Range(((0, 5),)),))
        self._encoder = ValueTypeEncoder(encoder, value_type)
    def test_binary(self):
        """Test rsk_mt.enforce.encoding.ValueTypeEncoder binary attribute"""
        self.assertEqual(self._encoder.binary, False)
    def test_encode_success(self):
        """Test rsk_mt.enforce.encoding.ValueTypeEncoder encode success"""
        self.assertEqual('1', self._encoder.encode(1))
    def test_encode_type_error(self):
        """Test rsk_mt.enforce.encoding.ValueTypeEncoder encode TypeError"""
        self.assertRaises(TypeError, self._encoder.encode, 'foo')
    def test_encode_value_error(self):
        """Test rsk_mt.enforce.encoding.ValueTypeEncoder encode ValueError"""
        self.assertRaises(ValueError, self._encoder.encode, -2)
    def test_decode_success(self):
        """Test rsk_mt.enforce.encoding.ValueTypeEncoder decode success"""
        self.assertEqual(1, self._encoder.decode('1'))
    def test_decode_type_error(self):
        """Test rsk_mt.enforce.encoding.ValueTypeEncoder decode TypeError"""
        self.assertRaises(TypeError, self._encoder.decode, '"foo"')
    def test_decode_value_error(self):
        """Test rsk_mt.enforce.encoding.ValueTypeEncoder decode ValueError"""
        self.assertRaises(ValueError, self._encoder.decode, '-2')

class TestJson(TestCase):
    """Tests for rsk_mt.enforce.encoding.Json."""
    def __init__(self, *args):
        super().__init__(*args)
        self._encoder = Json()
    def test_binary(self):
        """Test rsk_mt.enforce.encoding.Json binary attribute"""
        self.assertEqual(self._encoder.binary, False)
    def test_encode(self):
        """Test rsk_mt.enforce.encoding.Json encode success"""
        self.assertEqual(
            self._encoder.encode([{'a': None}, -74]),
            '[{"a": null}, -74]',
        )
    def test_decode(self):
        """Test rsk_mt.enforce.encoding.Json decode success"""
        self.assertEqual(
            self._encoder.decode('[false, 7.2]'),
            [False, 7.2],
        )
    def test_decode_bad(self):
        """Test rsk_mt.enforce.encoding.Json decode ValueError"""
        self.assertRaises(ValueError, self._encoder.decode, 'not JSON')

class TestJsonDecimal(TestCase):
    """Tests for rsk_mt.enforce.encoding.JsonDecimal."""
    def __init__(self, *args):
        super().__init__(*args)
        self._encoder = JsonDecimal()
    def test_binary(self):
        """Test rsk_mt.enforce.encoding.JsonDecimal binary attribute"""
        self.assertEqual(self._encoder.binary, False)
    def test_encode(self):
        """Test rsk_mt.enforce.encoding.JsonDecimal encode success"""
        # decimal to real
        self.assertEqual(self._encoder.encode(Decimal('-3.7')), '-3.7')
        # float to real
        self.assertEqual(self._encoder.encode(-3.7), '-3.7')
    def test_encode_bad(self):
        """Test rsk_mt.enforce.encoding.JsonDecimal encode TypeError"""
        self.assertRaises(TypeError, self._encoder.encode, self)
    def test_decode(self):
        """Test rsk_mt.enforce.encoding.JsonDecimal decode success"""
        self.assertEqual(self._encoder.decode('-3.7'), Decimal('-3.7'))
        self.assertEqual(self._encoder.decode('true'), True)
    def test_decode_bad(self):
        """Test rsk_mt.enforce.encoding.JsonDecimal decode ValueError"""
        self.assertRaises(ValueError, self._encoder.decode, 'not JSON')
    def test_dumps(self):
        """Test rsk_mt.enforce.encoding.JsonDecimal.dumps method"""
        self.assertEqual(self._encoder.dumps(Decimal('-99.4')), '-99.4')
        self.assertEqual(self._encoder.dumps(-99.4), '-99.4')
    def test_dump(self):
        """Test rsk_mt.enforce.encoding.JsonDecimal.dump method"""
        (rfd, wfd) = os.pipe()
        with os.fdopen(wfd, 'w') as wfid:
            self._encoder.dump([Decimal('0.01'), False], wfid)
        with os.fdopen(rfd) as rfid:
            self.assertEqual(rfid.read(), '[0.01, false]')
    def test_loads(self):
        """Test rsk_mt.enforce.encoding.JsonDecimal.loads method"""
        self.assertEqual(self._encoder.loads('-23.4'), Decimal('-23.4'))
        self.assertEqual(self._encoder.loads('{}'), {})
    def test_load(self):
        """Test rsk_mt.enforce.encoding.JsonDecimal.load method"""
        (rfd, wfd) = os.pipe()
        with os.fdopen(wfd, 'w') as wfid:
            wfid.write('{"foo": -34.66}')
        with os.fdopen(rfd) as rfid:
            self.assertEqual(
                self._encoder.load(rfid),
                {'foo': Decimal('-34.66')},
            )
