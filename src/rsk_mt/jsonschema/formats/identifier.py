### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema`_ `location-independent`_ identifier format.

.. _JSON Schema: https://tools.ietf.org/html/draft-handrews-json-schema-01
.. _location-independent: https://tools.ietf.org/html/draft-handrews-json-schema-01#section-8.2.3
"""
# pylint: enable=line-too-long

import re

from . import Format

class LocationIndependentId(Format):
    """Semantic validation of `location-independent`_ identifier strings."""
    name = 'location-independent-$id'
    regexp = re.compile(r'^#[A-Za-z][A-Za-z0-9\-\_\:\.]*$')
    def validates(self, primitive):
        return primitive == 'string'
    def __call__(self, val):
        try:
            return bool(self.regexp.match(val))
        except TypeError:
            return False
