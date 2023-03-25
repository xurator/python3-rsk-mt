### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation`_ `ipv4`_ format.

.. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
.. _ipv4: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-7.3.4
.. _RFC 2673: https://tools.ietf.org/html/rfc2673#section-3.2
"""
# pylint: enable=line-too-long

import re

from . import Format

class IPv4(Format):
    """Semantic validation of `ipv4`_ strings per `RFC 2673`_."""
    name = 'ipv4'
    def __init__(self):
        super().__init__()
        decbyte = '([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])'
        dot = r'\.'
        rpattern = r'^((' + decbyte + dot + r'){3}' + decbyte + r')$'
        self._regexp = re.compile(rpattern)
    def validates(self, primitive):
        return primitive == 'string'
    def __call__(self, val):
        try:
            return bool(self._regexp.match(val))
        except TypeError:
            return False
