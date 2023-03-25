### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for rsk_mt.model.ModelledDict"""

from unittest import TestCase
from nose2.tools import params

from rsk_mt.enforce.value import (
    Any,
    Integer,
)
from rsk_mt.model import (
    NotDefinedError,
    AlreadyDefinedError,
    MappingModel,
    DictModel,
    ModelledDict,
)

from . import (
    make_fqname,
    make_params_values,
)

class TestMappingModelNegative(TestCase):
    """Negative tests for rsk_mt.model.MappingModel."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model = MappingModel(None, 'must-understand')
    def test_define(self):
        """Test rsk_mt.model.MappingModel is abstract"""
        self.assertRaises(NotImplementedError, MappingModel, {}, 'must-accept')
    def test_default_value(self):
        """Test rsk_mt.model.MappingModel default_value rejects unknown key"""
        self.assertRaises(KeyError, self._model.default_value, 'k')
    def test_screen_setitem(self):
        """Test rsk_mt.model.MappingModel screen_setitem rejects unknown key"""
        self.assertRaises(KeyError, self._model.screen_setitem, {}, 'k', 'v')
    def test_screen_moditem(self):
        """Test rsk_mt.model.MappingModel screen_moditem rejects unknown key"""
        self.assertRaises(KeyError, self._model.screen_moditem, {}, 'k', 'v')
    def test_screen_delitem(self):
        """Test rsk_mt.model.MappingModel screen_delitem passes unknown key"""
        self.assertEqual(self._model.screen_delitem({}, 'k'), 'k')
    def test_screen_update_empty(self):
        """Test rsk_mt.model.MappingModel screen_update passes empty other"""
        other = {}
        self.assertEqual(self._model.screen_update({}, other), other)
    def test_screen_update(self):
        """Test rsk_mt.model.MappingModel screen_update rejects non-empty other"""
        other = {'k': 'v'}
        self.assertRaises(ValueError, self._model.screen_update, {}, other)
    def test_model_pairs_free(self):
        """Test rsk_mt.model.MappingModel pairs_free returns all keys"""
        dct = {'foo': 1, 'bar': 2}
        keys = frozenset(dct)
        self.assertEqual(self._model.pairs_free(dct), keys)

class TestDictModelNegative(TestCase):
    """Negative tests for rsk_mt.model.DictModel."""
    def test_model_atomic(self):
        """Test rsk_mt.model.DictModel rejects atomic model spec"""
        model = 123
        self.assertRaises(ValueError, DictModel, model, 'must-understand')
    def test_model_list(self):
        """Test rsk_mt.model.DictModel rejects list model spec"""
        model = [123]
        self.assertRaises(ValueError, DictModel, model, 'must-understand')
    def test_model_bad_value_type(self):
        """Test rsk_mt.model.DictModel rejects bad elem value type"""
        model = {'foo': {'value_type': 99}}
        self.assertRaises(ValueError, DictModel, model, 'must-understand')
    def test_policy_unsupported(self):
        """Test rsk_mt.model.DictModel rejects unsupported policy"""
        model = {}
        self.assertRaises(ValueError, DictModel, model, 'not-supported')
    def test_model_not_defined(self):
        """Test rsk_mt.model.DictModel rejects __call__ before model defined"""
        model = DictModel(None, 'must-understand')
        self.assertRaises(NotDefinedError, model, {})
    def test_model_already_defined(self):
        """Test rsk_mt.model.DictModel rejects define when already defined"""
        model = DictModel({}, 'must-understand')
        try:
            model.model_spec = {}
        except AlreadyDefinedError:
            pass
        else:
            self.fail('failed to reject define when already defined')
    def test_instance_bad_type(self):
        """Test rsk_mt.model.DictModel rejects bad type"""
        model = DictModel({}, 'must-understand')
        self.assertRaises(TypeError, model, 99)

class _DictModelTestBuilder(type):
    """Build tests for rsk_mt.model.DictModel with specific policy.

    Specify this class as metaclass and provide:
    `policy_spec` - the policy to test
    `empty_success` - an iterable of pairs for empty model call success
    `empty_error` - an iterable of values for empty model call error
    `default_success` - an iterable of pairs for default model call success
    `default_error` - an iterable of values for default model call error
    `specific_success` - an iterable of pairs for specific model call success
    `specific_error` - an iterable of values for specific model call error

    Tests are build for: an empty model, built using :attr:`empty_spec` and
    `policy_spec`; a model with one element using the default element model,
    built using :attr:`default_spec` and `policy_spec`; a model with a specific
    element model, built using :attr:`specific_spec` and `policy_spec`.

    For call success, provide (input, output) pairs.
    """
    empty_spec = {}
    # single element with default model
    default_spec = {
        'foo': {},
    }
    # single element with specific model
    specific_spec = {
        'bar': {
            'value_type': Integer(),
            'mandatory': True,
            'constant': True,
            'default': -99,
        },
    }
    # common test data
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
        ('foo', False),
        ((), True),
        ((1, 2, 3), False),
        ((('foo', 'bar'),), True),
        ([], True),
        ([1, 2, 3], False),
        ([['foo', 'bar']], True),
        ({}, True),
        ({'foo': 'bar'}, True),
    )
    def __new__(cls, name, bases, dct):
        fqname = make_fqname(DictModel)
        policy_spec = dct['policy_spec']
        empty = (
            'empty',
            cls.empty_spec,
            dct['empty_success'],
            dct['empty_error'],
        )
        default = (
            'default',
            cls.default_spec,
            dct['default_success'],
            dct['default_error'],
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
                default,
                specific,
            ):
            model = DictModel(model_spec, policy_spec)
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
                f'test_model_access_{which}': cls.make_test_model_access(
                    fqname, which, model,
                ),
                f'test_model_error_{which}': cls.make_test_model_error(
                    fqname, which, model,
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
            self.assertEqual(model.defined, model_spec is not None)
            # iterating `model` should yield a key for each key in `model_spec`
            self.assertEqual(frozenset(model), frozenset(model_spec))
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
        """Make a function testing for expected call results."""
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
    @staticmethod
    def make_test_model_access(fqname, which, model):
        """Make a function testing for expected model access."""
        def method(self):
            """Test model access results."""
            mandatory_keys = set()
            for key in model.model_spec:
                elem_spec = model.model_spec[key]
                value_type = elem_spec.get('value_type', Any())
                if isinstance(value_type, Any):
                    val = {'balloons': [99, 'red']}
                else:
                    val = 123
                self.assertEqual(model.screen_value(key, val), val)
                mandatory = elem_spec.get('mandatory', False)
                self.assertEqual(model.is_mandatory(key), mandatory)
                if mandatory:
                    mandatory_keys.add(key)
                constant = elem_spec.get('constant', False)
                self.assertEqual(model.is_constant(key), constant)
                try:
                    default = elem_spec['default']
                except KeyError:
                    self.assertRaises(KeyError, model.default_value, key)
                else:
                    self.assertEqual(model.default_value(key), default)
            self.assertEqual(model.mandatory, mandatory_keys)
        method.__doc__ = f'Test {fqname} {which} model access'
        return method
    @staticmethod
    def make_test_model_error(fqname, which, model):
        """Make a function testing for expected model access errors."""
        def method(self):
            """Test model access errors."""
            self.assertRaises(KeyError, model.screen_value, 'bad', 1)
            self.assertRaises(KeyError, model.is_mandatory, 'bad')
            self.assertRaises(KeyError, model.is_constant, 'bad')
            self.assertRaises(KeyError, model.default_value, 'bad')
        method.__doc__ = f'Test {fqname} {which} model access error'
        return method

class TestDictModelMustUnderstand(TestCase, metaclass=_DictModelTestBuilder):
    """Test cases for rsk_mt.model.DictModel with must-understand policy."""
    policy_spec = 'must-understand'
    empty_success = (
        ({}, {}),
    )
    empty_error = (
        1,
        ['not-a-list-of-pairs'],
        {'unmodelled': 'any'},
    )
    default_success = empty_success + (
        ({'foo': 'string'}, {'foo': 'string'}),
        ({'foo': [True, 123]}, {'foo': [True, 123]}),
    )
    default_error = empty_error + (
        {'foo': 99, 'bar': 'abc'},
    )
    specific_success = (
        ({'bar': 77}, {'bar': 77}),
    )
    specific_error = empty_error + (
        {},
        {'bar': 'string'},
        {'baz': 99},
        {'bar': 99, 'baz': -123},
    )

class TestDictModelMustIgnore(TestCase, metaclass=_DictModelTestBuilder):
    """Test cases for rsk_mt.model.DictModel with must-ignore policy."""
    policy_spec = 'must-ignore'
    empty_success = (
        ({}, {}),
        ({'unmodelled': 'any'}, {}),
    )
    empty_error = (
        1,
        ['not-a-list-of-pairs'],
    )
    default_success = empty_success + (
        ({'foo': 'string'}, {'foo': 'string'}),
        ({'foo': [True, 123]}, {'foo': [True, 123]}),
        ({'foo': 99, 'bar': 'abc'}, {'foo': 99}),
    )
    default_error = empty_error
    specific_success = (
        ({'bar': 77}, {'bar': 77}),
        ({'bar': 99, 'baz': -123}, {'bar': 99}),
    )
    specific_error = empty_error + (
        {},
        {'bar': 'string'},
        {'baz': 99},
    )

class TestDictModelMustAccept(TestCase, metaclass=_DictModelTestBuilder):
    """Test cases for rsk_mt.model.DictModel with must-accept policy."""
    policy_spec = 'must-accept'
    empty_success = (
        ({}, {}),
        ({'unmodelled': 'any'}, {'unmodelled': 'any'}),
    )
    empty_error = (
        1,
        ['not-a-list-of-pairs'],
    )
    default_success = empty_success + (
        ({'foo': 'string'}, {'foo': 'string'}),
        ({'foo': [True, 123]}, {'foo': [True, 123]}),
        ({'foo': 99, 'bar': 'abc'}, {'foo': 99, 'bar': 'abc'}),
    )
    default_error = empty_error
    specific_success = (
        ({'bar': 123}, {'bar': 123}),
    )
    specific_error = empty_error + (
        {},
        {'bar': 'string'},
        {'bar': 'string', 'baz': -123},
    )

# pylint: disable=too-few-public-methods
class EmptyModelledDict(metaclass=ModelledDict):
    """A specialised class enforcing an empty dict model."""
    model = {}
    def __init__(self): # empty but part of the test
        pass
# pylint: enable=too-few-public-methods

class TestModelledDict(TestCase):
    """Tests for class from rsk_mt.model.ModelledDict."""
    def test_create(self):
        """Test class from rsk_mt.model.ModelledDict with __init__ method"""
        self.assertEqual(EmptyModelledDict(), {})
    def test_bad_type(self):
        """Test class from rsk_mt.model.ModelledDict rejects bad type"""
        self.assertRaises(TypeError, EmptyModelledDict, 123)
    def test_bad_value(self):
        """Test class from rsk_mt.model.ModelledDict rejects bad value"""
    def test_modelled_dict_not_defined(self):
        """Test class from rsk_mt.model.ModelledDict rejects when not defined"""
        cls = ModelledDict.declare('OnlyDeclared', ())
        self.assertRaises(NotDefinedError, cls)

# pylint: disable=too-few-public-methods
class SpecialMethod():
    """A mixin for bases test of a :class:`ModelledDict`."""
    def my_keys(self):
        """Return a frozenset of keys in `self`."""
        return frozenset(self)
# pylint: enable=too-few-public-methods

class _ModelledDictTestBuilder(type):
    """Build test for classes using rsk_mt.model.ModelledDict as metaclass.
    """
    def __new__(cls, name, bases, dct):
        model_spec = dct.get('model_spec')
        policy_spec = dct.get('policy_spec')
        descr = make_fqname(ModelledDict)
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
            'test_dict_getitem': cls.make_test_dict_getitem(descr),
            'test_dict_setitem': cls.make_test_dict_setitem(descr),
            'test_dict_delitem': cls.make_test_dict_delitem(descr),
            'test_dict_clear': cls.make_test_dict_clear(descr),
            'test_dict_pop': cls.make_test_dict_pop(descr),
            'test_dict_popitem': cls.make_test_dict_popitem(descr),
            'test_dict_setdefault': cls.make_test_dict_setdefault(descr),
            'test_dict_update': cls.make_test_dict_update(descr),
            'test_dict_unmodelled': cls.make_test_dict_unmodelled(descr),
        })
        return super().__new__(cls, name, bases, dct)
    @staticmethod
    def make_target_cls(model_spec, policy_spec):
        """Make a class, the test subject, using rsk_mt.model.ModelledDict."""
        body = {}
        if model_spec:
            body['model'] = model_spec
        if policy_spec:
            body['policy'] = policy_spec
        if body:
            return ModelledDict('Target', (SpecialMethod,), body)
        return ModelledDict.declare('Target', (SpecialMethod,))
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
            self.assertIsInstance(instance, dict)
            self.assertEqual(instance.my_keys(), frozenset(self.initialiser))
        method.__doc__ = f'Test {descr} instance creation'
        return method
    @staticmethod
    def make_test_dict_getitem(descr):
        """Make a function testing dict getitem."""
        def getitem(dct, key):
            """Get value at `key` in `dct`."""
            return dct[key]
        def method(self):
            """Test dict getitem."""
            model = self.target_cls.model
            instance = self.target_cls(self.initialiser)
            for key in model.model_spec:
                if key in instance:
                    self.assertEquals(instance[key], self.initialiser[key])
                else:
                    self.assertEquals(model.is_mandatory(key), False)
                    self.assertEquals(instance.get(key), None)
                    if 'default' in model.model_spec[key]:
                        default = model.model_spec[key]['default']
                        self.assertEquals(model.default_value(key), default)
                        self.assertEquals(instance[key], default)
                    else:
                        self.assertRaises(KeyError, getitem, instance, key)
        method.__doc__ = f'Test {descr} instance getitem'
        return method
    @staticmethod
    def make_test_dict_setitem(descr):
        """Make a function testing dict setitem."""
        def setitem(dct, key, val):
            """Set `key` to `val` in `dct`."""
            dct[key] = val
        def method(self):
            """Test dict setitem."""
            model = self.target_cls.model
            instance = self.target_cls(self.initialiser)
            for key in model.model_spec:
                if key not in instance:
                    # not mandatory
                    instance[key] = 0x0123
                    self.assertEqual(instance[key], 0x0123)
                elif not model.is_constant(key):
                    # not constant
                    instance[key] = 0x89AB
                    self.assertEqual(instance[key], 0x89AB)
                else:
                    # modifiable
                    self.assertRaises(KeyError, setitem, instance, key, 0x4567)
        method.__doc__ = f'Test {descr} dict setitem'
        return method
    @staticmethod
    def make_test_dict_delitem(descr):
        """Make a function testing dict delitem."""
        def getitem(dct, key):
            """Get value at `key` in `dct`."""
            return dct[key]
        def delitem(dct, key):
            """Delete value at `key` in `dct`."""
            del dct[key]
        def method(self):
            """Test dict delitem."""
            model = self.target_cls.model
            instance = self.target_cls(self.initialiser)
            for key in model.model_spec:
                if model.is_mandatory(key):
                    self.assertRaises(KeyError, delitem, instance, key)
                elif key in instance:
                    del instance[key]
                    self.assertEquals(instance.get(key), None)
                    if 'default' in model.model_spec[key]:
                        default = model.model_spec[key]['default']
                        self.assertEquals(model.default_value(key), default)
                        self.assertEquals(instance[key], default)
                    else:
                        self.assertRaises(KeyError, getitem, instance, key)
                else:
                    self.assertEquals(instance.get(key), None)
                    self.assertRaises(KeyError, delitem, instance, key)
        method.__doc__ = f'Test {descr} dict delitem'
        return method
    @staticmethod
    def make_test_dict_clear(descr):
        """Make a function testing dict clear."""
        def method(self):
            """Test dict clear."""
            instance = self.target_cls(self.initialiser)
            instance.clear()
            self.assertEqual(instance.model.mandatory, instance.keys())
        method.__doc__ = f'Test {descr} dict clear'
        return method
    @staticmethod
    def make_test_dict_pop(descr):
        """Make a function testing dict pop."""
        def method(self):
            """Test dict pop."""
            model = self.target_cls.model
            instance = self.target_cls(self.initialiser)
            for key in model.model_spec:
                if model.is_mandatory(key):
                    self.assertRaises(KeyError, instance.pop, key)
                elif key in instance:
                    self.assertEqual(instance.pop(key), self.initialiser[key])
                    self.assertEqual(key in instance, False)
                    self.assertRaises(KeyError, instance.pop, key)
                    self.assertEqual(instance.pop(key, 'foobar'), 'foobar')
                else:
                    self.assertRaises(KeyError, instance.pop, key)
        method.__doc__ = f'Test {descr} dict pop'
        return method
    @staticmethod
    def make_test_dict_popitem(descr):
        """Make a function testing dict popitem."""
        def method(self):
            """Test dict popitem."""
            model = self.target_cls.model
            instance = self.target_cls(self.initialiser)
            while True:
                try:
                    (key, val) = instance.popitem()
                except KeyError:
                    break
                else:
                    self.assertEqual(self.initialiser[key], val)
                    self.assertEqual(model.is_mandatory(key), False)
            self.assertEqual(instance.model.mandatory, instance.keys())
        method.__doc__ = f'Test {descr} dict popitem'
        return method
    @staticmethod
    def make_test_dict_setdefault(descr):
        """Make a function testing dict setdefault."""
        def method(self):
            """Test dict setdefault."""
            model = self.target_cls.model
            instance = self.target_cls(self.initialiser)
            for key in model.model_spec:
                if key in instance:
                    self.assertEquals(
                        instance.setdefault(key),
                        self.initialiser[key],
                    )
                else:
                    try:
                        model.screen_value(key, None)
                    except (TypeError, ValueError):
                        self.assertRaises(
                            (TypeError, ValueError),
                            instance.setdefault,
                            key,
                        )
                    else:
                        self.assertEqual(instance.setdefault(key), None)
                        self.assertEqual(instance[key], None)
                        self.assertEqual(instance.get(key, 'barbaz'), None)
        method.__doc__ = f'Test {descr} dict setdefault'
        return method
    @staticmethod
    def make_test_dict_update(descr):
        """Make a function testing dict update."""
        def method(self):
            """Test dict update."""
            for (other, after) in self.update_success:
                instance = self.target_cls(self.initialiser)
                self.assertEqual(None, instance.update(other))
                self.assertEqual(instance, after)
            for other in self.update_error:
                instance = self.target_cls(self.initialiser)
                before = instance.copy()
                self.assertRaises(
                    (TypeError, ValueError),
                    instance.update,
                    other,
                )
                self.assertEqual(instance, before)
        method.__doc__ = f'Test {descr} dict update'
        return method
    @staticmethod
    def make_test_dict_unmodelled(descr):
        """Make a function testing dict unmodelled pairs."""
        def method(self):
            """Test dict unmodelled pairs."""
            key = 'unmodelled'
            val = ('arbitrary', 'value')
            model = self.target_cls.model
            instance = self.target_cls(self.initialiser)
            self.assertEqual(key in instance, False)
            if model.policy_spec == 'must-accept':
                instance[key] = val
                self.assertEqual(instance[key], val)
                del instance[key]
            else:
                self.assertRaises(KeyError, instance.setdefault, key, val)
            self.assertEqual(key in instance, False)
        method.__doc__ = f'Test {descr} dict unmodelled pairs'
        return method

MODEL_SPEC = {
    'quuz': {
        # empty
    },
    'thud': {
        'value_type': Integer(),
        'default': 66,
    },
    'wibble': {
        'value_type': Integer(),
        'mandatory': True,
    },
    'wobble': {
        'constant': True,
    },
    'quux': {
        'constant': True,
        'default': 'abcdef',
    },
    'corge': {
        'mandatory': True,
        'constant': True,
    },
}

INITIALISER = {
    'wibble': -123456,
    'wobble': [0.5],
    'quux': {"abc": "def"},
    'corge': [None, False],
}

UPDATE_SUCCESS_UNDERSTAND = [(None, {
    'wibble': -123456,
    'wobble': [0.5],
    'quux': {"abc": "def"},
    'corge': [None, False],
}), ({
    # empty
}, {
    'wibble': -123456,
    'wobble': [0.5],
    'quux': {"abc": "def"},
    'corge': [None, False],
}), ({
    'thud': -1,
}, {
    'thud': -1,
    'wibble': -123456,
    'wobble': [0.5],
    'quux': {"abc": "def"},
    'corge': [None, False],
}), ({
    'wibble': 76,
}, {
    'wibble': 76,
    'wobble': [0.5],
    'quux': {"abc": "def"},
    'corge': [None, False],
}), ({
    'thud': 1,
    'wibble': 2,
}, {
    'thud': 1,
    'wibble': 2,
    'wobble': [0.5],
    'quux': {"abc": "def"},
    'corge': [None, False],
})]

UPDATE_SUCCESS_IGNORE = UPDATE_SUCCESS_UNDERSTAND

UPDATE_SUCCESS_ACCEPT = UPDATE_SUCCESS_UNDERSTAND + [({
    'unmodelled': 'any',
}, {
    'wibble': -123456,
    'wobble': [0.5],
    'quux': {"abc": "def"},
    'corge': [None, False],
    'unmodelled': 'any',
}), ({
    'unmodelled': 'any',
    'wibble': 543,
}, {
    'wibble': 543,
    'wobble': [0.5],
    'quux': {"abc": "def"},
    'corge': [None, False],
    'unmodelled': 'any',
})]

UPDATE_ERROR_ACCEPT = [{
    'thud': 'not-an-integer',
}, {
    'thud': 123,
    'wibble': 'not-an-integer',
}, {
    'wobble': 'cannot change constant',
}, {
    'thud': 123,
    'corge': 'cannot change constant',
}]

UPDATE_ERROR_UNDERSTAND = UPDATE_ERROR_ACCEPT + [{
    'unmodelled': 'any',
}, {
    'thud': 98,
    'unmodelled': 'any',
}]

UPDATE_ERROR_IGNORE = UPDATE_ERROR_UNDERSTAND

# TestDefined*: define model and policy at class creation time

class TestDefinedMustUnderstand(TestCase, metaclass=_ModelledDictTestBuilder):
    """Tests for rsk_mt.model.ModelledDict defined, policy must-understand."""
    model_spec = MODEL_SPEC
    policy_spec = 'must-understand'
    initialiser = INITIALISER
    update_success = UPDATE_SUCCESS_UNDERSTAND
    update_error = UPDATE_ERROR_UNDERSTAND

class TestDefinedMustIgnore(TestCase, metaclass=_ModelledDictTestBuilder):
    """Tests for rsk_mt.model.ModelledDict defined, policy must-ignore."""
    model_spec = MODEL_SPEC
    policy_spec = 'must-ignore'
    initialiser = INITIALISER
    update_success = UPDATE_SUCCESS_IGNORE
    update_error = UPDATE_ERROR_IGNORE

class TestDefinedMustAccept(TestCase, metaclass=_ModelledDictTestBuilder):
    """Test for rsk_mt.model.ModelledDict defined, policy must-accept."""
    model_spec = MODEL_SPEC
    policy_spec = 'must-accept'
    initialiser = INITIALISER
    update_success = UPDATE_SUCCESS_ACCEPT
    update_error = UPDATE_ERROR_ACCEPT

# TestDelayed*: define policy at class creation time, model later

class TestDelayedMustUnderstand(TestCase, metaclass=_ModelledDictTestBuilder):
    """Tests for rsk_mt.model.ModelledDict delayed, policy must-understand."""
    initialiser = INITIALISER
    policy_spec = 'must-understand'
    update_success = UPDATE_SUCCESS_UNDERSTAND
    update_error = UPDATE_ERROR_UNDERSTAND
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pylint: disable=no-member
        if not self.target_cls.model.defined:
            self.target_cls.define(MODEL_SPEC, self.policy_spec)

class TestDelayedMustIgnore(TestCase, metaclass=_ModelledDictTestBuilder):
    """Tests for rsk_mt.model.ModelledDict delayed, policy must-ignore."""
    initialiser = INITIALISER
    policy_spec = 'must-ignore'
    update_success = UPDATE_SUCCESS_IGNORE
    update_error = UPDATE_ERROR_IGNORE
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pylint: disable=no-member
        if not self.target_cls.model.defined:
            self.target_cls.define(MODEL_SPEC, self.policy_spec)

class TestDelayedMustAccept(TestCase, metaclass=_ModelledDictTestBuilder):
    """Tests for rsk_mt.model.ModelledDict delayed, policy must-accept."""
    initialiser = INITIALISER
    policy_spec = 'must-accept'
    update_success = UPDATE_SUCCESS_ACCEPT
    update_error = UPDATE_ERROR_ACCEPT
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pylint: disable=no-member
        if not self.target_cls.model.defined:
            self.target_cls.define(MODEL_SPEC, self.policy_spec)

# TestDeclared*: define model and policy after class creation time

class TestDeclaredMustUnderstand(TestCase, metaclass=_ModelledDictTestBuilder):
    """Tests for rsk_mt.model.ModelledDict declared, policy must-understand."""
    initialiser = INITIALISER
    update_success = UPDATE_SUCCESS_UNDERSTAND
    update_error = UPDATE_ERROR_UNDERSTAND
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pylint: disable=no-member
        if not self.target_cls.model.defined:
            self.target_cls.model.policy_spec = 'must-understand'
            self.target_cls.define(MODEL_SPEC)

class TestDeclaredMustIgnore(TestCase, metaclass=_ModelledDictTestBuilder):
    """Tests for rsk_mt.model.ModelledDict declared, policy must-ignore."""
    initialiser = INITIALISER
    update_success = UPDATE_SUCCESS_IGNORE
    update_error = UPDATE_ERROR_IGNORE
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pylint: disable=no-member
        if not self.target_cls.model.defined:
            self.target_cls.model.policy_spec = 'must-ignore'
            self.target_cls.define(MODEL_SPEC)

class TestDeclaredMustAccept(TestCase, metaclass=_ModelledDictTestBuilder):
    """Tests for rsk_mt.model.ModelledDict declared, policy must-accept."""
    initialiser = INITIALISER
    update_success = UPDATE_SUCCESS_ACCEPT
    update_error = UPDATE_ERROR_ACCEPT
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pylint: disable=no-member
        if not self.target_cls.model.defined:
            self.target_cls.model.policy_spec = 'must-accept'
            self.target_cls.define(MODEL_SPEC)

class TestCornerCasesMustAccept(TestCase):
    """Tests for rsk_mt.model.ModelledDict policy must-accept corner cases."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        body = {'model': {}, 'policy': 'must-accept'}
        self.target_cls = ModelledDict('Target', (), body)
    def test_corner_case_update(self):
        """Test rsk_mt.model.ModeledDict policy must-accept update corner case"""
        instance = self.target_cls({'unmodelled': 'initial value'})
        self.assertEqual(instance, {'unmodelled': 'initial value'})
        # pylint: disable=no-member
        instance.update({'unmodelled': 'updated value'})
        self.assertEqual(instance, {'unmodelled': 'updated value'})
