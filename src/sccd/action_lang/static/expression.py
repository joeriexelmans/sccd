from abc import *
from typing import *
from dataclasses import *
from sccd.util.duration import *
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
class StaticTypeError(ModelError):
    pass

class Expression(ABC):
    # Run static analysis on the expression.
    # Must be called exactly once on each expression, before any call to eval is made.
    # Determines the static type of the expression. May throw if there is a type error.
    # Returns static type of expression.
    @abstractmethod
    def init_expr(self, scope: Scope) -> SCCDType:
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
    @abstractmethod
    def init_lvalue(self, scope: Scope, rhs_type: SCCDType):
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

    def init_expr(self, scope: Scope) -> SCCDType:
        self.offset, type = scope.get_rvalue(self.name)
        return type

    def init_lvalue(self, scope: Scope, type):
        self.offset = scope.put_lvalue(self.name, type)

    def assign(self, memory: MemoryInterface, value: Any):
        memory.store(self.offset, value)

    def eval(self, memory: MemoryInterface):
        return memory.load(self.offset)

    def render(self):
        return self.name

@dataclass
class FunctionCall(Expression):
    function: Expression
    params: List[Expression]

    def init_expr(self, scope: Scope) -> SCCDType:
        function_type = self.function.init_expr(scope)
        if not isinstance(function_type, SCCDFunction):
            raise StaticTypeError("Function call: Expression '%s' is not a function" % self.function.render())

        formal_types = function_type.param_types
        return_type = function_type.return_type

        actual_types = [p.init_expr(scope) for p in self.params]
        if len(formal_types) != len(actual_types):
            raise StaticTypeError("Function call, expected %d arguments, but %d were given." % (len(formal_types), len(actual_types)))
        for i, (formal, actual) in enumerate(zip(formal_types, actual_types)):
            if formal != actual:
                raise StaticTypeError("Function call, argument %d: %s is not expected type %s, instead is %s" % (i, self.params[i].render(), str(formal), str(actual)))
        return return_type

    def eval(self, memory: MemoryInterface):
        f = self.function.eval(memory)
        p = [p.eval(memory) for p in self.params]
        return f(memory, *p)

    def render(self):
        return self.function.render()+'('+','.join([p.render() for p in self.params])+')'

# Used in EventDecl and FunctionDeclaration
@dataclass
class ParamDecl:
    name: str
    formal_type: SCCDType
    offset: Optional[int] = None

    def init_param(self, scope: Scope):
        self.offset = scope.declare(self.name, self.formal_type)

    def render(self):
        return self.name + ":" + str(self.formal_type)

@dataclass
class FunctionDeclaration(Expression):
    params_decl: List[ParamDecl]
    body: 'Statement'
    scope: Optional[Scope] = None

    def init_expr(self, scope: Scope) -> SCCDType:
        self.scope = Scope("function", scope)
        # Reserve space for arguments on stack
        for p in self.params_decl:
            p.init_param(self.scope)
        ret = self.body.init_stmt(self.scope)
        return_type = ret.get_return_type()
        return SCCDFunction([p.formal_type for p in self.params_decl], return_type)

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

    def init_lvalue(self, scope: Scope, type):
        if not isinstance(self.array, LValue):
            raise StaticTypeError("Array indexation as LValue: Expression '%s' must be an LValue" % self.array.render())

        self.array.init_lvalue(scope, SCCDArray(element_type=type))

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

    def eval(self, memory: MemoryInterface):
        return self.string

    def render(self):
        return '"'+self.string+'"'


@dataclass
class IntLiteral(Expression):
    i: int 

    def init_expr(self, scope: Scope) -> SCCDType:
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

    def eval(self, memory: MemoryInterface):
        return self.f

    def render(self):
        return str(self.f)

@dataclass
class BoolLiteral(Expression):
    b: bool 

    def init_expr(self, scope: Scope) -> SCCDType:
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

    def eval(self, memory: MemoryInterface):
        return [e.eval(memory) for e in self.elements]

    def render(self):
        return '['+','.join([e.render() for e in self.elements])+']'

# Does not add anything semantically, but ensures that when rendering an expression,
# the parenthesis are not lost
@dataclass
class Group(Expression):
    subexpr: Expression

    def init_expr(self, scope: Scope) -> SCCDType:
        return self.subexpr.init_expr(scope)

    def eval(self, memory: MemoryInterface):
        return self.subexpr.eval(memory)

    def render(self):
        return '('+self.subexpr.render()+')'

@dataclass
class BinaryExpression(Expression):
    lhs: Expression
    operator: str # token name from the grammar.
    rhs: Expression

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

        t = {
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

        if t is None:
            raise StaticTypeError("Illegal types for '%s'-operation: %s and %s" % (self.operator, lhs_t, rhs_t))

        return t

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

    def init_expr(self, scope: Scope) -> SCCDType:
        expr_type = self.expr.init_expr(scope)

        def logical():
            if expr_type.is_bool_castable():
                return SCCDBool
                
        def neg():
            if expr_type.is_neg():
                return expr_type

        t = {
            "not": logical,
            "-":   neg,
        }[self.operator]()

        if t is None:
            raise StaticTypeError("Illegal type for unary '%s'-expression: %s" % (self.operator, expr_type))

        return t

    def eval(self, memory: MemoryInterface):
        return {
            "not": lambda x: not x.eval(memory),
            "-": lambda x: - x.eval(memory),
        }[self.operator](self.expr)

    def render(self):
        return self.operator + ' ' + self.expr.render()
