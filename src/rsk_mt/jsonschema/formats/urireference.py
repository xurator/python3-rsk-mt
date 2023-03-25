### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation`_ `uri-reference`_ format.

.. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
.. _uri-reference: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-7.3.5
.. _RFC 3986: https://tools.ietf.org/html/rfc3986
"""
# pylint: enable=line-too-long

from urllib.parse import urlsplit

from . import Format

class UriReference(Format):
    """Semantic validation of `uri-reference`_ strings per `RFC 3986`_."""
    name = 'uri-reference'
    def validates(self, primitive):
        return primitive == 'string'
    def __call__(self, val):
        if not isinstance(val, str):
            return False
        (scheme, authority, path, _, _) = urlsplit(val)
        # `RFC 3986`_ Section 4. URI Reference
        # "A URI-reference is either a URI or a relative reference.
        # If the URI-reference's prefix does not match the syntax of a scheme
        # followed by its colon separator, then the URI-reference is a relative
        # reference."
        if scheme and ((not authority and not path) or path.startswith('//')):
            return False
        return True
