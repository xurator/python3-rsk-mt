### SPDX-License-Identifier: GPL-2.0-or-later

"""A tool for generating a JSON Schema index."""

from argparse import ArgumentParser
import sys
import json
from os.path import (
    isfile,
    dirname,
    isabs,
    abspath,
)
from os.path import join as joinpath
from importlib.resources import (
    files,
    as_file,
)

from rsk_mt.jsonschema import share
from .schema import (RootSchema, Support)
from .types import TYPE_ABSOLUTE_URI

SYSTEM_FILE = '/usr/share/json-schema/rsk-mt/index.json'
BASE_URI = 'https://json-schema.roughsketch.co.uk/rsk-mt/index.json'

def build_index(filename=None):
    """Build an empty JSON Schema index, for mapping Schema URI to filename.

    Build a |RootSchema| which enforces the JSON Schema at `filename`. If
    `filename` is None then prefer to use a system JSON Schema file at
    :data:`SYSTEM_FILE`, falling back to using the JSON Schema file shipped
    with this code. Return an empty instance of the |RootSchema|.
    """
    if filename is not None:
        return RootSchema.load(filename)({})
    if isfile(SYSTEM_FILE):
        return RootSchema.load(SYSTEM_FILE)({})
    with as_file(files(share).joinpath('index.json')) as shipped:
        return RootSchema.load(shipped)({})

class IndexSupport(Support):
    """Application support for loading external Schemas.

    Load external Schemas from a single JSON Schema index. The index is built to
    enforce the schema in `filename`, as per :func:`build_index`. The index is
    populated with content from file `index`.
    """
    def __init__(self, filename, index, *args, **kwargs):
        Support.__init__(self, *args, **kwargs)
        self._dirname = dirname(index)
        self._index = build_index(filename)
        with open(index, encoding='utf-8') as fid:
            mapping = json.load(fid)
            self._index.update(mapping)
        ### a mapping of filename to root Schema
        self._roots = {}
        ### the stack of filenames being loaded
        self._stack = []
    def load_schema(self, uri):
        try:
            filename = self._index[TYPE_ABSOLUTE_URI.cast(uri)]
        except KeyError:
            # pylint: disable=raise-missing-from
            raise ValueError(uri)
        if not isabs(filename):
            filename = joinpath(self._dirname, filename)
            filename = abspath(filename)
        try:
            root = self._roots[filename]
        except KeyError:
            if filename in self._stack:
                err = [f'circular dependency from {filename} via files:']
                err += self._stack
                # pylint: disable=raise-missing-from
                raise RuntimeError('\n\t'.join(err))
            self._stack.append(filename)
            root = RootSchema.load(filename, support=self)
            self._roots[filename] = root
            self._stack.pop()
        return root.get_schema(uri, load=False)
    @classmethod
    def build(cls, index, *args, **kwargs):
        """Build an Application support instance.

        Return a new instance of `cls` for loading external Schemas. The index
        is built from the content in file `index`.
        """
        return cls(None, index, *args, **kwargs)

def main():
    """Generate a JSON Schema index.

    Print to stdout a mapping of Schema URI to local filename.
    """
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument(
        '-b', '--absolute-path', action='store_true',
        help=' '.join((
            "index filename by absolute path",
            "(by default filenames are indexed as supplied)",
        )),
    )
    aparser.add_argument(
        '-a', '--all', action='store_true',
        help=' '.join((
            "include all URIs in the index",
            "(by default only absolute URIs are included)",
        )),
    )
    aparser.add_argument(
        'schema', nargs='*', help="the JSON Schema files to index",
    )
    args = aparser.parse_args()
    index = build_index()
    for filename in args.schema:
        schema = RootSchema.load(filename, define=False)
        for uri in schema.uris:
            if not args.all:
                try:
                    uri = TYPE_ABSOLUTE_URI(uri)
                except ValueError:
                    continue
                if uri.endswith('#'):
                    continue
            try:
                if filename != index[uri]:
                    sys.exit(
                        f'{uri} appears in files {filename} and {index[uri]}'
                    )
            except KeyError:
                pass
            if args.absolute_path:
                index[uri] = abspath(filename)
            else:
                index[uri] = filename
    print(json.dumps(index))

if __name__ == '__main__':
    main()
