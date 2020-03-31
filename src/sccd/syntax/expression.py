from abc import *
from typing import *
from dataclasses import *
from sccd.util.duration import *
from sccd.syntax.scope import *

# to inspect types in Python 3.6 and 3.7, we rely on a backporting package
# Python 3.8 already has this in its 'typing' module
import sys
if sys.version_info.minor < 8:
    from typing_inspect import get_args


class Expression(ABC):
    # Must be called exactly once on each expression, before any call to eval is made.
    # Determines the static type of the expression. May throw if there is a type error.
    # Returns static type of expression.
    @abstractmethod
    def init_rvalue(self, scope: Scope) -> type:
        pass

    # Evaluation should NOT have side effects.
    # Motivation is that the evaluation of a guard condition cannot have side effects.
    @abstractmethod
    def eval(self, ctx: EvalContext):
        pass

# The LValue type is any type that can serve as an expression OR an LValue (left hand of assignment)
# Either 'init_rvalue' or 'init_lvalue' is called to initialize the LValue.
# Then either 'eval' or 'eval_lvalue' can be called any number of times.
class LValue(Expression):
    # Initialize the LValue as an LValue. 
    @abstractmethod
    def init_lvalue(self, scope: Scope, expected_type: type):
        pass

    @abstractmethod
    def eval_lvalue(self, ctx: EvalContext) -> Variable:
        pass

    # LValues can also serve as expressions!
    def eval(self, ctx: EvalContext):
        variable = self.eval_lvalue(ctx)
        return variable.load(ctx)

@dataclass
class Identifier(LValue):
    name: str
    variable: Optional[Variable] = None

    def init_rvalue(self, scope: Scope) -> type:
        assert self.variable is None
        self.variable = scope.get(self.name)
        # print("init rvalue", self.name, "as", self.variable)
        return self.variable.type

    def init_lvalue(self, scope: Scope, expected_type):
        assert self.variable is None
        self.variable = scope.put_variable_assignment(self.name, expected_type)
        # print("init lvalue", self.name, "as", self.variable)

    def eval_lvalue(self, ctx: EvalContext) -> Variable:
        return self.variable

    def render(self):
        return self.name

@dataclass
class FunctionCall(Expression):
    function: Expression
    parameters: List[Expression]

    type: Optional[type] = None

    def init_rvalue(self, scope: Scope) -> type:
        function_type = self.function.init_rvalue(scope)
        if not isinstance(function_type, Callable):
            raise Exception("Function call: Expression '%s' is not callable" % self.function.render())
        formal_types, return_type = get_args(function_type)
        self.type = return_type

        # We always secretly pass an EvalContext object with every function call
        # Not visible to the user.
        assert formal_types[0] == EvalContext

        actual_types = [p.init_rvalue(scope) for p in self.parameters]
        for i, (formal, actual) in enumerate(zip(formal_types[1:], actual_types)):
            if formal != actual:
                raise Exception("Function call, argument %d: %s is not expected type %s, instead is %s" % (i, self.parameters[i].render(), str(formal), str(actual)))
        return self.type

    def eval(self, ctx: EvalContext):
        # print(self.function)
        f = self.function.eval(ctx)
        p = [p.eval(ctx) for p in self.parameters]
        return f(ctx, *p)

    def render(self):
        return self.function.render()+'('+','.join([p.render() for p in self.parameters])+')'


@dataclass
class StringLiteral(Expression):
    string: str

    def init_rvalue(self, scope: Scope) -> type:
        return str

    def eval(self, ctx: EvalContext):
        return self.string

    def render(self):
        return '"'+self.string+'"'


@dataclass
class IntLiteral(Expression):
    i: int 

    def init_rvalue(self, scope: Scope) -> type:
        return int

    def eval(self, ctx: EvalContext):
        return self.i

    def render(self):
        return str(self.i)

@dataclass
class BoolLiteral(Expression):
    b: bool 

    def init_rvalue(self, scope: Scope) -> type:
        return bool

    def eval(self, ctx: EvalContext):
        return self.b

    def render(self):
        return "true" if self.b else "false"

@dataclass
class DurationLiteral(Expression):
    d: Duration

    def init_rvalue(self, scope: Scope) -> type:
        return Duration

    def eval(self, ctx: EvalContext):
        return self.d

    def render(self):
        return str(self.d)

@dataclass
class Array(Expression):
    elements: List[Any]

    type: Optional[type] = None

    def init_rvalue(self, scope: Scope) -> type:
        for e in self.elements:
            t = e.init_rvalue(scope)
            if self.type and self.type != t:
                raise Exception("Mixed element types in Array expression: %s and %s" % (str(self.type), str(t)))
            self.type = t

        return List[self.type]

    def eval(self, ctx: EvalContext):
        return [e.eval(ctx) for e in self.elements]

    def render(self):
        return '['+','.join([e.render() for e in self.elements])+']'

# Does not add anything semantically, but ensures that when rendering an expression,
# the parenthesis are not lost
@dataclass
class Group(Expression):
    subexpr: Expression

    def init_rvalue(self, scope: Scope) -> type:
        return self.subexpr.init_rvalue(scope)

    def eval(self, ctx: EvalContext):
        return self.subexpr.eval(ctx)

    def render(self):
        return '('+self.subexpr.render()+')'

@dataclass
class BinaryExpression(Expression):
    lhs: Expression
    operator: str # token name from the grammar.
    rhs: Expression

    def init_rvalue(self, scope: Scope) -> type:
        lhs_t = self.lhs.init_rvalue(scope)
        rhs_t = self.rhs.init_rvalue(scope)
        if lhs_t != rhs_t:
            raise Exception("Mixed LHS and RHS types in '%s' expression: %s and %s" % (self.operator, str(lhs_t), str(rhs_t)))
        return lhs_t

    def eval(self, ctx: EvalContext):
        
        return {
            # "AND": lambda x,y: x and y,
            # "OR": lambda x,y: x or y,
            # "EQ": lambda x,y: x == y,
            # "NEQ": lambda x,y: x != y,
            # "GT": lambda x,y: x > y,
            # "GEQ": lambda x,y: x >= y,
            # "LT": lambda x,y: x < y,
            # "LEQ": lambda x,y: x <= y,
            # "PLUS": lambda x,y: x + y,
            # "MINUS": lambda x,y: x - y,
            # "MULT": lambda x,y: x * y,
            # "DIV": lambda x,y: x / y,
            # "FLOORDIV": lambda x,y: x // y,
            # "MOD": lambda x,y: x % y,
            # "EXP": lambda x,y: x ** y,

            "and": lambda x,y: x.eval(ctx) and y.eval(ctx),
            "or": lambda x,y: x.eval(ctx) or y.eval(ctx),
            "==": lambda x,y: x.eval(ctx) == y.eval(ctx),
            "!=": lambda x,y: x.eval(ctx) != y.eval(ctx),
            ">": lambda x,y: x.eval(ctx) > y.eval(ctx),
            ">=": lambda x,y: x.eval(ctx) >= y.eval(ctx),
            "<": lambda x,y: x.eval(ctx) < y.eval(ctx),
            "<=": lambda x,y: x.eval(ctx) <= y.eval(ctx),
            "+": lambda x,y: x.eval(ctx) + y.eval(ctx),
            "-": lambda x,y: x.eval(ctx) - y.eval(ctx),
            "*": lambda x,y: x.eval(ctx) * y.eval(ctx),
            "/": lambda x,y: x.eval(ctx) / y.eval(ctx),
            "//": lambda x,y: x.eval(ctx) // y.eval(ctx),
            "%": lambda x,y: x.eval(ctx) % y.eval(ctx),
            "**": lambda x,y: x.eval(ctx) ** y.eval(ctx),
        }[self.operator](self.lhs, self.rhs) # Borrow Python's lazy evaluation

    def render(self):
        return self.lhs.render() + ' ' + self.operator + ' ' + self.rhs.render()

@dataclass
class UnaryExpression(Expression):
    operator: str # token value from the grammar.
    expr: Expression

    def init_rvalue(self, scope: Scope) -> type:
        return self.expr.init_rvalue(scope)

    def eval(self, ctx: EvalContext):
        return {
            "not": lambda x: not x.eval(ctx),
            "-": lambda x: - x.eval(ctx),
        }[self.operator](self.expr)

    def render(self):
        return self.operator + ' ' + self.expr.render()
