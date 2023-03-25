### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for rsk_mt.model.ModelledTuple"""

from unittest import TestCase
from nose2.tools import params

from rsk_mt.enforce.value import (
    Boolean,
    Integer,
    String,
)
from rsk_mt.model import (
    NotDefinedError,
    AlreadyDefinedError,
    SequenceModel,
    ModelledTuple,
)

from . import (
    make_fqname,
    make_params_values,
)

class TestSequenceModelNegative(TestCase):
    """Negative tests for rsk_mt.model.SequenceModel."""
    def test_model_atomic(self):
        """Test rsk_mt.model.SequenceModel rejects atomic model spec"""
        model = 123
        self.assertRaises(ValueError, SequenceModel, model, 'must-understand')
    def test_model_list(self):
        """Test rsk_mt.model.SequenceModel rejects list model spec"""
        model = [123]
        self.assertRaises(ValueError, SequenceModel, model, 'must-understand')
    def test_model_bad_head(self):
        """Test rsk_mt.model.SequenceModel rejects bad head value type"""
        model = {'head': (99,)}
        self.assertRaises(ValueError, SequenceModel, model, 'must-understand')
    def test_model_bad_tail(self):
        """Test rsk_mt.model.SequenceModel rejects bad tail value type"""
        model = {'tail': 99}
        self.assertRaises(ValueError, SequenceModel, model, 'must-understand')
    def test_policy_unsupported(self):
        """Test rsk_mt.model.SequenceModel rejects unsupported policy"""
        model = {}
        self.assertRaises(ValueError, SequenceModel, model, 'not-supported')
    def test_model_not_defined(self):
        """Test rsk_mt.model.SequenceModel rejects __call__ before model defined"""
        model = SequenceModel(None, 'must-understand')
        self.assertRaises(NotDefinedError, model, {})
    def test_model_already_defined(self):
        """Test rsk_mt.model.SequenceModel rejects define when already defined"""
        model = SequenceModel({}, 'must-understand')
        try:
            model.model_spec = {}
        except AlreadyDefinedError:
            pass
        else:
            self.fail('failed to reject define when already defined')
    def test_instance_bad_type(self):
        """Test rsk_mt.model.SequenceModel rejects bad type"""
        model = SequenceModel({}, 'must-understand')
        self.assertRaises(TypeError, model, 99)

class _SequenceModelTestBuilder(type):
    """Build tests for rsk_mt.model.SequenceModel with specific policy.

    Specify this class as metaclass and provide:
    `policy_spec` - the policy to test
    `empty_success` - an iterable of pairs for empty model call success
    `empty_error` - an iterable of values for empty model call error
    `specific_success` - an iterable of pairs for specific model call success
    `specific_error` - an iterable of values for specific model call error

    Tests are built for: an empty model, built using :attr:`empty_spec` and
    `policy_spec`, enforcing an empty tuple; and a specific model, built using
    :attr:`specific_spec` and `policy_spec`, enforcing a non-empty tuple.

    For call success, provide (input, output) pairs.
    """
    # empty model
    empty_spec = {}
    # specific model
    specific_spec = {
        'head': [Boolean(), Integer()],
        'tail': String(),
        'length': (1, 4),
        'unique': True,
        # pylint: disable=unsupported-membership-test
        'condition': lambda val: 'FAILME' not in val,
    }
    # test data
    type_checks = (
        (None, False),
        (False, False),
        (True, False),
        (-1, False),
        (0, False),
        (1, False),
        (-1.5, False),
        (0.0, False),
        (1.5, False),
        ('', True),
        ('foo', True),
        ((), True),
        ((1, 2, 3), True),
        ((('foo', 'bar'),), True),
        ([], True),
        ([1, 2, 3], True),
        ([['foo', 'bar']], True),
        ({}, True),
        ({'foo': 'bar'}, True),
    )
    def __new__(cls, name, bases, dct):
        fqname = make_fqname(SequenceModel)
        policy_spec = dct['policy_spec']
        empty = (
            'empty',
            cls.empty_spec,
            dct['empty_success'],
            dct['empty_error'],
        )
        specific = (
            'specific',
            cls.specific_spec,
            dct['specific_success'],
            dct['specific_error'],
        )
        # build out class for testing
        for (which, model_spec, call_success, call_error) in (
                empty,
                specific,
            ):
            model = SequenceModel(model_spec, policy_spec)
            dct.update({
                f'test_attributes_{which}': cls.make_test_attributes(
                    fqname, which, model, model_spec, policy_spec,
                ),
                f'test_check_{which}': cls.make_test_check(
                    fqname, which, model, cls.type_checks,
                ),
                f'test_call_success_{which}': cls.make_test_call_success(
                    fqname, which, model, call_success,
                ),
                f'test_call_error_{which}': cls.make_test_call_error(
                    fqname, which, model, make_params_values(call_error),
                ),
            })
        return super().__new__(cls, name, bases, dct)
    # make functions for use as TestCase methods
    @staticmethod
    def make_test_attributes(fqname, which, model, model_spec, policy_spec):
        """Make a function testing for attribute values."""
        def method(self):
            """Test `model` attribute values."""
            self.assertEqual(model.model_spec, model_spec)
            self.assertEqual(model.policy_spec, policy_spec)
        method.__doc__ = f'Test {fqname} {which} model attribute values'
        return method
    @staticmethod
    def make_test_check(fqname, which, model, pairs):
        """Make a function testing for expected check results."""
        @params(*pairs)
        def method(self, value, result):
            """Test type check result."""
            self.assertEqual(model.check(value), result)
        method.__doc__ = f'Test {fqname} {which} model check result'
        return method
    @staticmethod
    def make_test_call_success(fqname, which, model, pairs):
        """Make a function testing for expected call results"""
        @params(*pairs)
        def method(self, value, result):
            """Test call result."""
            self.assertEqual(model(value), result)
        method.__doc__ = f'Test {fqname} {which} model call result'
        return method
    @staticmethod
    def make_test_call_error(fqname, which, model, values):
        """Make a function testing for expected call errors."""
        @params(*values)
        def method(self, value):
            """Test call error."""
            self.assertRaises((TypeError, ValueError), model, value)
        method.__doc__ = f'Test {fqname} {which} model call error'
        return method

class TestSequenceModelMustUnderstand(
        TestCase,
        metaclass=_SequenceModelTestBuilder
    ):
    """Tests for rsk_mt.model.SequenceModel with policy must-understand."""
    policy_spec = 'must-understand'
    empty_success = (
        ([], []),
    )
    empty_error = (
        1,
        ['l-string'],
        ('t-string',),
        {'d-key': 'd-val'},
    )
    specific_success = (
        ([False], [False]),
        ([True, 0], [True, 0]),
        ([False, 1, "foo"], [False, 1, "foo"]),
        ([True, 2, "foo", "bar"], [True, 2, "foo", "bar"]),
    )
    specific_error = empty_error + (
        [],
        (),
        [1],
        [True, "foo"],
        [True, 1, True],
        [True, 1, "foo", False],
        [True, 1, "foo", "foo"],
        [False, 3, "foo", "bar", "baz"],
        [False, 5, "FAILME", "bar"],
    )

class TestSequenceModelMustIgnore(
        TestCase,
        metaclass=_SequenceModelTestBuilder,
    ):
    """Tests for rsk_mt.model.SequenceModel with policy must-ignore."""
    policy_spec = 'must-ignore'
    empty_success = (
        ([], []),
        (['l-string'], []),
        (('t-string',), []),
        ({'d-key': 'd-val'}, []),
    )
    empty_error = (
        1,
    )
    specific_success = (
        ([False], [False]),
        ([True, 0], [True, 0]),
        ([False, 1, "foo"], [False, 1, "foo"]),
        ([True, 2, "foo", "bar"], [True, 2, "foo", "bar"]),
    )
    specific_error = empty_error + (
        [],
        (),
        [1],
        [True, "foo"],
        [True, 1, True],
        [True, 1, "foo", False],
        [True, 1, "foo", "foo"],
        [False, 3, "foo", "bar", "baz"],
        [False, 5, "FAILME", "bar"],
    )

class TestSequenceModelMustAccept(
        TestCase,
        metaclass=_SequenceModelTestBuilder,
    ):
    """Tests for rsk_mt.model.SequenceModel with policy must-accept."""
    policy_spec = 'must-accept'
    empty_success = (
        ([], []),
        (['l-string'], ['l-string']),
        (('t-string',), ['t-string',]),
        ({'d-key': 'd-val'}, ['d-key']),
    )
    empty_error = (
        1,
    )
    specific_success = (
        ([False], [False]),
        ([True, 0], [True, 0]),
        ([False, 1, "foo"], [False, 1, "foo"]),
        ([True, 2, "foo", "bar"], [True, 2, "foo", "bar"]),
    )
    specific_error = empty_error + (
        [],
        (),
        [1],
        [True, "foo"],
        [True, 1, True],
        [True, 1, "foo", False],
        [True, 1, "foo", "foo"],
        [False, 3, "foo", "bar", "baz"],
        [False, 5, "FAILME", "bar"],
    )

# pylint: disable=too-few-public-methods
class EmptyTuple(metaclass=ModelledTuple):
    """A specialised class enforcing an empty tuple model."""
    model = {}
    def __init__(self): # empty but part of the test
        pass
# pylint: enable=too-few-public-methods

class TestModelledTuple(TestCase):
    """Tests for class from rsk_mt.model.ModelledTuple."""
    def test_create(self):
        """Test class from rsk_mt.model.ModelledTuple with __init__ method"""
        self.assertEqual(EmptyTuple(), ())
    def test_bad_type(self):
        """Test class from rsk_mt.model.ModelledTuple rejects bad type"""
        self.assertRaises(TypeError, EmptyTuple, 123)
    def test_bad_value(self):
        """Test class from rsk_mt.model.ModelledTuple rejects bad value"""
        self.assertRaises(ValueError, EmptyTuple, [1])
    def test_not_defined(self):
        """Test class from rsk_mt.model.ModelledTuple rejects when not defined"""
        cls = ModelledTuple.declare('OnlyDeclared', ())
        self.assertRaises(NotDefinedError, cls)

# pylint: disable=too-few-public-methods
class MagicValue():
    """A mixin for bases test of a :class:`ModelledTuple`."""
    @staticmethod
    def magic_value():
        """Return a magic value."""
        return 99
# pylint: enable=too-few-public-methods

class _ModelledTupleTestBuilder(type):
    """Build tests for classes using rsk_mt.model.ModelledType as metaclass."""
    def __new__(cls, name, bases, dct):
        model_spec = dct.get('model_spec')
        policy_spec = dct.get('policy_spec')
        descr = make_fqname(ModelledTuple)
        descr += '('
        descr += 'defined' if model_spec else 'undefined'
        descr += ' model, '
        descr += policy_spec if policy_spec else 'undefined'
        descr += ' policy)'
        # build out class for testing
        dct.update({
            'target_cls': cls.make_target_cls(model_spec, policy_spec),
            'test_redefine_error': cls.make_test_redefine_error(descr),
            'test_instance_create': cls.make_test_instance_create(descr),
        })
        return super().__new__(cls, name, bases, dct)
    @staticmethod
    def make_target_cls(model_spec, policy_spec):
        """Make a class, the test subject, using rsk_mt.model.ModelledTuple."""
        body = {}
        if model_spec:
            body['model'] = model_spec
        if policy_spec:
            body['policy'] = policy_spec
        if body:
            return ModelledTuple('Target', (MagicValue,), body)
        return ModelledTuple.declare('Target', (MagicValue,))
    # make functions for use as TestCase methods
    @staticmethod
    def make_test_redefine_error(descr):
        """Make a function testing redefinition rejected."""
        def method(self):
            """Test redefinition rejected."""
            self.assertRaises(AlreadyDefinedError, self.target_cls.define, {})
        method.__doc__ = f'Test {descr} rejects redefinition'
        return method
    @staticmethod
    def make_test_instance_create(descr):
        """Make a function testing instance creation."""
        def method(self):
            """Test instance creation."""
            instance = self.target_cls(self.initialiser)
            self.assertIsInstance(instance, tuple)
            self.assertEqual(instance.magic_value(), 99)
        method.__doc__ = f'Test {descr} instance creation'
        return method

MODEL_SPEC = {'head': [Integer(), String()]}
INITIALISER = (1, "foo")

# TestDefined*: define model and policy at class creation time

class TestDefinedMustUnderstand(TestCase, metaclass=_ModelledTupleTestBuilder):
    """Tests for rsk_mt.model.ModelledTuple defined, policy must-understand."""
    model_spec = MODEL_SPEC
    initialiser = INITIALISER
    policy_spec = 'must-understand'

class TestDefinedMustIgnore(TestCase, metaclass=_ModelledTupleTestBuilder):
    """Tests for rsk_mt.model.ModelledTuple defined, policy must-ignore."""
    model_spec = MODEL_SPEC
    initialiser = INITIALISER
    policy_spec = 'must-ignore'

class TestDefinedMustAccept(TestCase, metaclass=_ModelledTupleTestBuilder):
    """Tests for rsk_mt.model.ModelledTuple defined, policy must-accept."""
    model_spec = MODEL_SPEC
    initialiser = INITIALISER
    policy_spec = 'must-accept'

# TestDelayed*: define policy at class creation time, model later

class TestDelayedMustUnderstand(TestCase, metaclass=_ModelledTupleTestBuilder):
    """Tests for rsk_mt.model.ModelledTuple delayed, policy must-understand."""
    initialiser = INITIALISER
    policy_spec = 'must-understand'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pylint: disable=no-member
        if not self.target_cls.model.defined:
            self.target_cls.define(MODEL_SPEC, self.policy_spec)

class TestDelayedMustIgnore(TestCase, metaclass=_ModelledTupleTestBuilder):
    """Tests for rsk_mt.model.ModelledTuple delayed, policy must-ignore."""
    initialiser = INITIALISER
    policy_spec = 'must-ignore'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pylint: disable=no-member
        if not self.target_cls.model.defined:
            self.target_cls.define(MODEL_SPEC, self.policy_spec)

class TestDelayedMustAccept(TestCase, metaclass=_ModelledTupleTestBuilder):
    """Tests for rsk_mt.model.ModelledTuple delayed, policy must-accept."""
    initialiser = INITIALISER
    policy_spec = 'must-accept'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pylint: disable=no-member
        if not self.target_cls.model.defined:
            self.target_cls.define(MODEL_SPEC, self.policy_spec)

# TestDeclared*: define model and policy after class creation time

class TestDeclaredMustUnderstand(TestCase, metaclass=_ModelledTupleTestBuilder):
    """Tests for rsk_mt.model.ModelledTuple declared, policy must-understand."""
    initialiser = INITIALISER
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pylint: disable=no-member
        if not self.target_cls.model.defined:
            self.target_cls.model.policy_spec = 'must-understand'
            self.target_cls.define(MODEL_SPEC)

class TestDeclaredMustIgnore(TestCase, metaclass=_ModelledTupleTestBuilder):
    """Tests for rsk_mt.model.ModelledTuple declared, policy must-ignore."""
    initialiser = INITIALISER
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pylint: disable=no-member
        if not self.target_cls.model.defined:
            self.target_cls.model.policy_spec = 'must-ignore'
            self.target_cls.define(MODEL_SPEC)

class TestDeclaredMustAccept(TestCase, metaclass=_ModelledTupleTestBuilder):
    """Tests for rsk_mt.model.ModelledTuple declared, policy must-accept."""
    initialiser = INITIALISER
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pylint: disable=no-member
        if not self.target_cls.model.defined:
            self.target_cls.model.policy_spec = 'must-accept'
            self.target_cls.define(MODEL_SPEC)
