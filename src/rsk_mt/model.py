### SPDX-License-Identifier: GPL-2.0-or-later

"""Data structure values enforced by a class-specific model and policy.

A model defines acceptable value structures for instances of a modelled class.

A policy specifies modelled class behaviour during instance initialisation and
instance value modification (set, delete) after initialisation.

The policies:

* 'must-understand' provides a strict protocol.

The type model is strictly and exclusively enforced. When initialising an
instance of a modelled class, only values for elements defined in the model are
accepted: supplying values for elements which are not defined in the model is an
error. Only values for elements defined in the model may be set or deleted after
initialisation (subject to constraints specified in the model).

* 'must-ignore' provides a flexible protocol.

The type model is strictly enforced for elements defined in the model. When
initialising an instance of a modelled class, values for elements not defined in
the model are accepted and silently discarded. Only values for elements defined
in the model may be set or deleted after initialisation (subject to constraints
specified in the model).

* 'must-accept' provides a permissive protocol.

The type model is strictly enforced for elements defined in the model: elements
not defined in the model are not subject to any restrictions. When initialising
an instance of a modelled class, values for elements not defined in the model
may be accepted: supplying values for elements not defined in the model is not
normally an error. Any element values may be set or deleted after
initialisation. Only elements defined in the model are subject to its specified
constraints.

.. |ValueType| replace:: :class:`ValueType <rsk_mt.enforce.value.ValueType>`
.. |TypeError| replace:: :class:`TypeError`
.. |ValueError| replace:: :class:`ValueError`
.. |KeyError| replace:: :class:`KeyError`

.. |NotDefinedError| replace:: :class:`NotDefinedError`
.. |AlreadyDefinedError| replace:: :class:`AlreadyDefinedError`
"""

from rsk_mt.enforce.value import (
    ValueType,
    Any,
    Enum,
)

POLICY = Enum((
    'must-understand',
    'must-ignore',
    'must-accept',
))

class NotDefinedError(Exception):
    """An exception indicating a type model is not yet defined.

    Used to indicate that the type model for `cls` is not yet defined and there
    was an attempt to validate data using `cls` or an instance of `cls`.
    """
    def __init__(self, cls):
        super().__init__()
        self.modelled_cls = cls

class AlreadyDefinedError(Exception):
    """An exception indicating a type model is already defined.

    Used to indicate that the type model for `cls` is already defined and there
    was an attempt to redefine it.
    """
    def __init__(self, cls):
        super().__init__()
        self.modelled_cls = cls

def _modelled_define(cls, model_spec, policy_spec=None):
    """Define the type model for `cls` from `model_spec`.

    Raise |AlreadyDefinedError| if the model for `cls` is already defined.
    If `policy_spec` is not None then also set the policy.
    """
    try:
        cls.model.model_spec = model_spec
    except AlreadyDefinedError as err:
        raise AlreadyDefinedError(cls) from err
    if policy_spec is not None:
        cls.model.policy_spec = policy_spec
    return cls

def _modelled_init_mutable(bases, body):
    """Make a function for use as __init__ of a specialised mutable type.

    The __init__ method of the first base in `bases` is called with the value
    supplied to the function. After initialisation of that first base, the
    function calls the __init__ method specified in `body` to perform class-
    specific initialisation. If there is no __init__ method in `body`, then the
    __init__ method for each other base in `bases` is called. (No value is
    supplied to these subsequent calls.)
    """
    def init(self, val=()):
        """Initialise `self`, a specialised class instance, from `val`."""
        try:
            val = self.model(val)
        except NotDefinedError as err:
            raise NotDefinedError(self.__class__) from err
        # init the type that is being specialised with `val`
        bases[0].__init__(self, val)
        # init other bases
        if '__init__' in body:
            # class-specific initialisation
            body['__init__'](self)
        else:
            # other bases initialisation
            for base in bases[1:]:
                base.__init__(self)
    return init

def _modelled_new_immutable(base):
    """Make a function for use as __new__ of a specialised immutable type.

    A __new__ method must be used to supply the initialisation value for an
    immutable class instance: a value cannot be supplied using a __init__ method
    (attempting this raises |TypeError|).
    """
    def new(cls, val=()):
        """Create a specialised class instance from `val`."""
        try:
            val = cls.model(val)
        except NotDefinedError as err:
            raise NotDefinedError(cls) from err
        else:
            return base.__new__(cls, val)
    return new

def _modelled_init_immutable(bases, body):
    """Make a function for use as __init__ of a specialised immutable type.

    The __init__ method of the first base in `bases` is called. After
    initialisation of that first base, the function calls the __init__ method
    specified in `body` to perform class-specific initialisation. If there is no
    __init__ method in `body`, then the __init__ method for each other base in
    `bases` is called. (No value is supplied to any of these calls.)
    """
    def init(self, val=None): # pylint: disable=unused-argument
        """Initialise `self`, a specialised class instance, ignoring `val`."""
        # init the type that is being specialised
        bases[0].__init__(self)
        # init other bases
        if '__init__' in body:
            # class-specific initialisation
            body['__init__'](self)
        else:
            # other bases initialisation
            for base in bases[1:]:
                base.__init__(self)
    return init

class Model(ValueType):
    """A model codifying enforcement rules for specialised classes.

    A model codifying enforcement rules for creating, accessing and modifying
    instances of a specialised class. The enforcement rules are specified in
    `model_spec` and `policy_spec`.
    """
    def __init__(self, model_spec, policy_spec):
        super().__init__()
        self._model_spec = None
        self._policy_spec = None
        self.model_spec = model_spec
        self.policy_spec = policy_spec
    def _define(self):
        """Perform class-specific model definition using :attr:`model_spec`."""
        raise NotImplementedError
    @property
    def defined(self):
        """Return True if the model spec is defined. Otherwise return False."""
        return self._model_spec is not None
    @property
    def model_spec(self):
        """Return the model spec if it is defined. Otherwise return None."""
        return dict(self._model_spec) if self.defined else None
    @model_spec.setter
    def model_spec(self, val):
        """Set the model spec from `val` then define the model.

        Raise |AlreadyDefinedError| if the model is already defined. If `val` is
        None do not attempt to change the model. Otherwise raise |ValueError| if
        `val` is not a dict.
        """
        if self.defined:
            raise AlreadyDefinedError(self.__class__)
        if val is None:
            return
        if not isinstance(val, dict):
            raise ValueError(val)
        self._model_spec = val
        self._define()
    @property
    def policy_spec(self):
        """Return the policy spec."""
        return self._policy_spec
    @policy_spec.setter
    def policy_spec(self, policy):
        """Set the policy spec from `policy`.

        Raise |ValueError| if `policy` is not a supported :data:`POLICY`.
        """
        self._policy_spec = POLICY(policy)

class MappingModel(Model):
    """A model codifying enforcement rules for specialised mappings.

    A mapping model is a |ValueType| enforcing the type model specified in
    `model_spec` and `policy_spec` upon a mapping value. When creating a mapping
    model, `model_spec` may be None. In this case, the model must be supplied by
    setting :attr:`model_spec` before using this instance. `policy_spec` must be
    a supported :data:`POLICY` value.
    """
    def _define(self):
        raise NotImplementedError
    def default_value(self, key): # pylint: disable=no-self-use
        """Return the default value for `key`.

        Raise |KeyError| if there is no default value.
        """
        raise KeyError(key)
    def screen_setitem(self, mapping, key, val): # pylint: disable=no-self-use
        """Screen setting `key` to `val` in `mapping`.

        If a pair formed from `key` and `val` may be set in `mapping`, then
        return the pair to set. Raise |ValueError| if the pair cannot be set
        because `val` does not conform to the model for this pair. Raise
        |KeyError| if the pair cannot be set for any other reason.
        """
        raise KeyError(key)
    def screen_moditem(self, mapping, key, val): # pylint: disable=no-self-use
        """Screen modifying `key` to `val` in `mapping`.

        If a pair formed from `key` and `val` may modify the existing pair value
        in `mapping`, then return the pair to set. Raise |ValueError| if the
        pair cannot be modified because `val` does not conform to the model for
        this pair. Raise |KeyError| if the pair cannot be modified for any other
        reason.
        """
        raise KeyError(key)
    def screen_delitem(self, mapping, key): # pylint: disable=no-self-use,unused-argument
        """Screen deleting `key` in `mapping`.

        Return `key` if the pair at `key` may be deleted from `mapping`. Raise
        |KeyError| if the pair cannot be deleted for any reason.
        """
        return key
    def screen_update(self, mapping, other): # pylint: disable=no-self-use,unused-argument
        """Screen updating `mapping` with `other`.

        If `other` can be used to update `mapping`, then return a dict to use
        for the update. Raise |ValueError| if `other` cannot be applied for any
        reason.
        """
        if other:
            raise ValueError(other)
        return other
    def pairs_free(self, mapping): # pylint: disable=no-self-use
        """Return a set of keys which may be freely removed from `mapping`."""
        return set(mapping)

class DictModel(MappingModel):
    """A model codifying enforcement rules for specialised dicts.

    A dict model is a |ValueType| enforcing the type model specified in
    `model_spec` and `policy_spec` upon a dict value. `model_spec` is a dict
    mapping keys to pair models. A pair model is a dict which may specify:

    * 'value_type': a |ValueType| instance for enforcing a pair's value before
    setting it (default: an instance of :class:`rsk_mt.enforce.value.Any`)

    * 'mandatory': a boolean indicating whether a dict must always have a value
    for this pair (must be initialised and cannot be deleted) (default: False)

    * 'constant': a boolean indicating whether a pair's value can be changed
    after it has been set (default: False)

    * 'default': a value to be returned when getting the pair's value if no
    value is explicitly set. A default value should conform to this pair's
    'value_type' (though this is not enforced).
    """
    def __init__(self, model_spec, policy_spec):
        self._pair_model = {}
        self._mandatory_pairs = frozenset()
        super().__init__(model_spec, policy_spec)
    def _define(self):
        mandatory_pairs = set()
        for key in self._model_spec:
            self._pair_model[key] = self._to_pair_model(self._model_spec[key])
            if self.is_mandatory(key):
                mandatory_pairs.add(key)
        self._mandatory_pairs = frozenset(mandatory_pairs)
    def __iter__(self):
        """Yield the pair keys in the model spec."""
        if self.defined:
            for key in self._model_spec:
                yield key
    @property
    def mandatory(self):
        """A frozenset of the keys of mandatory pairs."""
        return self._mandatory_pairs
    @staticmethod
    def _to_pair_model(spec):
        """Return a pair model from `spec`."""
        model = {}
        model['value_type'] = spec.get('value_type', Any())
        if not isinstance(model['value_type'], ValueType):
            raise ValueError(model['value_type'])
        model['mandatory'] = bool(spec.get('mandatory', False))
        model['constant'] = bool(spec.get('constant', False))
        try:
            model['default'] = spec['default']
        except KeyError:
            # omit 'default' to cause a |KeyError| to be raised
            # when attempting to access it
            pass
        return model
    def screen_value(self, key, val):
        """Screen value for the pair at `key` from value `val`.

        Return a value for setting at `key` from `val`. Raise |KeyError| if
        there is no model for `key`. Raise |TypeError| or |ValueError| if `val`
        does not conform to the model value type at `key`.
        """
        return self._pair_model[key]['value_type'](val)
    def is_mandatory(self, key):
        """Return True if the pair at `key` is mandatory, False otherwise.

        Raise |KeyError| if there is no model for `key`.
        """
        return self._pair_model[key]['mandatory']
    def is_constant(self, key):
        """Return True if the pair at `key` is constant, False otherwise.

        Raise |KeyError| if there is no model for `key`.
        """
        return self._pair_model[key]['constant']
    def default_value(self, key):
        """Return the default value for the pair at `key`.

        Raise |KeyError| if there is no model for `key`.
        Raise |KeyError| if there is no default value for `key`.
        """
        return self._pair_model[key]['default']
    def screen_setitem(self, mapping, key, val):
        try:
            val = self.screen_value(key, val)
        except KeyError:
            if self.policy_spec != 'must-accept':
                raise
        return (key, val)
    def screen_moditem(self, mapping, key, val):
        try:
            constant = self.is_constant(key)
        except KeyError:
            pass
        else:
            if constant:
                raise KeyError(key)
        try:
            val = self.screen_value(key, val)
        except KeyError:
            pass
        return (key, val)
    def screen_delitem(self, mapping, key):
        try:
            mandatory = self.is_mandatory(key)
        except KeyError:
            pass
        else:
            if mandatory:
                raise KeyError(key)
        return key
    def screen_update(self, mapping, other):
        for key in other:
            try:
                if key in mapping:
                    self.screen_moditem(mapping, key, other[key])
                else:
                    self.screen_setitem(mapping, key, other[key])
            except (KeyError, TypeError, ValueError) as err:
                raise ValueError(other) from err
        return other
    def pairs_free(self, mapping):
        return set(mapping) - self.mandatory
    def check(self, val):
        try:
            dict(val)
        except (TypeError, ValueError):
            return False
        else:
            return True
    def __call__(self, val):
        """Enforce this specialised dict model on `val`.

        Return a :class:`dict` value conforming to this model and policy from
        `val`, where `val` specifies key/value pairs. Raise |TypeError| or
        |ValueError| if the input value does not conform to the type model.
        Raise |NotDefinedError| if the type model is not yet defined.
        """
        val = dict(val)
        if not self.defined:
            raise NotDefinedError(self.__class__)
        formed = {}
        for key in val:
            try:
                formed[key] = self.screen_value(key, val[key])
            except KeyError:
                if self._policy_spec == 'must-understand':
                    raise ValueError(f'value not allowed at {key}') from None
                if self._policy_spec == 'must-accept':
                    formed[key] = val[key]
                # else self._policy_spec == 'must-ignore' => discard
            except (TypeError, ValueError) as err:
                reason = f'bad value for {key}: {str(err)}'
                raise err.__class__(reason) from None
        missing = self.mandatory - formed.keys()
        if missing:
            raise ValueError(f'missing values at {", ".join(missing)}')
        return formed

def _modelled_dict_missing(self, key):
    """Return the default value at `key` in specialised dict `self`."""
    return self.model.default_value(key)

def _modelled_dict_setitem(self, key, val):
    """Set the value at `key` in specialised dict `self` using value `val`."""
    if key in self:
        (key, val) = self.model.screen_moditem(self, key, val)
    else:
        (key, val) = self.model.screen_setitem(self, key, val)
    # perform set using base (dict) method
    super(self.__class__, self).__setitem__(key, val)

def _modelled_dict_delitem(self, key):
    """Delete the value at `key` in specialised dict `self`."""
    key = self.model.screen_delitem(self, key)
    # perform delete using base (dict) method
    super(self.__class__, self).__delitem__(key)

def _modelled_dict_clear(self):
    """Remove all free pairs from specialised dict `self`."""
    for key in self.model.pairs_free(self):
        del self[key]

def _modelled_dict_pop(self, key, default=None):
    """Remove `key` from specialised dict `self`, or return `default`."""
    if key in self:
        val = self[key]
        del self[key]
        return val
    if default is None:
        raise KeyError(key)
    return default

def _modelled_dict_popitem(self):
    """Pop one item which may be freely removed from specialised dict `self`."""
    # popping an empty set raises KeyError, which is desired behaviour here
    key = self.model.pairs_free(self).pop()
    val = self[key]
    del self[key]
    return (key, val)

def _modelled_dict_setdefault(self, key, default=None):
    """Return the value at `key` in specialised dict `self`.

    If there is no value at `key`, set `key` to `default` and return `default`.
    """
    if key in self:
        return self[key]
    self[key] = default
    return default

def _modelled_dict_update(self, other=None):
    """Update specialised dict `self` with (key, val) pairs from `other`."""
    if not other:
        return
    # screen other
    other = self.model.screen_update(self, dict(other))
    # update self
    for key in other:
        # perform set using base (dict) method
        super(self.__class__, self).__setitem__(key, other[key])

class ModelledDict(type):
    """A metaclass for constructing specialised dict classes.

    A metaclass for constructing specialised dict classes whose instances are
    managed by a class-specific model and policy.

    Each instance of a specialised dict class is still a :class:`dict`. As such
    the instance may be readily mixed with native Python values and may be
    JSON-encoded without the need for custom encoding. Base dict methods are
    supported, with specialisation of behaviour noted at the end of this
    docstring.

    The specialisation delivers managed initialisation, modification and access
    to the dict, subject to the class model and policy. The specialised class
    may define its own methods to provide a semantic layer above the base dict
    store.

    A class using this metaclass should normally set a 'model' class attribute,
    a dict defining constraints upon the mapping items. The class may also set
    a 'policy' class attribute to specify how to handle pairs not in the
    'model'. The 'policy' value must be a :data:`POLICY` value; the default
    policy is 'must-understand'.

    The 'model' value (or None, if not set) and 'policy' values are used to
    create a type model at class construction time. The type model is an
    instance of 'model_cls', if specified in the creating class, or, by default,
    :class:`DictModel`. The type model instance must implement |ValueType|. When
    a new instance of the specialised dict class is created, the type model's
    |ValueType| is called as a function to enforce the model and policy on the
    supplied input value.

    Specifying the class 'model' and 'policy' may be deferred until after class
    creation, in order to allow a class to be forward-declared. This allows the
    class model to reference itself, directly or indirectly. After the class
    model has been defined, by calling the class's 'define' method, the model
    and policy cannot be changed.

    The type model instance shall raise |NotDefinedError| if its |ValueType|
    is called before its model and policy have been defined.

    With regard to use of standard dict methods, the following behaviours are
    observed:

    **d[key]**

    Return the item of *d* at *key*. If *key* is not in the map and the type
    model has a default value for *key*, then return that default value. (The
    default value is returned by the specialised dict class implementation of
    :meth:`object.__missing__`.) The type model must implement
    :meth:`MappingModel.default_value`. Otherwise, raise |KeyError|.

    **d[key] = value**

    Set the item of *d* at *key* to a value formed from *value*. Raise
    |ValueError| if the type model cannot form a value from *value*. Raise
    |KeyError| if a value cannot be set at *key* for any other reason. The type
    model must implement :meth:`MappingModel.screen_setitem` and
    :meth:`MappingModel.screen_moditem`.

    **del d[key]**

    Delete the item at *key* from *d*. Raise |KeyError| if *key* is not in the
    map or if the pair cannot be deleted for any other reason. The type model
    must implement :meth:`MappingModel.screen_delitem`.

    **clear()**

    Delete all items from the mapping which can be freely deleted without
    violating the type model. The type model must implement
    :meth:`MappingModel.pairs_free`.

    **copy()**

    This base method is not overridden/its behaviour is not specialised.
    :meth:`dict.copy` returns a shallow copy of the dictionary, a :class:`dict`
    instance.

    **get(key[, default])**

    This base method is not overridden/its behaviour is not specialised.
    :meth:`dict.get` does not call :meth:`object.__missing__` so any type model
    default value at *key* is not used. Therefore the caller can use this method
    to determine whether a value has been explicitly set. The caller may also
    use this method where *default* is required as a specific override of the
    type model default value for *key*.

    **pop(key[, default])**

    If *key* is in the map, remove it and return its value, otherwise return
    *default*. If the type model does not allow *key* to be removed, or
    *default* is not given and *key* is not in the map, raise |KeyError|.
    The type model must implement :meth:`MappingModel.screen_delitem`.

    **popitem()**

    Remove and return an arbitrary (key, val) pair from the map. Only pairs
    which be freely removed without violating the type model are removed. Raise
    |KeyError| when there are no such pairs left to remove. The type model must
    implement :meth:`MappingModel.pairs_free`.

    **setdefault(key[, default])**

    If *key* is in the map, return its value. If not, insert *key* into the map
    with a value of *default* and return *default*. When inserting *key* into
    the map, the behaviour of __setitem__ (as above for **d[key] = value**) is
    respected.

    **update([other])**

    Update the map with the key/value pairs from *other*, overwriting existing
    keys. Return None. The type model must be observed such that either all
    pairs in *other* are updated or none are updated. Raise |ValueError| if
    updating from *other* would result in the map violating the type model. The
    type model must implement :meth:`MappingModel.screen_update`.
    """
    def __new__(cls, name, bases, dct):
        name = str(name)
        obases = list(bases)
        dct = dict(dct)
        # order bases: ensure dict first
        try:
            obases.remove(dict)
        except ValueError:
            pass
        obases.insert(0, dict)
        bases = tuple(obases)
        # get the type model class
        model_cls = dct.get('model_cls', DictModel)
        # get the class 'model' specification
        try:
            model_spec = dict(dct['model'])
        except KeyError:
            # No model defined, usually for the purposes of creating a forward
            # declaration/self-reference. The model must be defined before
            # using an instance of this class.
            model_spec = None
        # get the class 'policy' specification
        policy_spec = dct.get('policy', 'must-understand')
        # build the class body...
        # ...from specified methods and attributes in `dct`
        body = dict(dct)
        # ...overriding with ModelledDict methods and attributes
        body.update({
            # class-related
            'model': model_cls(model_spec, policy_spec),
            'define': classmethod(_modelled_define),
            # instance-related
            '__init__': _modelled_init_mutable(bases, dct),
            '__missing__': _modelled_dict_missing,
            '__setitem__': _modelled_dict_setitem,
            '__delitem__': _modelled_dict_delitem,
            'clear': _modelled_dict_clear,
            'pop': _modelled_dict_pop,
            'popitem': _modelled_dict_popitem,
            'setdefault': _modelled_dict_setdefault,
            'update': _modelled_dict_update,
        })
        return super().__new__(cls, name, bases, body)
    @classmethod
    def declare(cls, name, bases=(dict,)):
        """Forward declare a class whose model will be defined later.

        This method allows a class to be forward-declared in order that its
        model may refer to itself. Before the class can be used its model
        must be set by calling `cls.define()`.
        """
        return cls(name, bases, {})

class SequenceModel(Model):
    """A model codifying enforcement rules for specialised sequences.

    A sequence model is a |ValueType| enforcing the type model specified in
    `model_spec` and `policy_spec` upon a sequence value. `model_spec` is a
    dict specifying constraints upon the sequence elements. It may specify:

    * 'head': a sequence of |ValueType| instances which specify the value types
    of the first N elements of a valid data value. Note that the length of
    'head' does not imply a minimum length for a valid value; only that any
    values which are supplied for the first N elements of a data value must
    conform to the value type at the corresponding index in 'head'.

    * 'tail': a |ValueType| instance specifying the value type of any element
    values supplied after the 'head' element values. Note that the presence of a
    'tail' does not require that a data value supplies any values after the
    'head'. Also note that the absence of 'tail' may imply a maximum length for
    a valid value, conditional upon the value of `policy_spec`. In this case:
    when `policy_spec` is 'must-understand', then no data values may be supplied
    after 'head'; when `policy_spec` is 'must-accept', there is no constraint on
    the value type of data values supplied after 'head'; when `policy_spec` is
    'must-ignore', then any data values supplied after 'head' are silently
    discarded.

    * 'length': a 2-tuple, the (min, max) length of a valid data value. 'min'
    must be a non-negative integer: a valid data value must have a length
    greater than or equal to the 'min' length. 'max' must be either a
    non-negative integer or None: when a non-negative integer, a valid data
    value must have a length less than or equal to the 'max' length; when
    None, there is no upper bound on data value length. If 'length' is not
    specified then there is no explicit constraint on data value length.

    * 'unique': a boolean specifying whether all element values in a valid data
    value must be unique or not. If 'unique' is not supplied then element values
    are not required to be unique.

    * 'condition': a function returning True if the element values in a data
    value satisfy the condition defined by the function. If 'condition' is not
    specified then data values implicitly pass.

    When creating a sequence model, `model_spec` may be None. In this case, the
    model must be supplied by setting :attr:`model_spec` before using this
    instance. `policy_spec` must be a supported :data:`POLICY` value.
    """
    def __init__(self, model_spec, policy_spec):
        self._head = ()
        self._tail = None
        self._min = 0
        self._max = None
        self._unique = False
        self._condition = None
        super().__init__(model_spec, policy_spec)
    def _define(self):
        self._head = self._model_spec.get('head', ())
        for value_type in self._head:
            if not isinstance(value_type, ValueType):
                raise ValueError(f'bad value type in head {self._head}')
        self._tail = self._model_spec.get('tail')
        if self._tail and not isinstance(self._tail, ValueType):
            raise ValueError(f'bad value type in tail {self._tail}')
        try:
            self._min = int(self._model_spec['length'][0])
        except KeyError:
            self._min = 0
        try:
            self._max = int(self._model_spec['length'][1])
        except (KeyError, TypeError):
            self._max = None
        self._unique = bool(self._model_spec.get('unique', False))
        self._condition = self._model_spec.get('condition')
    def check(self, val):
        try:
            iter(val)
        except (TypeError, ValueError):
            return False
        else:
            return True
    def __call__(self, val):
        """Enforce this specialised sequence model on `val`.

        Return a :class:`list` value conforming to this model and policy from
        `val`, where `val` is a sequence value. Raise |TypeError| or
        |ValueError| if the input value does not conform to the type model.
        Raise |NotDefinedError| if the type model is not yet defined.
        """
        val = tuple(val)
        if not self.defined:
            raise NotDefinedError(self.__class__)
        formed = []
        idx = 0
        # form head elements
        while idx < len(val):
            try:
                formed.append(self._head[idx](val[idx]))
            except IndexError:
                break
            except (TypeError, ValueError) as err:
                reason = f'bad value at #{idx}: {str(err)}'
                raise err.__class__(reason) from None
            idx += 1
        # form tail elements
        while idx < len(val):
            if self._tail:
                try:
                    formed.append(self._tail(val[idx]))
                except (TypeError, ValueError) as err:
                    reason = f'bad value at #{idx}: {str(err)}'
                    raise err.__class__(reason) from None
            elif self._policy_spec == 'must-understand':
                raise ValueError(f'value not allowed at #{idx}')
            elif self._policy_spec == 'must-accept':
                formed.append(val[idx])
            # else self._policy_spec == 'must-ignore' => discard
            idx += 1
        error = False
        error = error or (len(formed) < self._min)
        error = error or ((self._max is not None) and self._max < len(formed))
        error = error or (self._unique and len(formed) != len(frozenset(formed)))
        error = error or (self._condition and not bool(self._condition(formed)))
        if error:
            raise ValueError(val)
        return formed

class ModelledTuple(type): # pylint: disable=too-few-public-methods
    """A metaclass for constructing specialised tuple classes.

    A metaclass for constructing specialised tuple classes whose instances are
    managed by a class-specific model and policy.

    Each instance of a specialised tuple class is still a :class:`tuple`. As
    such, the instance may be readily mixed with native Python values and may
    be JSON-encoded without the need for custom encoding. As with standard tuple
    values, modelled tuples are immutable: a new value can only be created by
    instantiating a new instance of the specialised tuple class.

    The specialisation delivers managed initialisation and access to the tuple,
    subject to the class model and policy. The specialised class may define its
    own methods to provide a semantic layer above the base tuple sequence.

    A class using this metaclass should normally set a 'model' class attribute,
    a dict defining constraints upon the sequence items. The class may also set
    a 'policy' class attribute to specify how to handle items not in the model.
    The 'policy' value must be a :data:`POLICY` value; the default policy is
    'must-understand'.

    The 'model' value (or None, if not set) and 'policy' values are used to
    create a type model at class construction time. The type model is an
    instance of 'model_cls', if specified in the creating class, or, by default,
    :class:`SequenceModel`. The type model instance must implement |ValueType|.
    When a new instance of the specialised tuple class is created, the type
    model's |ValueType| is called as a function to enforce the model and policy
    on the supplied input value.

    Specifying the class 'model' and 'policy' may be deferred until after class
    creation, in order to allow a class to be forward-declared. This allows the
    class model to reference itself, directly or indirectly. After the class
    model has been defined, by calling the class's 'define' method, the model
    and policy cannot be changed.

    The type model instance shall raise |NotDefinedError| if its |ValueType|
    is called before its model and policy have been defined.
    """
    def __new__(cls, name, bases, dct):
        name = str(name)
        obases = list(bases)
        dct = dict(dct)
        # order bases: ensure tuple first
        try:
            obases.remove(tuple)
        except ValueError:
            pass
        obases.insert(0, tuple)
        bases = tuple(obases)
        # get the type model class
        model_cls = dct.get('model_cls', SequenceModel)
        # get the class 'model' specification
        try:
            model_spec = dict(dct['model'])
        except KeyError:
            # No model defined, usually for the purposes of creating a forward
            # declaration/self-reference. The model must be defined before
            # using an instance of this class.
            model_spec = None
        # get the class 'policy' specification
        policy_spec = dct.get('policy', 'must-understand')
        # build the class body...
        # ...from specified methods and attributes in `dct`
        body = dict(dct)
        # ...overriding with ModelledTuple methods and attributes
        body.update({
            # class-related
            'model': model_cls(model_spec, policy_spec),
            'define': classmethod(_modelled_define),
            # instance-related
            '__new__': _modelled_new_immutable(bases[0]),
            '__init__': _modelled_init_immutable(bases, dct),
        })
        return super().__new__(cls, name, bases, body)
    @classmethod
    def declare(cls, name, bases=(tuple,)):
        """Forward declare a class whose model will be defined later.

        This method allows a class to be forward-declared in order that its
        model may refer to itself. Before the class can be used its model
        must be set by calling `cls.define()`.
        """
        return cls(name, bases, {})
