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
    # Must be called exactly once on each expression, before any call to eval is made.
    # Determines the static type of the expression. May throw if there is a type error.
    # Returns static type of expression.
    @abstractmethod
    def init_expr(self, scope: Scope) -> SCCDType:
        pass

    # Evaluation should NOT have side effects.
    # Motivation is that the evaluation of a guard condition cannot have side effects.
    @abstractmethod
    def eval(self, memory: MemoryInterface):
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
    def eval_lvalue(self) -> int:
        pass

    # Any type that is an LValue can also serve as an expression!
    def eval(self, memory: MemoryInterface):
        offset = self.eval_lvalue()
        return memory.load(offset)

@dataclass
class Identifier(LValue):
    name: str
    offset: Optional[int] = None

    def init_expr(self, scope: Scope) -> SCCDType:
        self.offset, type = scope.get_rvalue(self.name)
        return type

    def init_lvalue(self, scope: Scope, type):
        self.offset = scope.put_lvalue(self.name, type)

    def eval_lvalue(self) -> int:
        return self.offset

    def render(self):
        return self.name

@dataclass
class FunctionCall(Expression):
    function: Expression
    params: List[Expression]

    type: Optional[type] = None

    def init_expr(self, scope: Scope) -> SCCDType:
        function_type = self.function.init_expr(scope)
        if not isinstance(function_type, SCCDFunction):
            raise StaticTypeError("Function call: Expression '%s' is not a function" % self.function.render())

        formal_types = function_type.param_types
        return_type = function_type.return_type

        actual_types = [p.init_expr(scope) for p in self.params]
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

        def comparison_type():
            same_type()
            return SCCDBool

        def same_type():
            if lhs_t != rhs_t:
                raise StaticTypeError("Mixed LHS and RHS types in '%s' expression: %s and %s" % (self.operator, str(lhs_t), str(rhs_t)))
            return lhs_t

        def mult_type():
            if lhs_t == rhs_t:
                if lhs_t == Duration:
                    raise StaticTypeError("Cannot multiply 'Duration' and 'Duration'")
                return lhs_t
            key = lambda x: {SCCDInt: 1, SCCDFloat: 2, SCCDDuration: 3}[x]
            [smallest_type, largest_type] = sorted([lhs_t, rhs_t], key=key)
            if largest_type == SCCDDuration and smallest_type == SCCDFloat:
                raise StaticTypeError("Cannot multiply 'float' and 'Duration'")
            return largest_type

        return {
            "and": SCCDBool,
            "or":  SCCDBool,
            "==":  comparison_type(),
            "!=":  comparison_type(),
            ">":   comparison_type(),
            ">=":  comparison_type(),
            "<":   comparison_type(),
            "<=":  comparison_type(),
            "+":   same_type(),
            "-":   same_type(),
            "*":   mult_type(),
            "/":   SCCDFloat,
            "//":  same_type(),
            "%":   same_type(),
            "**":  same_type(),
        }[self.operator]

    def eval(self, memory: MemoryInterface):
        
        return {
            "and": lambda x,y: x.eval(memory) and y.eval(memory),
            "or": lambda x,y: x.eval(memory) or y.eval(memory),
            "==": lambda x,y: x.eval(memory) == y.eval(memory),
            "!=": lambda x,y: x.eval(memory) != y.eval(memory),
            ">": lambda x,y: x.eval(memory) > y.eval(memory),
            ">=": lambda x,y: x.eval(memory) >= y.eval(memory),
            "<": lambda x,y: x.eval(memory) < y.eval(memory),
            "<=": lambda x,y: x.eval(memory) <= y.eval(memory),
            "+": lambda x,y: x.eval(memory) + y.eval(memory),
            "-": lambda x,y: x.eval(memory) - y.eval(memory),
            "*": lambda x,y: x.eval(memory) * y.eval(memory),
            "/": lambda x,y: x.eval(memory) / y.eval(memory),
            "//": lambda x,y: x.eval(memory) // y.eval(memory),
            "%": lambda x,y: x.eval(memory) % y.eval(memory),
            "**": lambda x,y: x.eval(memory) ** y.eval(memory),
        }[self.operator](self.lhs, self.rhs) # Borrow Python's lazy evaluation

    def render(self):
        return self.lhs.render() + ' ' + self.operator + ' ' + self.rhs.render()

@dataclass
class UnaryExpression(Expression):
    operator: str # token value from the grammar.
    expr: Expression

    def init_expr(self, scope: Scope) -> SCCDType:
        expr_type = self.expr.init_expr(scope)
        return {
            "not": SCCDBool,
            "-":   expr_type,
        }[self.operator]

    def eval(self, memory: MemoryInterface):
        return {
            "not": lambda x: not x.eval(memory),
            "-": lambda x: - x.eval(memory),
        }[self.operator](self.expr)

    def render(self):
        return self.operator + ' ' + self.expr.render()
