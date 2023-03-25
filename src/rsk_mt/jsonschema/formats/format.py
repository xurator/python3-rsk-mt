### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""Base class for `JSON Schema Validation`_ `format`_ implementations.

.. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
.. _format: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-7.2
"""
# pylint: enable=line-too-long

class Format():
    """A base class for semantic validation formats.

    A derived class must specify a `name` attribute, a string giving the common
    name of the format.
    """
    name = None
    def validates(self, primitive):
        """Return True if format validates `primitive` type, else False."""
        raise NotImplementedError
    def __call__(self, val):
        """Return True if `val` is semantically valid, else False."""
        raise NotImplementedError
