### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema encoding: base64"""

from unittest import TestCase

from rsk_mt.jsonschema.encodings import Base64

from .test_encoding import EncodingTestBuilder

class TestBase64(TestCase, metaclass=EncodingTestBuilder):
    """Test JSON Schema encoding base64."""
    constructor = Base64
    name = 'base64'
    accept = (
        "",             # ""
        "YQ==",         # "a"
        "Zm9vYmFyYmF6", # "foobarbaz"
        "Zm9=",         # "fo"
    )
    reject = (
        "Z",
        "Zm",
        "Zm9",
    )
