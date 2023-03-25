### SPDX-License-Identifier: GPL-2.0-or-later

"""`JSON Schema Core`_ types.

.. _JSON Schema Core: https://tools.ietf.org/html/draft-handrews-json-schema-01
"""

from ..enforce.value import Null as TypeNull
from ..enforce.value import Boolean as TypeBoolean
from ..enforce.value import Integer as TypeInteger
from ..enforce.value import Number as TypeNumber
from ..enforce.value import String as TypeString
from ..enforce.value import Sequence as TypeSequence
from ..enforce.value import Mapping as TypeMapping
from ..enforce.value import Constrained

from .uri import TypeAbsoluteUri
from .uri import TypeUriReference

TYPE_CORE = {
    'null': TypeNull(),
    'boolean': TypeBoolean(),
    'integer': TypeInteger(),
    'number': TypeNumber(),
    'string': TypeString(),
    'array': TypeSequence(),
    'object': TypeMapping(),
}

TYPE_POSITIVE_NUMBER = Constrained(
    TypeNumber(),
    (lambda val: val > 0,),
)

TYPE_NON_NEGATIVE_INTEGER = Constrained(
    TypeInteger(),
    (lambda val: val >= 0,),
)

TYPE_ABSOLUTE_URI = TypeAbsoluteUri()

TYPE_URI_REFERENCE = TypeUriReference()
