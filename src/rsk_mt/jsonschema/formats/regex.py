### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation`_ `regex`_ format.

.. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
.. _regex: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-7.3.8
"""
# pylint: enable=line-too-long

import re

from . import Format

class Regex(Format):
    """Semantic validation of `regex`_ strings."""
    name = 'regex'
    def validates(self, primitive):
        return primitive == 'string'
    def __call__(self, val):
        try:
            return bool(re.compile(val))
        except (TypeError, re.error):
            return False
