### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation`_ `JSON Pointer`_ formats.

.. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
.. _JSON Pointer: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-7.3.7
.. _json-pointer: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-7.3.7
.. _relative-json-pointer: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-7.3.7
.. _RFC 6901: https://tools.ietf.org/html/rfc6901
.. _draft: https://tools.ietf.org/html/draft-handrews-relative-json-pointer-00
"""
# pylint: enable=line-too-long

import re

from . import Format

UNESCAPED = r'[^~/]'
ESCAPED = r'~[01]'
REFERENCE_TOKEN = r'(' + UNESCAPED + r'|' + ESCAPED + r')*'
JSON_POINTER = r'(' + r'/' + REFERENCE_TOKEN + r')*'

NON_NEGATIVE_INTEGER = r'(0|[1-9][0-9]*)'
RELATIVE_JSON_POINTER = NON_NEGATIVE_INTEGER + r'(\#|' + JSON_POINTER + r')'

class JsonPointer(Format):
    """Semantic validation of `json-pointer`_ strings per `RFC 6901`_."""
    name = 'json-pointer'
    def __init__(self):
        super().__init__()
        self._regexp = re.compile(r'^' + JSON_POINTER + r'$')
    def validates(self, primitive):
        return primitive == 'string'
    def __call__(self, val):
        try:
            return bool(self._regexp.match(val))
        except TypeError:
            return False

class RelativeJsonPointer(Format): # pylint: disable=too-few-public-methods
    """Semantic validation of `relative-json-pointer`_ strings per `draft`_."""
    name = 'relative-json-pointer'
    def __init__(self):
        super().__init__()
        self._regexp = re.compile(r'^' + RELATIVE_JSON_POINTER + r'$')
    def validates(self, primitive):
        return primitive == 'string'
    def __call__(self, val):
        try:
            return bool(self._regexp.match(val))
        except TypeError:
            return False
