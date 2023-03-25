### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""Base class for `JSON Schema Validation`_ `contentEncoding`_ implementations.

.. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
.. _contentEncoding: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-8.3
"""
# pylint: enable=line-too-long

class Encoding(): # pylint: disable=too-few-public-methods
    """A base class for string value encodings.

    A derived class must specify a `name` attribute, a string giving the common
    name of the encoding.
    """
    name = None
    def __call__(self, val):
        """Test whether `val` was encoded by this encoding.

        Return True if `val` is a string value encoded by this encoding, False
        otherwise.
        """
        raise NotImplementedError
