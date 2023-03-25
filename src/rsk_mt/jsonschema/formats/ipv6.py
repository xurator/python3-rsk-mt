### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation`_ `ipv6`_ format.

.. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
.. _ipv6: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-7.3.4
.. _RFC 2373: https://tools.ietf.org/html/rfc2373#section-2.2
"""
# pylint: enable=line-too-long

import re

from . import Format

class IPv6(Format):
    """Semantic validation of `ipv6`_ strings per `RFC 2373`_."""
    name = 'ipv6'
    def __init__(self):
        super().__init__()
        expr = r''.join((
            r'((:|[0-9a-fA-F]{0,4}):)([0-9a-fA-F]{0,4}:){0,5}',
            r'((([0-9a-fA-F]{0,4}:)?(:|[0-9a-fA-F]{0,4}))|',
            r'(((25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\.){3}',
            r'(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])))',
        ))
        self._regexp = re.compile(r'^' + expr + r'$')
    def validates(self, primitive):
        return primitive == 'string'
    def __call__(self, val):
        try:
            return bool(self._regexp.match(val))
        except TypeError:
            return False
