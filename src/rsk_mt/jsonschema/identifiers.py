### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""JSON Schema identifiers.

.. _JSON Pointer: https://tools.ietf.org/html/rfc6901
.. _base URI: https://tools.ietf.org/html/draft-handrews-json-schema-01#section-8
"""
# pylint: enable=line-too-long

from urllib.parse import (
    urlsplit,
    urlunsplit,
)
from .types import (
    TYPE_URI_REFERENCE,
    TYPE_ABSOLUTE_URI,
)

def key_path_to_json_pointer(key_path):
    """Return `key_path` as a `JSON Pointer`_ string.

    `key_path` is a tuple of keys for addressing an element in an arbitrary
    structure of dict and list instances.
    """
    def escape(token):
        """Return `token` as an escaped string for use in a `JSON Pointer`_."""
        # https://tools.ietf.org/html/rfc6901#section-3
        # "Because the characters '~' (%x7E) and '/' (%x2F) have special
        # meanings in JSON Pointer, '~' needs to be encoded as '~0' and '/'
        # needs to be encoded as '~1' when these characters appear in a
        # reference token."
        return str(token).replace('~', '~0').replace('/', '~1')
    return '/' + '/'.join(escape(_) for _ in key_path) if key_path else ''

class Identifiers():
    """A set of identifiers for a JSON Schema.

    `context_base_uri` is an absolute URI, the base URI of the Schema context.
    `key_path` is the tuple of keys to address the Schema relative to the root
    Schema.
    """
    def __init__(self, context_base_uri, key_path=()):
        self._context_base_uri = context_base_uri
        self._key_path = key_path
        self._pointer = key_path_to_json_pointer(key_path)
        self._base_uri = None
        self._uri = None
    @property
    def key_path(self):
        """The tuple of keys to address the Schema."""
        return self._key_path
    @property
    def pointer(self):
        """The `JSON Pointer`_ address of the Schema."""
        return self._pointer
    @property
    def base_uri(self):
        """The `base URI`_ of the Schema."""
        return self._base_uri
    @property
    def uri(self):
        """The URI of the Schema."""
        return self._uri
    @uri.setter
    def uri(self, uri):
        """Set the URI of the Schema."""
        if self._uri is not None:
            raise RuntimeError
        self._uri = uri
    def define(self, schema):
        """Finalise this set of identifiers for JSON Schema `schema`."""
        id_ = schema.id_
        # screen `id_` value
        if id_:
            if schema.is_root:
                # https://tools.ietf.org/html/draft-handrews-json-schema-01
                # #section-8.2.1
                # "The root schema of a JSON Schema document SHOULD contain an
                # '$id' keyword with a URI (containing a scheme, but no
                # fragment), or this absolute URI but with an empty fragment."
                try:
                    TYPE_ABSOLUTE_URI(id_)
                except ValueError:
                    TYPE_ABSOLUTE_URI(id_.rstrip('#'))
            else:
                # https://tools.ietf.org/html/draft-handrews-json-schema-01
                # #section-8.2
                # If present, the value for this keyword MUST be a string, and
                # MUST represent a valid URI-reference [RFC3986]. This value
                # SHOULD be normalized, and SHOULD NOT be an empty fragment <#>
                # or an empty string <>.
                TYPE_URI_REFERENCE(id_)
                if TYPE_URI_REFERENCE.is_fragment(id_):
                    # https://tools.ietf.org/html/draft-handrews-json-schema-01
                    # #section-8.2.3
                    format_ = schema.root.get_format('location-independent-$id')
                    if format_ and not format_(id_):
                        raise ValueError(id_)
        # https://tools.ietf.org/html/draft-handrews-json-schema-01#section-8
        if not schema.is_root or not id_:
            self._base_uri = self._context_base_uri
        else:
            self._base_uri = id_
        # The URI of the Schema is either an absolute URI or base URI with $id
        # fragment (or None)
        if schema.is_root or id_:
            fragment = id_.lstrip('#') if id_ and id_.startswith('#') else None
            self._uri = urlunsplit(urlsplit(self.base_uri)[0:4] + (fragment,))
        return self
