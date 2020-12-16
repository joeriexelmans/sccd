from abc import *
from typing import *
from dataclasses import *
from sccd.util.duration import *
from sccd.util.visitable import *
from sccd.action_lang.static.scope import *

class MemoryInterface(ABC):

  @abstractmethod
  def current_frame(self) -> 'StackFrame':
    pass

  @abstractmethod
  def push_frame(self, scope: Scope):
    pass

  @abstractmethod
  def push_frame_w_context(self, scope: Scope, context: 'StackFrame'):
    pass

  @abstractmethod
  def pop_frame(self):
    pass

  @abstractmethod
  def load(self, offset: int) -> Any:
    pass

  @abstractmethod
  def store(self, offset: int, value: Any):
    pass

# Thrown if the type checker encountered something illegal.
# Not to be confused with Python's TypeError exception.
class StaticTypeError(ModelStaticError):
    pass

class Expression(ABC, Visitable):
    # Run static analysis on the expression.
    # Must be called exactly once on each expression, before any call to eval is made.
    # Determines the static type of the expression. May throw if there is a type error.
    # Returns static type of expression.
    @abstractmethod
    def init_expr(self, scope: Scope) -> SCCDType:
        pass

    # Returns static type of expression.
    @abstractmethod
    def get_type(self) -> SCCDType:
        pass

    # Evaluate the expression.
    # Evaluation may have side effects.
    @abstractmethod
    def eval(self, memory: MemoryInterface):
        pass

    @abstractmethod
    def render(self) -> str:
        pass

# The LValue type is any type that can serve as an expression OR an LValue (left hand of assignment)
# Either 'init_expr' or 'init_lvalue' is called to initialize the LValue.
# Then either 'eval' or 'eval_lvalue' can be called any number of times.
class LValue(Expression):
    # Initialize the LValue as an LValue.
    # Returns whether LValue was initialized, or just re-assigned another value.
    @abstractmethod
    def init_lvalue(self, scope: Scope, rhs_t: SCCDType, rhs: Expression) -> bool:
        pass

    # Should return offset relative to current context stack frame.
    #   offset ∈ [0, +∞[ : variable's memory address is within current scope
    #   offset ∈ ]-∞, 0[ : variable's memory address is in a parent scope (or better: 'context scope')
    @abstractmethod
    def assign(self, memory: MemoryInterface, value: Any):
        pass

@dataclass
class Identifier(LValue):
    name: str

    offset: Optional[int] = None
    type: Optional[SCCDType] = None
    is_lvalue: Optional[bool] = None
    is_init: Optional[bool] = None

    # is_function_call_result: Optional[SCCDFunctionCallResult] = None

    def init_expr(self, scope: Scope) -> SCCDType:
        self.offset, self.type = scope.get_rvalue(self.name)
        self.is_init = False
        self.is_lvalue = False
        return self.type

    def get_type(self) -> SCCDType:
        return self.type

    def init_lvalue(self, scope: Scope, rhs_t: SCCDType, rhs: Expression) -> bool:
        # if isinstance(rhs_t, SCCDFunctionCallResult):
            # self.is_function_call_result = rhs_t
            # rhs_t = rhs_t.return_type
        self.is_lvalue = True
        self.offset, self.is_init = scope.put_lvalue(self.name, rhs_t, rhs)
        return self.is_init

    def assign(self, memory: MemoryInterface, value: Any):
        memory.store(self.offset, value)

    def eval(self, memory: MemoryInterface):
        return memory.load(self.offset)

    def render(self):
        return self.name


@dataclass
class FunctionCall(Expression):
    function: Expression # an identifier, or another function call
    params: List[Expression]

    return_type: Optional[SCCDType] = None
    function_being_called: Optional['FunctionDeclaration'] = None

    def init_expr(self, scope: Scope) -> SCCDType:
        function_type = self.function.init_expr(scope)

        # A FunctionCall can be a call on a regular function, or a closure object
        if isinstance(function_type, SCCDClosureObject):
            # For static analysis, we treat calls on closure objects just like calls on regular functions.
            function_type = function_type.function_type

        if not isinstance(function_type, SCCDFunction):
            raise StaticTypeError("Function call: Expression '%s' is not a function" % self.function.render())

        self.function_being_called = function_type.function

        formal_types = function_type.param_types
        self.return_type = function_type.return_type

        actual_types = [p.init_expr(scope) for p in self.params]
        if len(formal_types) != len(actual_types):
            raise StaticTypeError("Function call, expected %d arguments, but %d were given." % (len(formal_types), len(actual_types)))
        for i, (formal, actual) in enumerate(zip(formal_types, actual_types)):
            if formal != actual:
                raise StaticTypeError("Function call, argument %d: %s is not expected type %s, instead is %s" % (i, self.params[i].render(), str(formal), str(actual)))

        # The type of a function call is the return type of the function called
        return self.return_type

    def get_type(self) -> SCCDType:
        return self.return_type

    def eval(self, memory: MemoryInterface):
        f = self.function.eval(memory)
        p = [p.eval(memory) for p in self.params]
        return f(memory, *p)

    def render(self):
        return self.function.render()+'('+','.join([p.render() for p in self.params])+')'

# Used in EventDecl and FunctionDeclaration
@dataclass
class ParamDecl(Visitable):
    name: str
    formal_type: SCCDType
    offset: Optional[int] = None

    def init_param(self, scope: Scope):
        self.offset = scope.declare(self.name, self.formal_type)

    def render(self):
        return self.name + ":" + str(self.formal_type)

@dataclass(eq=False) # eq=False: make it hashable (plus, we don't need auto eq)
class FunctionDeclaration(Expression):
    params_decl: List[ParamDecl]
    body: 'Statement'
    scope: Optional[Scope] = None
    return_type: Optional[SCCDType] = None
    type: Optional[SCCDFunction] = None

    def init_expr(self, scope: Scope) -> SCCDType:
        self.scope = Scope("function", scope)
        # Reserve space for arguments on stack
        for p in self.params_decl:
            p.init_param(self.scope)
        ret = self.body.init_stmt(self.scope)
        self.return_type = ret.get_return_type()

        if isinstance(self.return_type, SCCDFunction) and self.return_type.function.scope.parent is self.scope:
            # Called function returns a closure object
            self.return_type = SCCDClosureObject(self.scope, function_type=self.return_type)
        self.type = SCCDFunction([p.formal_type for p in self.params_decl], self.return_type, function=self)
        return self.type

    def get_type(self) -> SCCDType:
        return self.type

    def eval(self, memory: MemoryInterface):
        context: 'StackFrame' = memory.current_frame()
        def FUNCTION(memory: MemoryInterface, *params):
            memory.push_frame_w_context(self.scope, context)
            # Copy arguments to stack
            for val, p in zip(params, self.params_decl):
                memory.store(p.offset, val)
            ret = self.body.exec(memory)
            memory.pop_frame()
            return ret.val
        return FUNCTION

    def render(self) -> str:
        return "func(%s) [...]" % ", ".join(p.render() for p in self.params_decl) # todo

@dataclass
class ArrayIndexed(LValue):
    array: Expression
    index: Expression

    def init_expr(self, scope: Scope) -> SCCDType:
        array_type = self.array.init_expr(scope)
        if not isinstance(array_type, SCCDArray):
            raise StaticTypeError("Array indexation: Expression '%s' is not an array" % self.array.render())
        index_type = self.index.init_expr(scope)
        if index_type is not SCCDInt:
            raise StaticTypeError("Array indexation: Expression '%s' is not an integer" % self.index_type.render())
        return array_type.element_type

    def get_type(self) -> SCCDType:
        return self.array.get_type().element_type

    def init_lvalue(self, scope: Scope, rhs_t: SCCDType, rhs: Expression) -> bool:
        if not isinstance(self.array, LValue):
            raise StaticTypeError("Array indexation as LValue: Expression '%s' must be an LValue" % self.array.render())

        return self.array.init_lvalue(scope, SCCDArray(element_type=type), rhs)

    def assign(self, memory: MemoryInterface, value):
        self.array.eval(memory)[self.index.eval(memory)] = value

    def render(self):
        return self.name

    def eval(self, memory: MemoryInterface):
        index = self.index.eval()
        return array.eval(memory)[index]

    def render(self):
        return self.array.render() + '[' + self.index.render() + ']'

@dataclass
class StringLiteral(Expression):
    string: str

    def init_expr(self, scope: Scope) -> SCCDType:
        return SCCDString

    def get_type(self) -> SCCDType:
        return SCCDString

    def eval(self, memory: MemoryInterface):
        return self.string

    def render(self):
        return '"'+self.string+'"'


@dataclass
class IntLiteral(Expression):
    i: int 

    def init_expr(self, scope: Scope) -> SCCDType:
        return SCCDInt

    def get_type(self) -> SCCDType:
        return SCCDInt

    def eval(self, memory: MemoryInterface):
        return self.i

    def render(self):
        return str(self.i)

@dataclass
class FloatLiteral(Expression):
    f: float

    def init_expr(self, scope: Scope) -> SCCDType:
        return SCCDFloat

    def get_type(self) -> SCCDType:
        return SCCDFloat

    def eval(self, memory: MemoryInterface):
        return self.f

    def render(self):
        return str(self.f)

@dataclass
class BoolLiteral(Expression):
    b: bool 

    def init_expr(self, scope: Scope) -> SCCDType:
        return SCCDBool

    def get_type(self) -> SCCDType:
        return SCCDBool

    def eval(self, memory: MemoryInterface):
        return self.b

    def render(self):
        return "true" if self.b else "false"

@dataclass
class DurationLiteral(Expression):
    d: Duration

    def init_expr(self, scope: Scope) -> SCCDType:
        return SCCDDuration

    def get_type(self) -> SCCDType:
        return SCCDDuration

    def eval(self, memory: MemoryInterface):
        return self.d

    def render(self):
        return str(self.d)

@dataclass
class Array(Expression):
    elements: List[Any]

    element_type: Optional[SCCDType] = None

    def init_expr(self, scope: Scope) -> SCCDType:
        for e in self.elements:
            t = e.init_expr(scope)
            if self.element_type and self.element_type != t:
                raise StaticTypeError("Mixed element types in Array expression: %s and %s" % (str(self.element_type), str(t)))
            self.element_type = t

        return SCCDArray(self.element_type)

    def get_type(self) -> SCCDType:
        return SCCDArray(self.element_type)

    def eval(self, memory: MemoryInterface):
        return [e.eval(memory) for e in self.elements]

    def render(self):
        return '['+','.join([e.render() for e in self.elements])+']'

# A group of parentheses in the concrete syntax.
# Does not add anything semantically, but allows us to go back from abstract to concrete textual syntax without weird rules
@dataclass
class Group(Expression):
    subexpr: Expression

    def init_expr(self, scope: Scope) -> SCCDType:
        return self.subexpr.init_expr(scope)

    def get_type(self) -> SCCDType:
        return self.subexpr.get_type()

    def eval(self, memory: MemoryInterface):
        return self.subexpr.eval(memory)

    def render(self):
        return '('+self.subexpr.render()+')'

@dataclass
class BinaryExpression(Expression):
    lhs: Expression
    operator: str # token name from the grammar.
    rhs: Expression

    type: Optional[SCCDType] = None

    def init_expr(self, scope: Scope) -> SCCDType:
        lhs_t = self.lhs.init_expr(scope)
        rhs_t = self.rhs.init_expr(scope)

        def logical():
            if lhs_t.is_bool_castable() and rhs_t.is_bool_castable():
                return SCCDBool

        def eq():
            if lhs_t.is_eq(rhs_t):
                return SCCDBool

        def ord():
            if lhs_t.is_ord(rhs_t):
                return SCCDBool

        def sum():
            if lhs_t.is_summable(rhs_t):
                return lhs_t

        def mult():
            return lhs_t.mult(rhs_t)

        def div():
            return lhs_t.div(rhs_t)

        def floordiv():
            return lhs_t.floordiv(rhs_t)

        def exp():
            return lhs_t.exp(rhs_t)

        self.type = {
            "and": logical,
            "or":  logical,
            "==":  eq,
            "!=":  eq,
            ">":   ord,
            ">=":  ord,
            "<":   ord,
            "<=":  ord,
            "+":   sum,
            "-":   sum,
            "*":   mult,
            "/":   div,
            "//":  floordiv,
            "%":   floordiv,
            "**":  exp,
        }[self.operator]()

        if self.type is None:
            raise StaticTypeError("Illegal types for '%s'-operation: %s and %s" % (self.operator, lhs_t, rhs_t))

        return self.type

    def get_type(self) -> SCCDType:
        return self.type

    def eval(self, memory: MemoryInterface):
        return {
            "and": lambda x,y: x and y.eval(memory),
            "or": lambda x,y: x or y.eval(memory),
            "==": lambda x,y: x == y.eval(memory),
            "!=": lambda x,y: x != y.eval(memory),
            ">": lambda x,y: x > y.eval(memory),
            ">=": lambda x,y: x >= y.eval(memory),
            "<": lambda x,y: x < y.eval(memory),
            "<=": lambda x,y: x <= y.eval(memory),
            "+": lambda x,y: x + y.eval(memory),
            "-": lambda x,y: x - y.eval(memory),
            "*": lambda x,y: x * y.eval(memory),
            "/": lambda x,y: x / y.eval(memory),
            "//": lambda x,y: x // y.eval(memory),
            "%": lambda x,y: x % y.eval(memory),
            "**": lambda x,y: x ** y.eval(memory),
        }[self.operator](self.lhs.eval(memory), self.rhs) # Borrow Python's lazy evaluation

    def render(self):
        return self.lhs.render() + ' ' + self.operator + ' ' + self.rhs.render()

@dataclass
class UnaryExpression(Expression):
    operator: str # token value from the grammar.
    expr: Expression

    type: Optional[SCCDType] = None

    def init_expr(self, scope: Scope) -> SCCDType:
        expr_type = self.expr.init_expr(scope)

        def logical():
            if expr_type.is_bool_castable():
                return SCCDBool
                
        def neg():
            if expr_type.is_neg():
                return expr_type

        self.type = {
            "not": logical,
            "-":   neg,
        }[self.operator]()

        if self.type is None:
            raise StaticTypeError("Illegal type for unary '%s'-expression: %s" % (self.operator, expr_type))

        return self.type

    def get_type(self) -> SCCDType:
        return self.type

    def eval(self, memory: MemoryInterface):
        return {
            "not": lambda x: not x.eval(memory),
            "-": lambda x: - x.eval(memory),
        }[self.operator](self.expr)

    def render(self):
        return self.operator + ' ' + self.expr.render()
