### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema formats: json-pointer, relative-json-pointer"""

from unittest import TestCase

from rsk_mt.jsonschema.formats import (
    JsonPointer,
    RelativeJsonPointer,
)

from .test_format import FormatTestBuilder

class TestJsonPointer(TestCase, metaclass=FormatTestBuilder):
    """Test JSON Schema format json-pointer."""
    constructor = JsonPointer
    name = 'json-pointer'
    validate = (
        'string',
    )
    accept = (
        "",
        "/foo",
        "/foo/0",
        "/",
        "/a~1b",
        "/c%d",
        "/e^f",
        "/g|h",
        "/i\\j",
        "/k\"l",
        "/ ",
        "/m~0n",
        "/foo/bar",
        "/foo/a~0b",
        "/foo/a~1b",
    )
    reject = (
        "string",
        "/~",
        "/fo~o",
        "/~2",
        "/foo/~",
        "/foo/fo~o",
        "/foo/~2",
    )
    invalid = (
        None,
        False, True,
        -1, 0, 1,
        -1.5, 0.0, 1.5,
        [], ["foo", "bar", "baz"],
        {}, {"foo": "bar"},
    )

class TestRelativeJsonPointer(TestCase, metaclass=FormatTestBuilder):
    """Test JSON Schema format relative-json-pointer."""
    constructor = RelativeJsonPointer
    name = 'relative-json-pointer'
    validate = (
        'string',
    )
    accept = (
        "0#",
        "1#",
        "234#",
        "0",
        "1",
        "234",
        "0/foo",
        "1/foo/0",
        "2/",
        "3/a~1b",
        "4/c%d",
        "5/e^f",
        "6/g|h",
        "7/i\\j",
        "8/k\"l",
        "9/ ",
        "10/m~0n",
        "11/foo/bar",
        "12/foo/a~0b",
        "13/foo/a~1b",
    )
    reject = TestJsonPointer.accept + TestJsonPointer.reject + (
        ### leading zeroes
        "00#",
        "01#",
        ### non-decimal integer part
        "0abc#",
        "1abc#",
        "123abc#",
    )
    invalid = (
        None,
        False, True,
        -1, 0, 1,
        -1.5, 0.0, 1.5,
        [], ["foo", "bar", "baz"],
        {}, {"foo": "bar"},
    )
