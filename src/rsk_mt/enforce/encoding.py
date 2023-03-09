### SPDX-License-Identifier: GPL-2.0-or-later

"""Enforcement of value encoding."""

import json
from decimal import Decimal

class Encoder():
    """A base class for value encoder/decoders.

    :attr:`binary` declares whether encoded values returned by :meth:`encode`
    and accepted by :meth:`decode` are binary or not:
    - a value of True declares binary encoded values of type :class:`bytes`
    - a value of False declares text encoded values of type :class:`str`
    - a value of None declares encoded values of undefined type
    """
    binary = None
    def encode(self, val):
        """Encode `val`."""
        raise NotImplementedError
    def decode(self, val):
        """Decode `val`."""
        raise NotImplementedError

class ValueTypeEncoder(Encoder):
    """An :class:`Encoder` enforced by a :class:`ValueType`."""
    def __init__(self, encoder, value_type):
        super().__init__()
        self._encoder = encoder
        self._value_type = value_type
    @property
    def binary(self):
        """Return the :attr:`binary` attribute of this instance's encoder."""
        return self._encoder.binary
    def encode(self, val):
        """Encode the canonical value to which lexical value `val` maps.

        Raises :class:`TypeError` or :class:`ValueError` if `val` does not map
        to a canonical value or the canonical value cannot be encoded.
        """
        canonical = self._value_type.cast(val)
        return self._encoder.encode(canonical)
    def decode(self, val):
        """Decode a lexical value from `val`, return the mapped canonical value.

        Raises :class:`TypeError` or :class:`ValueError` if `val` cannot be
        decoded or the lexical value does not map to a canonical value.
        """
        lexical = self._encoder.decode(val)
        return self._value_type.cast(lexical)

class Json(Encoder):
    """A JSON encoder/decoder."""
    binary = False
    def __init__(self, serializers=()):
        super().__init__()
        serializers = dict(serializers)
        def default(self, obj): # pylint: disable=unused-argument
            """Return a commonly serializable value from `obj`."""
            try:
                func = serializers[type(obj)]
            except KeyError:
                return super(obj)
            else:
                return func(obj)
        body = {'default': default}
        self._encode_cls = type('JsonSerializer', (json.JSONEncoder,), body)
    def encode(self, val):
        return self.dumps(val)
    def decode(self, val):
        return self.loads(val)
    def dumps(self, val, *args, **kwargs):
        """Encode `val` to a JSON-encoded string.

        `args` and `kwargs` as per :func:`json.dumps`.
        """
        return json.dumps(val, cls=self._encode_cls, *args, **kwargs)
    def dump(self, val, fid, *args, **kwargs):
        """Encode `val` as a JSON-encoded string to file `fid`.

        `args` and `kwargs` as per :func:`json.dump`.
        """
        return json.dump(val, fid, cls=self._encode_cls, *args, **kwargs)
    def loads(self, val, *args, **kwargs): # pylint: disable=no-self-use
        """Decode a value from JSON-encoded string `val`.

        `args` and `kwargs` as per :func:`json.loads`.
        """
        return json.loads(val, *args, **kwargs)
    def load(self, fid, *args, **kwargs): # pylint: disable=no-self-use
        """Decode a value from a JSON-encoded string in file `fid`.

        `args` and `kwargs` as per :func:`json.load`.
        """
        return json.load(fid, *args, **kwargs)

class JsonDecimal(Json):
    """A JSON encoder/decoder for :class:`Decimal` values.

    Real numbers are decoded as :class:`Decimal` values.
    :class:`Decimal` and float values are encoded as real numbers.
    """
    def __init__(self, serializers=()):
        super().__init__(serializers + ((Decimal, float),))
    def loads(self, val, *args, **kwargs):
        """Decode a value from JSON-encoded string `val`.

        Real numbers are decoded as :class:`Decimal` values.
        `args` and `kwargs` as per :func:`json.loads`.
        """
        return super().loads(val, parse_float=Decimal, *args, **kwargs)
    def load(self, fid, *args, **kwargs):
        """Decode a value from a JSON-encoded string in file `fid`.

        Real numbers are decoded as :class:`Decimal` values.
        `args` and `kwargs` as per :func:`json.load`.
        """
        return super().load(fid, parse_float=Decimal, *args, **kwargs)
