### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation`_ `hostname`_ format.

.. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
.. _hostname: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-7.3.3
.. _RFC 1034: https://tools.ietf.org/html/rfc1034#section-3.1
"""
# pylint: enable=line-too-long

import re

from . import Format

class Hostname(Format):
    """Semantic validation of `hostname`_ strings per `RFC 1034`_."""
    name = 'hostname'
    def __init__(self):
        super().__init__()
        label = r'([A-Za-z0-9]([A-Za-z0-9\-]{0,61}))?[A-Za-z0-9]'
        dot = r'\.'
        named = r'((' + label + dot + r')*' + r'(' + label + dot + r'?))'
        root = dot
        self._regexp = re.compile(r'^(' + named + r'|' + root + r')$')
    def validates(self, primitive):
        return primitive == 'string'
    def __call__(self, val):
        try:
            return bool(self._regexp.match(val)) and len(val.rstrip('.')) <= 253
        except TypeError:
            return False
