### SPDX-License-Identifier: GPL-2.0-or-later

"""Test JSON Schema formats: email, idn-email"""

from unittest import TestCase

from rsk_mt.jsonschema.formats import (
    Email,
    IdnEmail,
)

from .test_format import FormatTestBuilder

class TestEmail(TestCase, metaclass=FormatTestBuilder):
    """Test JSON Schema format email."""
    constructor = Email
    name = 'email'
    validate = (
        'string',
    )
    accept = (
        "foo@bar.baz",
        "foo.bar@baz",
        "foo.bar@bar.baz",
    )
    reject = (
        "", "string",
        "foo@",
        "@bar.baz ",
        " foo@bar.baz",
        "fo o@bar.baz",
        "foo @bar.baz",
        "foo@ bar.baz",
        "foo@b ar.baz",
        "foo@bar .baz",
        "foo@bar. baz",
        "foo@bar.b az",
        "foo@bar.baz ",
        "@foo@bar.baz",
        "f@oo@bar.baz",
        "foo@b@ar.baz",
        "foo@bar.b@az",
        "foo@bar.baz@",
        "실례@실례.테스트",
        " 실례@실례.테스트",
        "실 례@실례.테스트",
        "실례 @실례.테스트",
        "실례@ 실례.테스트",
        "실례@실 례.테스트",
        "실례@실례 .테스트",
        "실례@실례. 테스트",
        "실례@실례.테 스트",
        "실례@실례.테스 트",
        "실례@실례.테스트 ",
    )
    invalid = (
        None,
        False, True,
        -1, 0, 1,
        -1.5, 0.0, 1.5,
        [], ["foo", "bar", "baz"],
        {}, {"foo": "bar"},
    )

class TestIdnEmail(TestCase, metaclass=FormatTestBuilder):
    """Test JSON Schema format idn-email."""
    constructor = IdnEmail
    name = 'idn-email'
    validate = (
        'string',
    )
    accept = (
        "foo@bar.baz",
        "foo.bar@baz",
        "foo.bar@bar.baz",
        "실례@실례.테스트",
    )
    reject = (
        "", "string",
        "foo@",
        "@bar.baz ",
        " foo@bar.baz",
        "fo o@bar.baz",
        "foo @bar.baz",
        "foo@ bar.baz",
        "foo@b ar.baz",
        "foo@bar .baz",
        "foo@bar. baz",
        "foo@bar.b az",
        "foo@bar.baz ",
        "@foo@bar.baz",
        "f@oo@bar.baz",
        "foo@b@ar.baz",
        "foo@bar.b@az",
        "foo@bar.baz@",
        " 실례@실례.테스트",
        "실 례@실례.테스트",
        "실례 @실례.테스트",
        "실례@ 실례.테스트",
        "실례@실 례.테스트",
        "실례@실례 .테스트",
        "실례@실례. 테스트",
        "실례@실례.테 스트",
        "실례@실례.테스 트",
        "실례@실례.테스트 ",
    )
    invalid = (
        None,
        False, True,
        -1, 0, 1,
        -1.5, 0.0, 1.5,
        [], ["foo", "bar", "baz"],
        {}, {"foo": "bar"},
    )
