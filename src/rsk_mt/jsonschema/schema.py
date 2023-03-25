### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long
"""`JSON Schema Core`_ and `JSON Schema Validation`_.

.. |KeyError| replace:: :class:`KeyError`

.. |frozenset| replace:: :class:`frozenset`
.. |ValueType| replace:: :class:`ValueType <rsk_mt.enforce.value.ValueType>`
.. |Encoder| replace:: :class:`Encoder <rsk_mt.enforce.encoding.Encoder>`
.. |Validator| replace:: :class:`Validator <rsk_mt.jsonschema.validators.validator.Validator>`
.. |Format| replace:: :class:`Format <rsk_mt.jsonschema.formats.format.Format>`
.. |Encoding| replace:: :class:`Encoding <rsk_mt.jsonschema.encodings.encoding.Encoding>`
.. |Optimiser| replace:: :class:`Optimiser <rsk_mt.jsonschema.schema.Optimiser>`

.. |ApplicationSupport| replace:: :class:`Application Support <Support>`
.. |Identifiers| replace:: :class:`identifiers <rsk_mt.jsonschema.identifiers.Identifiers>`

.. _$id: https://tools.ietf.org/html/draft-handrews-json-schema-01#section-8.2
.. _$ref: https://tools.ietf.org/html/draft-handrews-json-schema-01#section-8.3
.. _type: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.1.1
.. _title: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-10.1
.. _description: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-10.1
.. _default: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-10.2
.. _contentEncoding: https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-8.3

.. _JSON Pointer: https://tools.ietf.org/html/rfc6901
"""
# pylint: enable=line-too-long

from os.path import (
    isfile,
    abspath,
)
from urllib.parse import urlunsplit
from importlib.resources import (
    files,
    as_file,
)

from ..enforce.value import ValueType
from ..enforce.encoding import (
    Encoder,
    Json,
)

from . import share
from .types import (
    TYPE_CORE,
    TYPE_ABSOLUTE_URI,
)
from .identifiers import (
    key_path_to_json_pointer,
    Identifiers,
)
from .validators import (
    TYPE_SCHEMA,
    Null, Boolean, Integer, Number, String, Array, Object,
    Enum, Const,
    Conditional,
    AllOf, AnyOf, OneOf, Not,
)
from .formats import (
    LocationIndependentId,
    DateTime, Date, Time,
    Email, IdnEmail,
    Hostname,
    IPv4, IPv6,
    Uri, UriReference,
    JsonPointer, RelativeJsonPointer,
    Regex,
)
from .encodings import (
    Base64,
)

JSON = Json()

# https://tools.ietf.org/html/draft-handrews-json-schema-01#section-4.2.1
# "An instance has one of six primitive types..."
#
# https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-6.1.1
# "...MUST be one of the six primitive types... or 'integer'"

TYPE_VALIDATION = dict((_.primitive, _) for _ in (
    Null,
    Boolean,
    Integer,
    Number,
    String,
    Array,
    Object,
))

VALIDATION = dict((_.keyword, _) for _ in (
    Enum,
    Const,
    Conditional,
    AllOf,
    AnyOf,
    OneOf,
    Not,
))

FORMATS = dict((_.name, _) for _ in (
    LocationIndependentId(),
    DateTime(), Date(), Time(),
    Email(), IdnEmail(),
    Hostname(),
    IPv4(), IPv6(),
    Uri(), UriReference(),
    JsonPointer(), RelativeJsonPointer(),
    Regex(),
))

ENCODINGS = dict((_.name, _) for _ in (
    Base64(),
))

class TypeType(ValueType):
    """A |ValueType| enforcing the `type`_ keyword value.

    The set of canonical values is all sets of supported `type`_ values. The set
    of lexical values includes a single `type`_ specified as a string and the
    set of iterables of `type`_ values.
    """
    def __init__(self):
        super().__init__()
        self._supported_types = frozenset(TYPE_VALIDATION)
    def __call__(self, val):
        if not val or val - self._supported_types:
            raise ValueError(val)
        return val
    def cast(self, val):
        if isinstance(val, str):
            val = (val,)
        return self(frozenset(val))
    def schema_types(self, schema):
        """Return a frozenset of the types that `schema` explicitly validates"""
        # https://tools.ietf.org/html/draft-handrews-json-schema-validation-01
        # #section-6.1.1
        try:
            type_ = schema.spec['type']
        except KeyError:
            return frozenset()
        try:
            return self.cast(type_)
        except (TypeError, ValueError) as err:
            raise SchemaError(schema) from err

TYPE_TYPE = TypeType()

### Value validation debugging

class Results():
    """The results accumulated while debugging schema validation of a value.

    Each boolean result is recorded by calling :meth:`assertion` and the result
    is recorded against the current value pointer. The value pointer is changed
    by calling :meth:`key_path_push` and :meth:`key_path_pop` as the value being
    validated is traversed.

    To create an instance, call the |RootSchema| returned by :meth:`build_cls`
    with the initial mapping for the results.
    """
    system_file = '/usr/share/json-schema/rsk-mt/results.json'
    base_uri = 'https://json-schema.roughsketch.co.uk/rsk-mt/results.json'
    def __init__(self):
        self._key_path = []
        self._pointer = None
    def key_path_push(self, key):
        """Push `key` to the key path."""
        self._key_path.append(key)
        self._pointer = None
    def key_path_pop(self):
        """Pop (and discard) the last element on the key path."""
        self._key_path.pop()
        self._pointer = None
    @property
    def pointer(self):
        """Return the JSON Pointer value of the current key path."""
        if self._pointer is None:
            self._pointer = key_path_to_json_pointer(self._key_path)
        return self._pointer
    def assertion(self, schema, keyword, result):
        """Record an assertion result.

        Record that the assertion at `keyword` in `schema` produced boolean
        `result` when validating the value currently pointed to.
        """
        # pylint: disable=unsubscriptable-object,unsupported-assignment-operation
        try:
            self[self.pointer]
        except KeyError:
            self[self.pointer] = {}
        try:
            self[self.pointer][schema.uri][keyword] = bool(result)
        except KeyError:
            self[self.pointer][schema.uri] = {keyword: bool(result)}
    @classmethod
    def build_cls(cls, filename=None):
        """Return a |RootSchema| instance for building results.

        The |RootSchema| instance enforces the JSON Schema at `filename`. If
        `filename` is None then prefer to use a system JSON Schema file in
        :attr:`system_file`. If a `filename` is not supplied and there is no
        file at :attr:`system_file` then use the JSON Schema resource shipped
        in this package.
        """
        support = Support(bases={f'{cls.base_uri}#value-results': (cls,)})
        if filename is not None:
            return RootSchema.load(filename, support=support)
        if isfile(cls.system_file):
            return RootSchema.load(cls.system_file, support=support)
        with as_file(files(share).joinpath('results.json')) as shipped:
            return RootSchema.load(shipped, support=support)
    @classmethod
    def build(cls, filename=None):
        """Return an empty instance of `cls`.

        The instance is created using a |RootSchema| built by :meth:`build_cls`,
        when supplied with `filename`.
        """
        return cls.build_cls(filename)({})

### JSON Schema and Subschema as a value type

class SchemaError(Exception):
    """An exception indicating a specification error in `schema`."""
    def __init__(self, schema, *args):
        super().__init__(*args)
        self.schema = schema

class Schema(ValueType, Encoder):
    """A `JSON Schema`_ as a |ValueType| and |Encoder|.

    An instance of this class may represent either a `Schema or Subschema`_.
    Instances of this class are normally created automatically as a result of
    creating a |RootSchema| instance.

    The arguments to the constructor for this class:

    `root`, a |RootSchema| instance, the `root Schema`_ containing this Schema;
    `spec`, a dict or bool, the `JSON Schema`_ validation rules for this Schema;
    `identifiers`, an |Identifiers| instance, the identifiers for this Schema.

    The set of canonical values is defined by :attr:`implementation`, which
    enforces the Schema's validation rules. Normally the implementation is built
    as |Validator| instances from the Schema's validation rules. These instances
    return values that directly mirror the input value; the returned values
    may be of native Python type, for example :class:`dict`, or may be instances
    of a specialising type, for example a class derived from :class:`dict` which
    enforces the Schema on the dict value. Alternatively, the implementation may
    be overridden by |ApplicationSupport|.

    The set of lexical values of a Schema is all Python values which are valid
    according to the :attr:`implementation`.

    When |ApplicationSupport| overrides the implementation, commonly to optimise
    value validation, then it is the responsibility of that implementation to
    ensure that either the canonical values according to the Schema validation
    rules are respected, or to otherwise define the validation behaviour of the
    application. For (hypothetical) example, if an application supports an
    'allOf' Schema which has two Subschemas and an optimised implementation of
    the first of those two Subschemas returns a substitute value which is not
    equal or equivalent to the value being validated, then the application is
    responsible for defining the consequences for validation using the second of
    the Subschemas, which is dependent upon the output of the first.

    In all cases, this instance's value type must be "completed", by assigning
    to :attr:`implementation`, before validation can be enforced.

    The JSON encoder/decoder from `root` is used as |ValueType| encoder/decoder
    for this Schema instance.

    An application may |ValueType.decode| a JSON-encoded string to a canonical
    Python value, or may validate a Python value directly by calling the Schema.
    """
    def __init__(self, root, spec, identifiers):
        super().__init__()
        self._root = root
        # https://tools.ietf.org/html/draft-handrews-json-schema-01#section-4.3.1
        # "A JSON Schema MUST be an object or a boolean."
        self._spec = TYPE_SCHEMA(spec)
        # https://tools.ietf.org/html/draft-handrews-json-schema-01#section-7
        # "The '$schema' keyword SHOULD be used in a root schema.
        # It MUST NOT appear in subschemas."
        try:
            version = self._spec['$schema']
        except (TypeError, KeyError):
            pass
        else:
            if self is not root:
                raise ValueError('$schema only allowed in root schema')
            if version != 'http://json-schema.org/draft-07/schema#':
                raise ValueError(version)
        self._identifiers = identifiers.define(self)
        self._implementation = None

    ### JSON Schema definition

    @property
    def root(self):
        """Return the root Schema in which this Schema is defined."""
        return self._root
    @property
    def is_root(self):
        """Return True if this Schema is a root Schema, else False."""
        return self is self._root
    @property
    def spec(self):
        """Return the Schema specification as a Python value."""
        return self._spec

    ### JSON Schema identifiers

    @property
    def id_(self):
        """Return the string `$id`_ of this Schema, or None."""
        try:
            id_ = self.spec['$id']
        except (TypeError, KeyError):
            return None
        else:
            return TYPE_CORE['string'](id_)
    @property
    def key_path(self):
        """Return the tuple of keys to address this Schema.

        The address is relative to this Schema's root Schema.
        """
        return self._identifiers.key_path
    @property
    def pointer(self):
        """Return the `JSON Pointer`_ of this Schema."""
        return self._identifiers.pointer
    @property
    def ref(self):
        """Return the URI-encoded `JSON Pointer`_ of this Schema."""
        return '#' + self.pointer
    @property
    def base_uri(self):
        """Return the base URI of this Schema.

        The base URI is an absolute URI against which URI references within this
        Schema are resolved.
        """
        return self._identifiers.base_uri
    @property
    def uri(self):
        """Return the URI of this Schema, or None."""
        return self._identifiers.uri
    @uri.setter
    def uri(self, uri):
        """Set the URI of this Schema."""
        self._identifiers.uri = uri

    def absolute_ref(self, *args):
        """Return the URI-encoded `JSON Pointer`_ of a Subschema of this Schema.

        The URI-encoded `JSON Pointer`_ addresses a Subschema at child path
        `args` under this Schema. (Note that a successful return does not mean
        that the Subschema exists under this Schema, only that the Pointer value
        was successfully formed.)
        """
        return '#' + key_path_to_json_pointer(self._identifiers.key_path + args)

    def relative_ref(self, schema):
        """Return the URI-encoded `JSON Pointer`_ of child `schema`.

        Raise :class:`ValueError` if `schema` is not located under this Schema.
        """
        if self.key_path != schema.key_path[:len(self.key_path)]:
            raise ValueError(schema)
        relative_path = schema.key_path[len(self.key_path):]
        return '#' + key_path_to_json_pointer(relative_path)

    ### JSON Schema metadata

    @property
    def title(self):
        """Return the string `title`_ of this Schema, or None."""
        try:
            title = self._spec['title']
        except (TypeError, KeyError):
            return None
        else:
            return TYPE_CORE['string'](title)
    @property
    def description(self):
        """Return the string `description`_ of this Schema, or None."""
        try:
            description = self._spec['description']
        except (TypeError, KeyError):
            return None
        else:
            return TYPE_CORE['string'](description)
    @property
    def default(self):
        """Return the `default`_ value of this Schema.

        Raise |KeyError| if there is no default value.
        """
        try:
            return self._spec['default']
        except TypeError:
            raise KeyError from None

    ### JSON Schema as a |ValueType|

    @property
    def implementation(self):
        """Return the |ValueType| implementation of this Schema."""
        return self._implementation
    @implementation.setter
    def implementation(self, implementation):
        """Set the |ValueType| implementation of this Schema."""
        self._implementation = implementation

    def __call__(self, val):
        return self._implementation(val)
    def cast(self, val):
        return self._implementation.cast(val)
    def validate(self, val):
        """Return True if `val` is valid against this Schema, else False."""
        try:
            self._implementation(val)
        except (TypeError, ValueError):
            return False
        else:
            return True
    def debug(self, val, results):
        """Return True if `val` is valid against this Schema, else False.

        Also record the outcome of each Schema and keyword function assertion in
        `results`.
        """
        return self._implementation.debug(val, results)

    ### JSON Schema as an |Encoder|

    @property
    def binary(self):
        """Return the binary attribute of the root instance's JSON encoder."""
        return self._root.json_impl.binary
    def encode(self, val):
        """Return the encoded canonical value for lexical value `val`."""
        canonical = self.cast(val)
        return self._root.json_impl.encode(canonical)
    def decode(self, val):
        """Return the canonical value for encoded lexical value `val`."""
        lexical = self._root.json_impl.decode(val)
        return self.cast(lexical)

class _ImplTrue(ValueType):
    """Implementation of JSON Schema specified as JSON value true."""
    def __call__(self, val):
        return val
    @staticmethod
    def debug(val, results): # pylint: disable=unused-argument
        """Return True: all values are valid against this Schema."""
        return True

_TRUE = _ImplTrue()

class _ImplFalse(ValueType):
    """Implementation of JSON Schema specified as JSON value false."""
    def __call__(self, val):
        raise ValueError(val)
    @staticmethod
    def debug(val, results): # pylint: disable=unused-argument
        """Return False: all values are invalid against this Schema."""
        return False

_FALSE = _ImplFalse()

class _ImplExplicit(ValueType):
    """Implementation of JSON Schema `schema` with explicit type validation."""
    def __init__(self, schema, type_validators, other_validators):
        super().__init__()
        self._schema = schema
        self._type_validators = type_validators
        self._other_validators = other_validators
    def __call__(self, val):
        type_checked = False
        for validator in self._type_validators:
            if validator.check(val):
                type_checked = True
                val = validator(val)
                break
        if not type_checked:
            raise TypeError(val)
        for validator in self._other_validators:
            val = validator(val)
        return val
    def cast(self, val):
        type_checked = False
        for validator in self._type_validators:
            if validator.check(val):
                type_checked = True
                val = validator.cast(val)
                break
        if not type_checked:
            raise TypeError(val)
        for validator in self._other_validators:
            val = validator.cast(val)
        return val
    def debug(self, val, results):
        """Return True if `val` is valid against this Schema, else False.

        Also record the outcome of each Schema and keyword function assertion in
        `results`.
        """
        valid = True
        type_checked = False
        for validator in self._type_validators:
            if validator.check(val):
                type_checked = True
                valid = validator.debug(val, results) and valid
                break
        valid = type_checked and valid
        results.assertion(self._schema, 'type', type_checked)
        for validator in self._other_validators:
            valid = validator.debug(val, results) and valid
        return valid

class _ImplImplicit(ValueType):
    """Implementation of JSON Schema `schema` with implicit type validation."""
    def __init__(self, schema, type_validators, other_validators):
        super().__init__()
        self._schema = schema
        self._type_validators = type_validators
        self._other_validators = other_validators
    def __call__(self, val):
        for validator in self._type_validators:
            if validator.check(val):
                val = validator(val)
                break
        for validator in self._other_validators:
            val = validator(val)
        return val
    def cast(self, val):
        for validator in self._type_validators:
            if validator.check(val):
                val = validator(val)
                break
        for validator in self._other_validators:
            val = validator.cast(val)
        return val
    def debug(self, val, results):
        """Return True if `val` is valid against this Schema, else False.

        Also record the outcome of each Schema and keyword function assertion in
        `results`.
        """
        valid = True
        for validator in self._type_validators:
            if validator.check(val):
                valid = validator.debug(val, results) and valid
                break
        for validator in self._other_validators:
            valid = validator.debug(val, results) and valid
        return valid

class Support():
    """A class providing for application support.

    Application support may include:

    - application base classes;
    - semantic validation formats;
    - string encodings;
    - schema optimisation;
    - loading schemas from external sources.

    When creating an instance of this class specify:

    - `bases`, a mapping of URI to a tuple of application base classes. When the
    Schema with this URI validates a value, then the value returned should also
    derive from the corresponding `bases` (if the type of the returned value
    can be specialised).

    - `formats`, a mapping of format name to |Format| instance or None. Semantic
    validation in JSON Schema is enforced by the `format`_ keyword. All formats
    defined in `JSON Schema Validation`_ that are supported in this
    implementation are included in the default mapping. Supplying a value of
    None for a format in `formats` disables validation for that name; supplying
    a |Format| instance overrides the default implementation or extends the set
    of supported formats.

    - `encodings`, a mapping of encoding name to |Encoding| instance or None.
    String encoding in JSON Schema is enforced by the `contentEncoding`_
    keyword. All encodings defined in `JSON Schema Validation`_ that are
    supported in this implementation are included in the default mapping.
    Supplying a value of None for an encoding in `encodings` disables validation
    for that name; supplying an |Encoding| instance overrides the default
    implementation or extends the set of supported encodings.

    - `optimiser`, an |Optimiser| instance which may provide an optimised
    |Validator| instance for a JSON Schema.
    """
    def __init__(self, bases=(), formats=(), encodings=(), optimiser=None):
        self._bases = dict(bases)
        self._formats = dict(FORMATS)
        self._formats.update(formats)
        self._encodings = dict(ENCODINGS)
        self._encodings.update(encodings)
        self._optimiser = optimiser
    @property
    def bases(self):
        """Get this instance's bases."""
        return self._bases
    @property
    def formats(self):
        """Get this instance's formats."""
        return self._formats
    @property
    def encodings(self):
        """Get this instance's encodings."""
        return self._encodings
    def get_bases(self, uri, root): # pylint: disable=unused-argument
        """Return base classes for validated value type specialisation.

        Return a tuple of base classes to build into a specialised type for
        values validated by the Schema at `uri` under `root`. If there are no
        such classes then return an empty tuple.
        """
        try:
            return self.bases[uri]
        except KeyError:
            return ()
    def get_format(self, name):
        """Return a |Format| instance for format `name`, or None."""
        try:
            return self.formats[name]
        except KeyError:
            return None
    def get_encoding(self, name):
        """Return an |Encoding| instance for encoding `name`, or None."""
        try:
            return self.encodings[name]
        except KeyError:
            return None
    def set_optimiser(self, optimiser):
        """Set `optimiser`, an |Optimiser| instance, for schema optimisation."""
        self._optimiser = optimiser
    def get_optimised(self, uri, root):
        """Return a |Validator| instance, the validation implementation.

        Return the validation implementation of the Schema at `uri` under
        `root`, or None to use validators built from the Schema definition.
        """
        return self._optimiser.optimised(uri, root) if self._optimiser else None
    def load_schema(self, uri): # pylint: disable=no-self-use
        """Return a |Schema| instance for the Schema at `uri`.

        Raise :class:`ValueError` if there is no Schema available for that URI.
        """
        raise ValueError(uri)

class Optimiser(): # pylint: disable=too-few-public-methods
    """A base class for an optimiser of JSON Schema implementations."""
    def optimised(self, uri, root): # pylint: disable=unused-argument,no-self-use
        """Return a |Validator| instance, the validation implementation.

        Return the validation implementation of the Schema at `uri` under
        `root`, or None to use validators built from the Schema definition.
        """
        return None

class Optimised(ValueType): # pylint: disable=too-few-public-methods
    """A minimal |Validator| substitute.

    The default behaviour is to raise :class:`ValueError` on a validation call.
    A derived class can override :meth:`get_schema` to select a schema
    implementation to validate a value.
    """
    def get_schema(self, val): # pylint: disable=no-self-use
        """Return a schema implementation for validating `val`.

        Raise :class:`ValueError` if there is no suitable schema (and therefore
        `val` cannot be validated; is invalid).
        """
        raise ValueError(val)
    def __call__(self, val):
        """Pass on this method call to the schema implementation."""
        return self.get_schema(val)(val)
    def debug(self, val, result):
        """Pass on this method call to the schema implementation."""
        return self.get_schema(val).debug(val, result)

def key_path_at_schema(key_path):
    """Return True if `key_path` addresses a schema, else False.

    Return False if `key_path` addresses a plain object.
    """
    if key_path == ('definitions',):
        return False
    count = 0
    for token in reversed(key_path):
        if token in ('properties', 'patternProperties', 'dependencies'):
            count += 1
        else:
            break
    if count % 2:
        return False
    return True

class RootSchema(Schema):
    """A `root Schema`_ as a |ValueType|.

    When creating an instance of this class specify:

    - `spec`, a dict or bool instance specifying a `JSON Schema`_; the top-level
    Schema in `spec` is the Schema for this instance and it is declared as the
    root Schema; recursively contained Subschemas are automatically created,
    declared and defined in the root Schema;
    - `initial_base_uri`, an absolute URI string, the `initial base URI`_ for
    this Schema and its Subschemas;
    - `json_impl`, the JSON encoder/decoder to use with this Schema and its
    Subschemas;
    - `support`, a :class:`Support` instance defining application support;
    - `define`, a boolean indicating whether to define the implementation or not
    (not defining an implementation is useful to declare all URIs without
    loading external Schemas).

    It is the application's responsibility to provide a JSON implementation that
    provides the correct support for its needs, including the ability to cope
    with encoding from/decoding to specific types.
    """
    def __init__(
            self, spec, initial_base_uri,
            json_impl=JSON, support=None, define=True,
        ): # pylint: disable=too-many-arguments
        self._support = support if support else Support()
        self._json_impl = json_impl
        initial_base_uri = TYPE_ABSOLUTE_URI(initial_base_uri)
        Schema.__init__(self, self, spec, Identifiers(initial_base_uri))
        # mapping of URI or URI-encoded JSON Pointer to Schema instance
        self._schema = {}
        # a stack of Schemas which change the absolute base URI
        self._stack = [self]
        # declare all Schema instances
        self.declare(self)
        # define all declared Schema instances
        if define:
            self.define()
    @property
    def support(self):
        """Return the application support."""
        return self._support
    @property
    def json_impl(self):
        """Return the JSON encoder/decoder implementation."""
        return self._json_impl
    def get_bases(self, uri):
        """Return base classes for validated value type specialisation.

        Return a tuple of base classes to build into a specialised type for
        values validated by the Schema at `uri` under this root Schema. If there
        are no such classes then return an empty tuple.
        """
        return self.support.get_bases(uri, self)
    def get_format(self, name):
        """Return a |Format| instance for format `name`, or None."""
        return self.support.get_format(name)
    def get_encoding(self, name):
        """Return an |Encoding| instance for encoding `name`, or None."""
        return self.support.get_encoding(name)
    def get_optimised(self, uri):
        """Return a |Validator| instance, the validation implementation.

        Return the validation implementation of the Schema at `uri`, or None to
        use validators built from the Schema definition.
        """
        return self.support.get_optimised(uri, self)
    def get_schema(self, key, load=True):
        """Return the Schema at `key`.

        `key` may be either a URI-encoded `JSON Pointer`_ or URI. When `key` is
        a URI-encoded JSON Pointer, then the Schema must be available in this
        root Schema. Raise :class:`KeyError` if there is no Schema available.

        When `key` is a URI, then the Schema may be available in this root
        Schema or, if `load` is True, from an external source using application
        support. Raise :class:`ValueError` if there is no Schema available.
        """
        try:
            return self._schema[key]
        except KeyError:
            pass
        try:
            TYPE_ABSOLUTE_URI.cast(key)
        except ValueError:
            raise KeyError(key) from None
        if not load:
            raise ValueError(key)
        return self.support.load_schema(key)
    @property
    def uris(self):
        """An iterable of the URIs against which Schemas are registered."""
        for key in self._schema:
            if not key.startswith('#'):
                yield key
    @classmethod
    def loads(cls, string, initial_base_uri=None, json_impl=JSON, **kwargs):
        """Return a |RootSchema| instance from JSON-encoded `string`.

        The |RootSchema| instance is built from the JSON Schema in JSON-encoded
        `string`. Use `json_impl` as the JSON encoder/decoder for all Schemas in
        this instance.
        """
        spec = json_impl.loads(string)
        return cls(spec, initial_base_uri, json_impl, **kwargs)
    @classmethod
    def load(cls, path, initial_base_uri=None, json_impl=JSON, **kwargs):
        """Return a |RootSchema| instance from the file at `path`.

        The |RootSchema| instance is built from the JSON Schema in the file at
        `path`. Use `json_impl` as the JSON encoder/decoder for all Schemas in
        this instance.
        """
        if initial_base_uri is None:
            initial_base_uri = urlunsplit(('file', '', abspath(path), '', ''))
        with open(path, encoding='utf-8') as fid:
            spec = json_impl.load(fid)
        return cls(spec, initial_base_uri, json_impl, **kwargs)
    def declare(self, schema):
        """Declare `schema` and its Subschemas in this `root Schema`_.

        Each Schema is registered against each URI that identifies it and the
        single URI-encoded `JSON Pointer`_ that identifies its location in this
        `root Schema`_.
        """
        # if `schema` changes the absolute base URI, then push stack
        push = self._stack[-1].base_uri != schema.base_uri
        if push:
            self._stack.append(schema)
        # register `schema` against its intrinsic URI
        # and its URI-encoded JSON Pointer
        if schema.uri in self._schema:
            raise KeyError(schema.uri)
        if schema.ref in self._schema:
            raise KeyError(schema.ref)
        if schema.uri is not None:
            self._schema[schema.uri] = schema
        self._schema[schema.ref] = schema
        # register `schema` against each extrinsic (location-based) URI
        # process in reverse nesting order (*)
        for base in reversed(self._stack):
            # an empty fragment is permitted in base URI, strip it if present
            uri = base.base_uri.rstrip('#') + base.relative_ref(schema)
            if uri in self._schema:
                raise KeyError(uri)
            self._schema[uri] = schema
            # (*) to assign most specific extrinsic URI when Schema has no URI
            if schema.uri is None:
                schema.uri = uri
        # declare Subschemas
        if schema.spec not in (True, False):
            for key in schema.spec:
                self._declare(
                    schema.spec[key],
                    schema.base_uri,
                    schema.key_path + (key,),
                )
        # pop stack, if required
        if push:
            self._stack.pop()
    def _declare(self, val, base_uri, key_path):
        """If `val` is a Schema then declare it in this `root Schema`_.

        Otherwise traverse `val` for any recursively contained Subschemas and
        declare them.
        """
        try:
            TYPE_SCHEMA(val)
        except (TypeError, ValueError):
            if isinstance(val, (list, tuple)):
                idx = 0
                while idx < len(val):
                    self._declare(val[idx], base_uri, key_path + (idx,))
                    idx += 1
        else:
            if val in (True, False):
                # create boolean `val` as a JSON Schema in this root Schema
                self.declare(Schema(self, val, Identifiers(base_uri, key_path)))
            elif key_path_at_schema(key_path):
                try:
                    base_uri = TYPE_ABSOLUTE_URI.graft(base_uri, val['$id'])
                except KeyError:
                    pass
                # create dict `val` as a JSON Schema in this root Schema
                self.declare(Schema(self, val, Identifiers(base_uri, key_path)))
            else:
                # dict `val` is not a JSON Schema itself:
                # its member values may be JSON Schemas
                for key in val:
                    self._declare(val[key], base_uri, key_path + (key,))
    def define(self):
        """Define all Schemas registered in this `root Schema`_."""
        for schema in frozenset(self._schema.values()):
            self._define(schema)
    def _define(self, schema):
        """Define the implementation for `schema`.

        If the application provides an optimised implementation of the Schema,
        then use that implementation. Otherwise, the Schema specification
        defines how to build validators to implement the Schema: if the
        specification includes a `$ref`_ reference, then the implementation is
        the JSON Schema at that reference; otherwise the implementation is
        defined by the validation pairs in the Schema.
        """
        optimised = self.get_optimised(schema.uri)
        if optimised:
            schema.implementation = optimised
        elif schema.spec is True:
            schema.implementation = _TRUE
        elif schema.spec is False:
            schema.implementation = _FALSE
        elif '$ref' in schema.spec:
            # https://tools.ietf.org/html/draft-handrews-json-schema-01#section-8.3
            # "An object schema with a '$ref' property MUST be interpreted as a
            # '$ref' reference. The value of the '$ref' property MUST be a URI
            # Reference. Resolved against the current URI base, it identifies
            # the URI of a schema to use. All other properties in a '$ref'
            # object MUST be ignored."
            ref = schema.spec['$ref']
            try:
                schema.implementation = self.get_schema(ref)
            except KeyError:
                # failed to get Schema by non-absolute URI reference
                # try resolving
                uri = TYPE_ABSOLUTE_URI.resolve(schema.base_uri, ref)
                schema.implementation = self.get_schema(uri)
        else:
            # https://tools.ietf.org/html/draft-handrews-json-schema-validation-01#section-3.2.1
            # "Most validation keywords only constrain values within a certain
            # primitive type. When the type of the instance is not of the type
            # targeted by the keyword, the instance is considered to conform to
            # the assertion."
            types = TYPE_TYPE.schema_types(schema)
            # include validation rules for all explicitly valid types, or
            # all non-empty validation rules for implicitly valid types
            if types:
                include = lambda k, v: k in types
            else:
                include = lambda k, v: bool(v)
            type_validators = self.build_validators(
                schema, TYPE_VALIDATION, include,
            )
            # include all non-empty validation rules for
            # non-type specific validators
            other_validators = self.build_validators(
                schema, VALIDATION, lambda k, v: bool(v),
            )
            impl_cls = _ImplExplicit if types else _ImplImplicit
            schema.implementation = impl_cls(
                schema, type_validators, other_validators,
            )
    def build_validators(self, schema, rules, include):
        """Return validators for enforcing the validation `rules` for `schema`.

        Return a list of validators, each a |ValueType| instance, for enforcing
        validation `rules` for `schema`. `rules` must be a mapping of rule key
        to a validation rule function. If the specification of `schema` does not
        conform to any rule in `rules` then raise :class:`SchemaError`. Only
        build and include a validator for a rule if function `include` returns
        True when called with the rule key and a validation rule.
        """
        validators = []
        for key in rules:
            try:
                validation = rules[key](schema.spec)
            except (TypeError, ValueError) as err:
                raise SchemaError(schema) from err
            if include(key, validation):
                validator = validation.validator(self, schema)
                if validator:
                    validators.append(validator)
        return validators
