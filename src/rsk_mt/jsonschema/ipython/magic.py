### SPDX-License-Identifier: GPL-2.0-or-later

'''IPython magic commands.

   Suggested usage: symlink to this file from a profile startup directory.
'''

from IPython.core.magic import register_line_magic
from IPython.core.magic_arguments import (
    magic_arguments,
    argument,
    parse_argstring,
)

from rsk_mt.jsonschema.schema import RootSchema as Schema

@register_line_magic
@magic_arguments()
@argument('-f', '--fromfile', action='store_true', help='read `data` from file')
@argument('schema', help='JSON Schema file to validate against')
@argument('data', nargs='+', help='JSON data to validate')
def jsonschema(arg):
    '''Validate JSON `data` against JSON Schema `schema`, returning `data` as a
       Python value.

       `schema` is a filename containing the JSON Schema.

       `data` is either a JSON-encoded string, or a file containing JSON data.
    '''
    args = parse_argstring(jsonschema, arg)
    schema = args.schema
    data = ' '.join(args.data)
    if args.fromfile:
        with open(data, encoding='utf-8') as fid:
            data = fid.read()
    return Schema.load(schema).decode(data)

del register_line_magic
del magic_arguments
del argument
