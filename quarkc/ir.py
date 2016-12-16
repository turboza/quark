# Problem areas from the current backend:
#  - scoping of names (if nested in while nested in function, sometimes introduces scopes, sometimes not)
#  - mapping of names into target language (dumb languages that use captialization to mean things)
#  - importing between namespaces and/or packages
#  - sourcemaps
#  - testing backend in isolation

# Potential ordering that this could proceed.
#
#  1. Flesh out this sketch to skeletaly solve the problem areas
#     described above, e.g. make it just capable of correctly
#     compiling an if nested in a while nested in a function that is
#     imported into another namespace and another package and fully
#     capture the mapping of line numbers between input source and
#     output code while doing so.
#
#  2. Hook up skeletal version into each target language (including
#     go) and make sure the methodology for testing this is
#     satisfactory.
#
#  3. Fill in the extra bits needed to make the skeletal version
#     turing complete.
#
#  4. Wire this into a frontend. This might be the existing frontend,
#     or it might be a scope reduced frontend if the other work
#     streams have eliminated dependencies on frontend features like
#     inheritence. Hypothetically it could even be an alternative
#     frontend.
from functools import total_ordering
from itertools import groupby

from .match import match, lazy, ntuple, many, opt, choice
from . import tree

class IR(tree._Tree):

    @staticmethod
    def load_path(path):
        with open(path) as f:
            return IR.load(f.read(), source=path)

    @staticmethod
    def load(ir_str, source='<string>'):
        g = globals()
        ir_c = compile("(" + ir_str + ",)\n", source, 'eval')
        ir_e = eval(ir_c, {}, dict((k,g[k]) for k in __all__))
        ir = ir_e[0]
        assert isinstance(ir, IR), "%s: does not contain IR" % source
        return ir

    def copy(self):
        return IR.load(repr(self))

def namesplit(name):
    if ':' in name:
        package, path = name.split(':')
        path = tuple(path.split('.'))
        return package, path
    else:
        return name, ()

# A fully qualified name.

@total_ordering
class _Name(IR):

    @match(basestring, many(basestring))
    def __init__(self, package, *path):
        pkg, pfx = namesplit(package)
        self.package = pkg
        self.path = pfx
        for n in path:
            self.path += tuple(n.split('.'))
        self._validate()

    def _validate(self):
        assert self.package, "Package must be non-empty"
        assert len(self.path) > 1, "Expected at least one namespace-thing %s %s" % (self.package, self.path)

    @property
    def children(self):
        if False: yield

    @match(lazy("_Name"))
    def __eq__(self, other):
        """ Name and Ref compare equal """
        return self.package == other.package and self.path == other.path

    @match(lazy("_Name"))
    def __ne__(self, other):
        return not self.__eq__(other)

    @match(lazy("_Name"))
    def __lt__(self, other):
        return (self.package, self.path) < (other.package, other.path)

    @match(lazy("_Name"))
    def __gt__(self, other):
        return (self.package, self.path) > (other.package, other.path)

    def __hash__(self):
        return hash((self.package, self.path))

    def __repr__(self):
        return self.repr(self.package, *self.path)

    def __str__(self):
        return ":".join((self.package, ) + (self.path and (".".join(self.path),)))

    @property
    def namespace(self):
        return NamespaceName(self.package, *self.path[:-1])

    @classmethod
    @match(type, lazy("_Name"), many(basestring))
    def join(cls, name, *elem):
        return cls(name.package, *(name.path + elem))

# The name of a Namespace.

class NamespaceName(_Name):
    def _validate(self):
        assert self.package, "Package must be non-empty"
        assert len(self.path), "Expected at least one namespace-thing %s %s" % (self.package, self.path)

    @property
    def namespace(self):
        if len(self.path) == 1:
            return PackageName(self.package, ())

# The name of a Package
class PackageName(_Name):
    def _validate(self):
        assert self.package, "Package must be non-empty"
        assert len(self.path) == 0, "Expected no namespace-things %s %s" % (self.package, self.path)

    @property
    def namespace(self):
        return self

    def __repr__(self):
        return self.repr(self.package)

# The name of a Definition.
class Name(_Name):
    pass


@total_ordering
class _ScopedName(IR):
    @match(basestring)
    def __init__(self, name):
        self.name = name

    @property
    def children(self):
        if False: yield

    def __repr__(self):
        return self.repr(self.name)

    @match(lazy("_ScopedName"))
    def __eq__(self, other):
        return self.name == other.name

    @match(lazy("_ScopedName"))
    def __ne__(self, other):
        return not self.__eq__(other)

    @match(lazy("_ScopedName"))
    def __lt__(self, other):
        return self.name < other.name

    @match(lazy("_ScopedName"))
    def __gt__(self, other):
        return self.name > other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name


class ScopedName(_ScopedName):
    pass

class LocalName(_ScopedName):
    pass

# A reference to a Definition
# The target must know how to import a Ref both across
# packages and from other namespaces within the same package. Does
# this need to know what type it is importing, e.g. might
# functions/interfaces/classes be imported differently?
# A: yes, ruby has different rules for FFI naming of functions and Interfaces
# The type can be inferred from usage context though

class Ref(_Name):
    pass

# Either a quark Type or a NativeType
class AbstractType(IR):
    pass

# A Quark defined type
# XXX: Should maybe switch to Ref/Def versions of names or something.
# XXX: These are allowed to be instantiated just so that shorthand Declaration continues to work.
class Type(AbstractType):
    @match(Ref)
    def __init__(self, name):
        self.name = name

    @match(basestring)
    def __init__(self, name):
        self.__init__(Ref(name))

    @property
    def children(self):
        yield self.name

    def __eq__(self, other):
        return type(self) is type(other) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.repr(self.name)

# A quark defined class type
class ClassType(Type):
    pass

# A quark defined interface type
class InterfaceType(Type):
    pass

# A no-type type
class Void(AbstractType):
    def __init__(self):
        pass

    @property
    def children(self):
        if False: yield

    def __repr__(self):
        return self.repr()

# a type that maps to a native type in target language, probably the quark primitive
class NativeType(AbstractType):

    def __init__(self):
        pass

    @property
    def children(self):
        if False: yield

    def __repr__(self):
        return self.repr()

class Int(NativeType):
    pass

class Float(NativeType):
    pass

class String(NativeType):
    pass

class Bool(NativeType):
    pass

# a native type that can represent any object in the target
class Any(NativeType):
    pass

# a native type that can represent any scalar in the target (Int, Float, String, Bool)
class Scalar(NativeType):
    pass

# a native type for a function accepting an InterfaceType and returning an InterfaceType
class Callable(NativeType):
    pass

# a representation of a native type in a boxed context, like Integer for java int
class Boxed(NativeType):
    @match(NativeType)
    def __init__(self, type):
        self.type = type

    @property
    def children(self):
        yield self.type

    def __repr__(self):
        return self.repr(self.type)

class Map(NativeType):
    @match(choice(Bool,String,Int,Float,Scalar), NativeType)
    def __init__(self, key, value):
        self.key = key
        self.value = value

    @property
    def children(self):
        yield self.key
        yield self.value

    def __repr__(self):
        return self.repr(self.key, self.value)

class List(NativeType):
    @match(AbstractType)
    def __init__(self, value):
        self.value = value

    @property
    def children(self):
        yield self.value

    def __repr__(self):
        return self.repr(self.value)

class Primitive(NativeType):
    @match(many(lazy("NativeBlock"), min=1))
    def __init__(self, *blocks):
        self.blocks = blocks

    @property
    def children(self):
        for b in self.blocks:
            yield b

    def __repr__(self):
        return self.repr(*self.blocks)

class Declaration(IR):

    @match(basestring, Ref)
    def __init__(self, name, type):
        self.__init__(name, Type(type))

    @match(basestring, basestring)
    def __init__(self, name, type):
        self.__init__(name, Ref(type))

    @property
    def children(self):
        yield self.name
        yield self.type

    def collisions(self, names):
        if self.name in names:
            yield self.name
        else:
            names.add(self.name)

    def __repr__(self):
        return self.repr(self.name, self.type)

class LocalDeclaration(Declaration):

    @match(LocalName, AbstractType)
    def __init__(self, name, type):
        self.name = name
        self.type = type

    @match(basestring, AbstractType)
    def __init__(self, name, type):
        self.__init__(LocalName(name), type)


class PublicDeclaration(Declaration):

    @match(ScopedName, AbstractType)
    def __init__(self, name, type):
        self.name = name
        self.type = type

    @match(basestring, AbstractType)
    def __init__(self, name, type):
        self.__init__(ScopedName(name), type)

# A class, interface, or function.
class Definition(IR):
    pass

class External(Definition):
    @match(Name)
    def __init__(self, name):
        self.name = name

    @property
    def children(self):
        yield self.name

    def __repr__(self):
        return self.repr(self.name)

class ExternalFunction(External):
    pass

class ExternalInterface(External):
    pass

class Namespace(IR):
    @match(NamespaceName, many(choice(Definition,lazy("Namespace"))))
    def __init__(self, name, *definitions):
        self.name = name
        self.definitions = definitions

    @property
    def children(self):
        yield self.name
        for d in self.definitions:
            yield d

    def __repr__(self):
        return self.repr(self.name, *self.definitions)

# Contains definitions. Renders to a buildable distribution unit.
class Package(IR):

    # XXX: this is transitional. Goal is for package to contain only namespaces
    @match()
    def __init__(self):
        self.__init__(PackageName("noname"))

    @match(many(Definition, min=1))
    def __init__(self, *definitions):
        self.name = PackageName(definitions[0].name.package)
        self.definitions = definitions

    @match(PackageName, many(Namespace))
    def __init__(self, name, *definitions):
        self.name = name
        self.definitions = definitions

    @property
    def children(self):
        yield self.name
        for d in self.definitions:
            yield d

    def __repr__(self):
        if self.definitions and isinstance(self.definitions[0], Namespace):
            return self.repr(self.name, *self.definitions)
        else:
            return self.repr(*self.definitions)

class ExternalPackage(Package):
    pass

class Root(IR):
    @match(many(Package))
    def __init__(self, *packages):
        self.packages = packages

    @property
    def children(self):
        for p in self.packages:
            yield p

    def __repr__(self):
        return self.repr(*self.packages)

# keeps same-named definitions together

# knows how to render inside a dfn, this has to account for imports
# needed by rendered code
class Code(IR):
    pass

class Statement(Code):
    pass

class Expression(Code):
    pass

class Block(Code):

    @match(many(Statement))
    def __init__(self, *statements):
        self.statements = statements

    @match(ntuple(Statement))
    def __init__(self, statements):
        self.__init__(*statements)

    @match(Expression)
    def __init__(self, expr):
        self.__init__(Evaluate(expr))

    @property
    def children(self):
        for s in self.statements:
            yield s

    def collisions(self, names):
        for s in self.statements:
            for c in s.collisions(names):
                yield c

    def __repr__(self):
        return self.repr(*[s for s in self.statements if not isinstance(s, FieldInitialize)])

class Param(LocalDeclaration):
    @match(LocalName, Void)
    def __init__(self, name, type):
        """XXX: until frontend decides what is the story on assignability to
        Any and so we use void parameters as an interim hack

        """
        self.name = name
        self.type = Any()

class Template(Definition):
    """ A templated definition. The definition is supposed to use TypeParam in places where
    """
    @match(choice(lazy("Interface"),lazy("Class"),lazy("Function"),lazy("Instantiation")))
    def __init__(self, dfn):
        self.dfn = dfn

    @property
    def children(self):
        yield self.dfn

    def __repr__(self):
        return self.repr(self.dfn)

class TypeParam(AbstractType):
    @match(basestring)
    def __init__(self, name):
        self.name = name

    @property
    def children(self):
        if False: yield

    def __repr__(self):
        return self.repr(self.name)

class TypeBinding(IR):
    @match(basestring, AbstractType)
    def __init__(self, name, type):
        self.name = name
        self.type = type

    @property
    def children(self):
        yield self.type

    def __repr__(self):
        return self.repr(self.name, self.type)

class Instantiation(Definition):

    @match(Name, Ref, many(TypeBinding, min=1))
    def __init__(self, name, template, *bindings):
        self.name = name
        self.template = template
        self.bindings = bindings

    @property
    def children(self):
        yield self.name
        yield self.template
        for b in self.bindings:
            yield b

    def __repr__(self):
        return self.repr(self.name, self.template, *self.bindings)

class Function(Definition):

    @match(Name, AbstractType, many(Param), choice(Block, lazy("NativeBlock")))
    def __init__(self, name, type, *args):
        self.name = name
        self.type = type
        self.params = args[:-1]
        self.body = args[-1]

    @match(Name, Ref, many(Param), Statement)
    def __init__(self, name, type, *args):
        self.__init__(name, Type(type), *(args[:-1] + (Block(args[-1]),)))

    @match(Name, AbstractType, many(Param), Statement)
    def __init__(self, name, type, *args):
        self.__init__(name, type, *(args[:-1] + (Block(args[-1]),)))

    @property
    def children(self):
        yield self.name
        yield self.type
        for p in self.params:
            yield p
        yield self.body

    def __repr__(self):
        return self.repr(self.name, self.type, *(self.params + (self.body,)))

class Field(PublicDeclaration):

    @match(ScopedName, AbstractType, opt(lazy('Null')))
    def __init__(self, name, type, initializer=None):
        self.type = type
        self.name = name
        self.initializer = initializer or Null(type.copy())

    @match(basestring, AbstractType, lazy('Null'))
    def __init__(self, name, type, initializer):
        self.__init__(ScopedName(name), type, initializer)

    @match(basestring, AbstractType)
    def __init__(self, name, type):
        self.__init__(ScopedName(name), type)

    # XXX: poor-man private constructor :)
    @match("private", ScopedName, NativeType, lazy('Literal'))
    def __init__(self, _, name, type, initializer):
        self.type = type
        self.name = name
        self.initializer = initializer

    @match(ScopedName, Bool, opt(lazy('BoolLit')))
    def __init__(self, name, type, initializer=None):
        self.__init__("private", name, type, Null(type))

    @match(ScopedName, Int, opt(lazy('IntLit')))
    def __init__(self, name, type, initializer=None):
        self.__init__("private", name, type, Null(type))

    @match(ScopedName, String, opt(lazy('StringLit')))
    def __init__(self, name, type, initializer=None):
        self.__init__("private", name, type, Null(type))

    @match(ScopedName, Float, opt(lazy('FloatLit')))
    def __init__(self, name, type, initializer=None):
        self.__init__("private", name, type, Null(type))

    @match(basestring, choice(Bool,Int,String,Float), opt(lazy('Literal')))
    def __init__(self, name, type, initializer=None):
        self.__init__("private", ScopedName(name), type, Null(type))

    @property
    def children(self):
        yield self.name
        yield self.type
        yield self.initializer

    def __repr__(self):
        return self.repr(self.name, self.type, self.initializer)



class Message(PublicDeclaration):

    @match(ScopedName, AbstractType, many(Param))
    def __init__(self, name, type, *args):
        self.name = name
        self.type = type
        self.params = args[:]

    @match(basestring, AbstractType, many(Param))
    def __init__(self, name, type, *args):
        self.__init__(ScopedName(name), type, *args)

    @property
    def children(self):
        yield self.name
        yield self.type
        for p in self.params:
            yield p

    def __repr__(self):
        return self.repr(self.name, self.type, *self.params)

class Method(IR):

    @match(ScopedName, AbstractType, many(Param), Block)
    def __init__(self, name, type, *args):
        self.name = name
        self.type = type
        self.params = args[:-1]
        self.body = args[-1]

    @match(basestring, AbstractType, many(Param), Block)
    def __init__(self, name, type, *args):
        self.__init__(ScopedName(name), type, *args)

    @property
    def children(self):
        yield self.name
        yield self.type
        for p in self.params:
            yield p
        yield self.body

    def __repr__(self):
        return self.repr(self.name, self.type, *(self.params + (self.body,)))

class Constructor(Method):
    @match(ScopedName, ClassType, many(Param), Block)
    def __init__(self, name, type, *args):
        self.name = name
        self.type = type
        self.params = args[:-1]
        self.body = args[-1]

    @match(basestring, ClassType, many(Param), Block)
    def __init__(self, name, type, *args):
        self.__init__(ScopedName(name), type, *args)


# Note that there is no concept of inheritence here, just
# implementation of interfaces. This implies that the quark FFI cannot
# accomodate subclassing, i.e. quark types cannot be subclassed from
# outside of quark, the only types quark really exports are
# interfaces, and the only external types quark allows to pass across
# its surface are interfaces.
class Class(Definition):

    @match(Name, many(InterfaceType), many(choice(Method, Field)))
    def __init__(self, name, *args):
        self.name = name
        self.implements = [a for a in args if isinstance(a, Type)]
        self.fields = [a for a in args if isinstance(a, Field)]
        self.constructors = [a for a in args if isinstance(a, Constructor)]
        self.methods = [a for a in args if isinstance(a, Method) and not isinstance(a,Constructor)]
        assert len(self.implements) + len(self.fields) + len(self.constructors) + len(self.methods) == len(args)
        assert len(self.constructors) <= 1

        if self.constructors:
            constructor_body = self.constructors[0].body

            initializers = tuple(FieldInitialize(This(), f.name, f.initializer.copy()) for f in self.fields)
            constructor_body.statements = initializers + constructor_body.statements

    @property
    def children(self):
        yield self.name
        for i in self.implements:
            yield i
        for f in self.fields:
            yield f
        for c in self.constructors:
            yield c
        for m in self.methods:
            yield m

    def __repr__(self):
        return self.repr(*([self.name] + self.implements + self.fields + self.constructors + self.methods))

# basically the same as a class but no fields
class Interface(Definition):

    @match(Name, many(InterfaceType), many(Message))
    def __init__(self, name, *args):
        self.name = name
        self.implements = [a for a in args if isinstance(a, Type)]
        self.methods = [a for a in args if isinstance(a, Message)]
        assert len(self.implements) + len(self.methods) == len(args)

    @property
    def children(self):
        yield self.name
        for i in self.implements:
            yield i
        for m in self.methods:
            yield m

    def __repr__(self):
        return self.repr(*([self.name] + self.implements + self.methods))

# code

# an expression with no children
class SimpleExpression(Expression):

    def __init__(self):
        pass

    @property
    def children(self):
        if False: yield

    def __repr__(self):
        return self.repr()

# evaluation of the implied this
class This(SimpleExpression):
    pass

# null value
class Null(SimpleExpression):
    def __new__(cls, type):
        return makeNull(type)

    def __init__(self, type):
        self.type = type

    @property
    def children(self):
        yield self.type

    def __repr__(self):
        return self.repr(self.type)

@match(Bool)
def makeNull(_):
    return BoolLit(False)

@match(Int)
def makeNull(_):
    return IntLit(0)

@match(String)
def makeNull(_):
    return StringLit("")

@match(Float)
def makeNull(_):
    return FloatLit(0.0)

@match(choice(AbstractType, Any, Callable))
def makeNull(type):
    # instantiate via superclass
    return SimpleExpression.__new__(Null, type)

# access a Local or a Param
class Var(SimpleExpression):

    @match(LocalName)
    def __init__(self, name):
        self.name = name

    @match(basestring)
    def __init__(self, name):
        self.__init__(LocalName(name))

    @property
    def children(self):
        yield self.name

    def __repr__(self):
        return self.repr(self.name)

# short-circuit bool operators
class And(Expression):
    @match(many(Expression, min=2))
    def __init__(self, *exprs):
        self.exprs = exprs

    @property
    def children(self):
        for e in self.exprs:
            yield e

    def __repr__(self):
        return self.repr(*self.exprs)

class Or(Expression):
    @match(many(Expression, min=2))
    def __init__(self, *exprs):
        self.exprs = exprs

    @property
    def children(self):
        for e in self.exprs:
            yield e

    def __repr__(self):
        return self.repr(*self.exprs)

# access a Field or a Method
class Get(Expression):

    @match(Expression, ScopedName)
    def __init__(self, expr, name):
        self.expr = expr
        self.name = name

    @match(Expression, basestring)
    def __init__(self, expr, name):
        self.__init__(expr, ScopedName(name))

    @property
    def children(self):
        yield self.expr
        yield self.name

    def __repr__(self):
        return self.repr(self.expr, self.name)

# mutate a Field
class Set(Statement):

    @match(Expression, ScopedName, Expression)
    def __init__(self, expr, name, value):
        self.expr = expr
        self.name = name
        self.value = value

    @match(Expression, basestring, Expression)
    def __init__(self, expr, name, value):
        self.__init__(expr, ScopedName(name), value)

    @property
    def children(self):
        yield self.expr
        yield self.name
        yield self.value

    def __repr__(self):
        return self.repr(self.expr, self.name, self.value)

# a specialization of Set, for Class Field initialization, so
# that Constructor Block can filter them out
class FieldInitialize(Set):
    pass

# Invokes a function given the fully qualified name and arguments
class Invoke(Expression):

    @match(Ref, many(Expression))
    def __init__(self, name, *args):
        self.name = name
        self.args = args

    @property
    def children(self):
        yield self.name
        for a in self.args:
            yield a

    def __repr__(self):
        return self.repr(self.name, *self.args)

# Invokes a method on an object
class Send(Expression):

    @match(Expression, ScopedName, (many(Expression),))
    def __init__(self, expr, name, args):
        self.expr = expr
        self.name = name
        self.args = args

    @match(Expression, basestring, (many(Expression),))
    def __init__(self, expr, name, args):
        self.__init__(expr, ScopedName(name), args)

    @property
    def children(self):
        yield self.expr
        yield self.name
        for a in self.args:
            yield a

    def __repr__(self):
        return self.repr(self.expr, self.name, self.args)

# Constructs an instance of a class.
class Construct(Expression):

    @match(Ref, (many(Expression),))
    def __init__(self, name, args):
        self.name = name
        self.args = args

    @property
    def children(self):
        yield self.name
        for a in self.args:
            yield a

    def __repr__(self):
        return self.repr(self.name, self.args)

# Invokes a callable expression.
class Call(Expression):

    @match(Expression, (many(Expression),))
    def __init__(self, expr, args):
        self.expr = expr
        self.args = args

    @property
    def children(self):
        yield self.expr
        for a in self.args:
            yield a

    def __repr__(self):
        return self.repr(self.expr, self.args)

class Cast(Expression):

    @match(AbstractType, Expression)
    def __init__(self, type, expr):
        self.type = type
        self.expr = expr

    @property
    def children(self):
        yield self.type
        yield self.expr

    def __repr__(self):
        return self.repr(self.type, self.expr)

# literals

class Literal(SimpleExpression):
    def __repr__(self):
        return self.repr(self.value)

    def __eq__(self, other):
        return type(self) is type(other) and self.value == other.value

    def __hash__(self):
        return hash(self.value)

# int literal
class IntLit(Literal):

    @match(int)
    def __init__(self, value):
        self.type = Int()
        self.value = int(value)

# float literal
class FloatLit(Literal):

    @match(float)
    def __init__(self, value):
        self.type = Float()
        self.value = float(value)

# string literal
class StringLit(Literal):

    @match(basestring)
    def __init__(self, value):
        self.type = String()
        self.value = unicode(value)

# string literal
class BoolLit(Literal):

    @match(bool)
    def __init__(self, value):
        self.type = String()
        self.value = bool(value)

# statements

class Local(LocalDeclaration, Statement):

    @match(LocalName, AbstractType, opt(Expression))
    def __init__(self, name, type, expr=None):
        self.type = type
        self.name = name
        self.expr = expr or Null(type.copy())

    @match(basestring, AbstractType, opt(Expression))
    def __init__(self, name, type, expr=None):
        self.__init__(LocalName(name), type, expr=expr)

    @property
    def children(self):
        yield self.name
        yield self.type
        if self.expr:
            yield self.expr

    def __repr__(self):
        if self.expr:
            return self.repr(self.name, self.type, self.expr)
        else:
            return self.repr(self.name, self.type)

class Evaluate(Statement):

    @match(Expression)
    def __init__(self, expr):
        self.expr = expr

    @property
    def children(self):
        yield self.expr

    def __repr__(self):
        return self.repr(self.expr)

class Return(Statement):

    @match(choice(Expression, None))
    def __init__(self, expr):
        self.expr = expr

    @property
    def children(self):
        if self.expr is not None:
            yield self.expr

    def __repr__(self):
        return self.repr(self.expr)

class Assign(Statement):

    @match(Var, Expression)
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    @property
    def children(self):
        yield self.lhs
        yield self.rhs

    def __repr__(self):
        return self.repr(self.lhs, self.rhs)

class If(Statement):

    @match(Expression, Block, Block)
    def __init__(self, predicate, consequence, alternative):
        self.predicate = predicate
        self.consequence = consequence
        self.alternative = alternative

    @match(Expression, Statement, Statement)
    def __init__(self, predicate, consequence, alternative):
        self.__init__(predicate, Block(consequence), Block(alternative))

    @match(Expression, Expression, Expression)
    def __init__(self, predicate, consequence, alternative):
        self.__init__(predicate, Block(consequence), Block(alternative))

    @match(Expression, Expression, Statement)
    def __init__(self, predicate, consequence, alternative):
        self.__init__(predicate, Block(consequence), Block(alternative))

    @match(Expression, Statement, Expression)
    def __init__(self, predicate, consequence, alternative):
        self.__init__(predicate, Block(consequence), Block(alternative))

    @property
    def children(self):
        yield self.predicate
        yield self.consequence
        yield self.alternative

    def collisions(self, names):
        for c in self.consequence.collisions(names):
            yield c
        for c in self.alternative.collisions(names):
            yield c

    def __repr__(self):
        return self.repr(self.predicate, self.consequence, self.alternative)

class While(Statement):

    @match(Expression, Block)
    def __init__(self, predicate, body):
        self.predicate = predicate
        self.body = body

    @match(Expression, many(Statement))
    def __init__(self, predicate, *statements):
        self.__init__(predicate, Block(statements))

    @property
    def children(self):
        yield self.predicate
        yield self.body

    def collisions(self, names):
        return self.body.collisions(names)

    def __repr__(self):
        return self.repr(self.predicate, self.body)


class SimpleStatement(Statement):
    def __init__(self):
        pass

    @property
    def children(self):
        if False: yield

    def collisions(self, names):
        if False: yield

    def __repr__(self):
        return self.repr()

class Break(SimpleStatement):
    pass

class Continue(SimpleStatement):
    pass


class Check(Definition):
    """ Check is a parameter-less void function that should get picked up by the target unit-test framework """

    @match(basestring, many(Statement))
    def __init__(self, name, *body):
        self.__init__(Name(name), Block(body))

    @match(Name, Block)
    def __init__(self, name, body):
        self.name = name
        self.body = body

    @property
    def children(self):
        yield self.name
        yield self.body

    def __repr__(self):
        return self.repr(self.name, self.body)


class TestClass(Class):
    """ Marker for container of TestMethods """
    pass

class TestMethod(Method):
    """ a method equivalent of a Check """
    pass

class NativeTestAssertion(Statement):
    @match(Expression, Expression)
    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual

    @property
    def children(self):
        yield self.expected
        yield self.actual

    def __repr__(self):
        return self.repr(self.expected, self.actual)


class AssertEqual(NativeTestAssertion):
    pass

class AssertNotEqual(NativeTestAssertion):
    pass



# Import of code oustide of quark to quark native functions

class NativeImport(IR):
    @match(basestring, choice(basestring, None))
    def __init__(self, module, alias):
        self.module = module
        self.alias = alias

    @property
    def children(self):
        if False: yield

    def __repr__(self):
        return self.repr(self.module, self.alias)

# a mapping of replacement keys to target-rendered expressions
class TemplateContext(IR):
    @match(many((basestring, choice(AbstractType, Expression, Ref))))
    def __init__(self, *mappings):
        self.mappings = mappings

    @property
    def children(self):
        for name, expr in self.mappings:
            yield expr

    def __repr__(self):
        return self.repr(*self.mappings)

# a template text that will have template replacement variables
# substituted with a target-evaluated TemplateContext. We'll just use
# string.format facility, so template replacement variables should be
# encoded as {replaceme}

class TemplateText(IR):
    @match(basestring, (many(NativeImport),), basestring)
    def __init__(self, target, imports, template):
        self.target = target
        self.imports = imports
        self.template = template

    @property
    def children(self):
        for imp in self.imports:
            yield imp

    def __repr__(self):
        return self.repr(self.target, self.imports, tree.multiline(self.template))

# a native function instantiated by frontend. The target will
# substitute the function body with the TemplateText that matches
# target by name
class NativeFunction(Function):
    @match(Name, AbstractType, many(Param), TemplateContext, many(TemplateText))
    def __init__(self, name, type, *args):
        params = [p for p in args if isinstance(p, Param)]
        context = [p for p in args if isinstance(p, TemplateContext)]
        assert len(context) == 1
        context = context[0]
        cases = [p for p in args if isinstance(p, TemplateText)]
        self.__init__(name, type, *(params + [NativeBlock(context, *cases)]))

# a native function block.  The target will
# substitute the function body with the TemplateText that matches
# target by name
class NativeBlock(IR):
    @match(TemplateContext, many(TemplateText))
    def __init__(self, context, *cases):
        self.context = context
        self.cases = cases

    @match(basestring, (many(NativeImport),), (many(choice(basestring, Expression, AbstractType)),))
    def __init__(self, target, imports, content):
        context = []
        template = []
        for el in content:
            if isinstance(el, IR):
                key = "{k%dy}" % len(context)
                context.append((key[1:-1], el))
                template.append(key)
            else:
                template.append(el)
        self.context = TemplateContext(*context)
        self.cases = (TemplateText(target, imports, "".join(template)), )

    @property
    def children(self):
        yield self.context
        for c in self.cases:
            yield c

    def __repr__(self):
        return self.repr(self.context, *self.cases)


class Annotation(tree.annotation):
    pass

class Doc(Annotation):
    @match(basestring)
    def __init__(self, doc):
        self.doc = doc

    def __repr__(self):
        return self.repr(tree.multiline(self.doc))


class Checksum(Annotation):
    @match(basestring)
    def __init__(self, checksum):
        self.checksum = checksum

    def __repr__(self):
        return self.repr(self.checksum)

@match(choice(Package, Namespace))
def restructure(pkg):
    """ Introduce Namespaces into a flat package """
    prefix = pkg.name.path
    children = []
    def keyfunc(dfn):
        assert pkg.name.package == dfn.name.package, "unexpected package %s %s" % (pkg.name, dfn.name)
        assert prefix == dfn.name.path[:len(prefix)]
        return dfn.name.path[:len(prefix)+1]
    for k, g in groupby(sorted(pkg.definitions, key=keyfunc), keyfunc):
        nested = []
        for dfn in g:
            if dfn.name.path == k:
                children.append(dfn)
            else:
                nested.append(dfn)
        if nested:
            children.append(restructure(Namespace(
                NamespaceName(pkg.name.package, *k),
                *nested)))
    return pkg.__class__(pkg.name.copy(), *children)

@match(Package)
def model_externals(pkg):
    """ Introduce external definitions to IR """
    q = tree.Query(pkg)
    names = filter(tree.isa(Name), tree.walk_dfs(pkg))
    refs = filter(tree.isa(Ref), tree.walk_dfs(pkg))
    # group refs by usage
    def first(t):
        t[0]
    def second(t):
        t[1]
    uses = dict(
        (k, dict(
            (first(kk), map(second, gg))
            for kk, gg in groupby(sorted(
                    ((type(q.parent(ref)), ref)
                     for ref in g)))))
        for k, g in groupby(sorted(refs)))
    unresolved = set(uses) - set(names)
    def keyfunc(ref):
        return ref.package
    def external(ref):
        assert len(uses[ref]) == 1, "Incosistent use of %s" % uses[ref]
        return external_kind(q.parent(ref))(Name(ref.package, *ref.path))
    externals = map(restructure, (
        ExternalPackage(*map(external, g))
        for k, g in groupby(sorted(unresolved, key=keyfunc), keyfunc)))
    return tuple(externals)

@match(Invoke)
def external_kind(use):
    return ExternalFunction
@match(InterfaceType)
def external_kind(use):
    return ExternalInterface
@match(IR)
def external_kind(use):
    assert False, "Broken FFI contract with external use: %r" % use

@match(Package)
def reconstruct(pkg):
    """ tie together a restructured package and all referenced externals """
    return Root(restructure(pkg), *model_externals(pkg))

def exportable(v):
    mro = getattr(v, "__mro__", ())
    return (IR in mro) or (Annotation in mro)

__all__ = [n for n,v in globals().items() if exportable(v)]
