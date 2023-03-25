### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation`_ `uri`_ format.

.. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
.. _uri: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-7.3.5
.. _RFC 3986: https://tools.ietf.org/html/rfc3986
"""
# pylint: enable=line-too-long

from urllib.parse import urlsplit

from . import Format

class Uri(Format):
    """Semantic validation of `uri`_ strings per `RFC 3986`_."""
    name = 'uri'
    def validates(self, primitive):
        return primitive == 'string'
    def __call__(self, val):
        if not isinstance(val, str):
            return False
        (scheme, authority, path, _, _) = urlsplit(val)
        # `RFC 3986`_ Section 3. Syntax Components
        # "The scheme and path components are required, though the path may be
        # empty (no characters). When authority is present, the path must either
        # be empty or begin with a slash character. When authority is not
        # present, the path cannot begin with two slash characters."
        if not scheme:
            return False
        if (not authority and not path) or path.startswith('//'):
            return False
        return True
