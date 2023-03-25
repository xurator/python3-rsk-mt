### SPDX-License-Identifier: GPL-2.0-or-later

"""JSON Schema `URI reference`_ enforcement and manipulation.

.. |ValueError| replace:: :class:`ValueError`
.. |ValueType| replace:: :class:`ValueType <rsk_mt.enforce.value.ValueType>`

.. _URI reference: https://tools.ietf.org/html/rfc3986#section-4.1
.. _absolute URI: https://tools.ietf.org/html/rfc3986#section-4.3
"""

from urllib.parse import (
    urlsplit,
    urlunsplit,
)

from rsk_mt.enforce.value import ValueType

from .formats import UriReference

class TypeUriReference(ValueType):
    """A |ValueType| accepting `URI reference`_ strings."""
    fmt = UriReference()
    def __call__(self, val):
        uri = str(val)
        if self.fmt(uri):
            return uri
        raise ValueError(val)
    @staticmethod
    def is_fragment(uri):
        """Return True if `uri` is a fragment, else False."""
        (scheme, authority, path, query, fragment) = urlsplit(uri)
        return not (scheme or authority or path or query) and fragment

class TypeAbsoluteUri(TypeUriReference):
    """A |ValueType| accepting `absolute URI`_ strings.

    The set of canonical values is URIs which have a scheme and do not have a
    fragment. If the URI does not specify an authority then the scheme must be
    'urn' or 'file'. The set of lexical values is all URIs: a lexical value is
    mapped to a canonical value by stripping any fragment.
    """
    def __call__(self, val):
        uri = str(val)
        (scheme, authority, _, _, fragment) = urlsplit(uri)
        if not scheme or fragment or uri.endswith('#'):
            ### fails classic definition
            raise ValueError(val)
        if not authority and scheme.lower() not in ('urn', 'file'):
            ### urlsplit detected a URI which looks like a URN without 'urn:'
            ### or a URL which is not 'file:'
            raise ValueError(val)
        return uri
    def cast(self, val):
        parts = urlsplit(val)
        uri = urlunsplit(parts[0:4] + (None,))
        return self(uri)
    @staticmethod
    def _graft_path(d_path, s_path):
        """Return a new path by grafting `s_path` onto `d_path`.

        Graft by replacing the last element in `d_path` with `s_path`.
        """
        sep = '/'
        elems = d_path.split(sep)
        elems[-1] = s_path.lstrip(sep)
        return sep.join(elems)
    def graft(self, dst, src):
        """Return an absolute URI by grafting `src` URI into `dst` URI.

        If `dst` is not an absolute URI, then raise |ValueError|;
        if `src` is an absolute URI, then return `src`;
        if `src` is a URI fragment, then return `dst`;
        otherwise, if `dst` is a URN, raise |ValueError|; or,
        if `dst` is a URL, return the URL formed by replacing the last element
        in `dst`'s path with `src`'s path.
        """
        self(dst)
        try:
            return self(src)
        except ValueError:
            pass
        if self.is_fragment(src):
            return dst
        d_parts = urlsplit(dst)
        if d_parts[0].lower() == 'urn':
            raise ValueError((dst, src))
        s_parts = urlsplit(src)
        g_path = self._graft_path(d_parts[2], s_parts[2])
        return urlunsplit(d_parts[0:2] + (g_path,) + d_parts[3:])
    def resolve(self, dst, src):
        """Return a URI by resolving `src` URI with respect to `dst` URI:

        If `dst` is not an absolute URI, then raise |ValueError|;
        if `src` is an absolute URI, then return `src`;
        if `src` is a URI fragment, then return the URI formed from appending
        `src` fragment to `dst`;
        otherwise, if `dst` is a URN, raise |ValueError|; or,
        if `dst` is a URL, return the URL formed by replacing the last element
        in `dst`'s path with `src`'s path.
        """
        self(dst)
        try:
            self(urlunsplit(urlsplit(src)[0:-1] + ('',)))
            return src
        except ValueError:
            pass
        d_parts = urlsplit(dst)
        if self.is_fragment(src):
            return urlunsplit(d_parts[0:-1] + (src.lstrip('#'),))
        if d_parts[0].lower() == 'urn':
            raise ValueError((dst, src))
        s_parts = urlsplit(src)
        g_path = self._graft_path(d_parts[2], s_parts[2])
        return urlunsplit(d_parts[0:2] + (g_path,) + d_parts[3:])
