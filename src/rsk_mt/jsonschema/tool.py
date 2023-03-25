### SPDX-License-Identifier: GPL-2.0-or-later

"""A tool for validating JSON-encoded data against a JSON Schema."""

from argparse import ArgumentParser
import re
import sys
from contextlib import nullcontext

from rsk_mt.enforce.encoding import JsonDecimal
from .formats import Format
from .schema import (RootSchema, Support, Results)
from .index import IndexSupport

JSON = JsonDecimal()

class _FormatRegexp(Format):
    """A format enforcing a regular expression on string values."""
    def __init__(self, name, regexp):
        self.name = name
        self._regexp = re.compile(regexp)
    def __call__(self, val):
        return bool(self._regexp.search(val))
    def validates(self, primitive):
        return primitive == 'string'
    @classmethod
    def build(cls, formats):
        """Build a mapping of format name to :class:`Format` instance.

        Return a mapping of format name to `cls` instance or None from the
        list of `formats` specification strings. A specification string is
        either a colon-separated format-name and regular expression (mapping
        format-name to `cls` instance), or ~ followed by format-name (mapping
        format-name to None). Any other string is discarded.
        """
        built = {}
        for spec in formats:
            try:
                name, regexp = spec.split(':', 1)
            except ValueError:
                if spec.startswith('~'):
                    built[spec[1:]] = None
            else:
                built[name] = cls(name, regexp)
        return built

def main():
    """Validate JSON-encoded data against a JSON Schema.

    Print valid data to stdout or print value validation results to stderr.
    """
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument(
        '-u', '--uri',
        help="the initial base URI of the JSON Schema",
    )
    aparser.add_argument(
        '-f', '--format',
        default=[], action='append',
        help=' '.join((
            "a string format to enforce, specified as a colon-separated name",
            "and regular expression pair e.g. --format='lower:^[a-z]+$',",
            "or, a format to disable, specified as ~ then format-name",
            "e.g. --format='~uri'",
        )),
    )
    aparser.add_argument('-d', '--debug', action='store_true', help=' '.join((
        "print value validation results to stdout (instead of valid data)",
    )))
    aparser.add_argument(
        '-l', '--load',
        help="the JSON Schema index to use to load referenced Schemas from",
    )
    aparser.add_argument(
        'schema',
        help="the JSON Schema file to validate the data against",
    )
    aparser.add_argument(
        'data',
        help="the JSON data file to validate, or '-' to read from stdin",
    )
    args = aparser.parse_args()
    formats = _FormatRegexp.build(args.format)
    if args.load:
        support = IndexSupport.build(args.load, formats=formats)
    else:
        support = Support(formats=formats)
    try:
        schema = RootSchema.load(args.schema, args.uri, JSON, support=support)
    except ValueError as err:
        sys.exit(f'failed to load JSON Schema: {err}')
    with (  open(args.data, encoding='utf-8')
            if args.data != '-' else
            nullcontext(sys.stdin)
        ) as fid:
        val = JSON.load(fid)
    results = Results.build()
    if schema.debug(val, results):
        print(JSON.dumps(results if args.debug else val))
    else:
        sys.exit(JSON.dumps(results))

if __name__ == '__main__':
    main()
