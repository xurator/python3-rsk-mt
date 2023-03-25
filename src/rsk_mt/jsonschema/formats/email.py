### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Validation`_ `email address`_ formats.

.. _JSON Schema Validation: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
.. _email address: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-7.3.2
.. _email: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-7.3.2
.. _idn-email: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-7.3.2
.. _RFC 5322: https://tools.ietf.org/html/rfc5322#section-3.4.1
.. _RFC 6531: https://tools.ietf.org/html/rfc6531
"""
# pylint: enable=line-too-long

import re

from . import Format

ATEXT = r'[\w\!\#\$\%\&\'\*\+\-\/\=\?\^\_\`\{\|\}\~]+'

class Email(Format):
    """Semantic validation of `email`_ strings per `RFC 5322`_.

    Only `dot-atom` production is supported: no comments or folding whitespace.
    """
    name = 'email'
    flags = re.ASCII
    def __init__(self):
        super().__init__()
        dot_atom = ATEXT + r'(\.' + ATEXT + r')*'
        rpattern = r'^' + dot_atom + r'@' + dot_atom + r'$'
        self._regexp = re.compile(rpattern, self.flags)
    def validates(self, primitive):
        return primitive == 'string'
    def __call__(self, val):
        try:
            return bool(self._regexp.match(val))
        except TypeError:
            return False

class IdnEmail(Email):
    """Semantic validation of `idn-email`_ strings per `RFC 6531`_, `RFC 5322`_.

    Only `dot-atom` production is supported: no comments or folding whitespace.
    """
    name = 'idn-email'
    flags = 0
