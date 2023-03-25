### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation`_ `base64`_ encoding.

.. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
.. _base64: https://tools.ietf.org/html/rfc2045#section-6.8
.. _RFC 2045: https://tools.ietf.org/html/rfc2045
"""
# pylint: enable=line-too-long

from base64 import b64decode
from binascii import Error as EncodingError

from . import Encoding

class Base64(Encoding): # pylint: disable=too-few-public-methods
    """Validation of `base64`_ encoded strings as specified in `RFC 2045`_."""
    name = 'base64'
    def __call__(self, val):
        try:
            b64decode(val)
        except (TypeError, EncodingError):
            return False
        else:
            return True
