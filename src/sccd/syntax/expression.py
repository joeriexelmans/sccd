from abc import *
from typing import *
from dataclasses import *
from sccd.syntax.scope import *
from sccd.util.duration import *

# to inspect types in Python 3.7
# Python 3.8 already has this built in
import typing_inspect

class Expression(ABC):
    # Must be called exactly once on each expression. May throw.
    # Returns static type of expression.
    @abstractmethod
    def init_rvalue(self, scope) -> type:
        pass

    # Evaluation should NOT have side effects.
    # Motivation is that the evaluation of a guard condition cannot have side effects.
    @abstractmethod
    def eval(self, current_state, events, memory):
        pass

class LValue(Expression):
    @abstractmethod
    def init_lvalue(self, scope, expected_type: type):
        pass

    @abstractmethod
    def eval_lvalue(self, current_state, events, memory) -> Variable:
        pass

    # LValues are expressions too!
    def eval(self, current_state, events, memory):
        variable = self.eval_lvalue(current_state, events, memory)
        return memory.load(variable.offset)


@dataclass
class Identifier(LValue):
    name: str

    variable: Optional[Variable] = None

    def init_rvalue(self, scope) -> type:
        assert self.variable is None
        self.variable = scope.get(self.name)
        # print("init rvalue", self.name, "as", self.variable)
        return self.variable.type

    def init_lvalue(self, scope, expected_type):
        assert self.variable is None
        self.variable = scope.put(self.name, expected_type)
        # print("init lvalue", self.name, "as", self.variable)

    def eval_lvalue(self, current_state, events, memory) -> Variable:
        return self.variable

    def render(self):
        return self.name


@dataclass
class FunctionCall(Expression):
    function: Expression
    parameters: List[Expression]

    type: Optional[type] = None

    def init_rvalue(self, scope) -> type:
        function_type = self.function.init_rvalue(scope)
        if not isinstance(function_type, Callable):
            raise Exception("Function call: Expression '%s' is not callable" % self.function.render())
        formal_types, return_type = typing_inspect.get_args(function_type)
        self.type = return_type

        actual_types = [p.init_rvalue(scope) for p in self.parameters]
        for formal, actual in zip(formal_types, actual_types):
            if formal != actual:
                raise Exception("Function call: Actual types '%s' differ from formal types '%s'" % (actual_types, formal_types))
        return self.type

    def eval(self, current_state, events, memory):
        # print(self.function)
        f = self.function.eval(current_state, events, memory)
        p = [p.eval(current_state, events, memory) for p in self.parameters]
        return f(current_state, events, memory, *p)

    def render(self):
        return self.function.render()+'('+','.join([p.render() for p in self.parameters])+')'


@dataclass
class StringLiteral(Expression):
    string: str

    def init_rvalue(self, scope) -> type:
        return str

    def eval(self, current_state, events, memory):
        return self.string

    def render(self):
        return '"'+self.string+'"'


@dataclass
class IntLiteral(Expression):
    i: int 

    def init_rvalue(self, scope) -> type:
        return int

    def eval(self, current_state, events, memory):
        return self.i

    def render(self):
        return str(self.i)

@dataclass
class BoolLiteral(Expression):
    b: bool 

    def init_rvalue(self, scope) -> type:
        return bool

    def eval(self, current_state, events, memory):
        return self.b

    def render(self):
        return "true" if self.b else "false"

@dataclass
class DurationLiteral(Expression):
    d: Duration

    def init_rvalue(self, scope) -> type:
        return Duration

    def eval(self, current_state, events, memory):
        return self.d

    def render(self):
        return str(self.d)

@dataclass
class Array(Expression):
    elements: List[Any]

    type: Optional[type] = None

    def init_rvalue(self, scope) -> type:
        for e in self.elements:
            t = e.init_rvalue(scope)
            if self.type and self.type != t:
                raise Exception("Mixed element types in Array expression: %s and %s" % (str(self.type), str(t)))
            self.type = t

        return List[self.type]

    def eval(self, current_state, events, memory):
        return [e.eval(current_state, events, memory) for e in self.elements]

    def render(self):
        return '['+','.join([e.render() for e in self.elements])+']'

# Does not add anything semantically, but ensures that when rendering an expression,
# the parenthesis are not lost
@dataclass
class Group(Expression):
    subexpr: Expression

    def init_rvalue(self, scope) -> type:
        return self.subexpr.init_rvalue(scope)

    def eval(self, current_state, events, memory):
        return self.subexpr.eval(current_state, events, memory)

    def render(self):
        return '('+self.subexpr.render()+')'

@dataclass
class BinaryExpression(Expression):
    lhs: Expression
    operator: str # token name from the grammar.
    rhs: Expression

    def init_rvalue(self, scope) -> type:
        lhs_t = self.lhs.init_rvalue(scope)
        rhs_t = self.rhs.init_rvalue(scope)
        if lhs_t != rhs_t:
            raise Exception("Mixed LHS and RHS types in '%s' expression: %s and %s" % (self.operator, str(lhs_t), str(rhs_t)))
        return lhs_t

    def eval(self, current_state, events, memory):
        
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

            "and": lambda x,y: x.eval(current_state, events, memory) and y.eval(current_state, events, memory),
            "or": lambda x,y: x.eval(current_state, events, memory) or y.eval(current_state, events, memory),
            "==": lambda x,y: x.eval(current_state, events, memory) == y.eval(current_state, events, memory),
            "!=": lambda x,y: x.eval(current_state, events, memory) != y.eval(current_state, events, memory),
            ">": lambda x,y: x.eval(current_state, events, memory) > y.eval(current_state, events, memory),
            ">=": lambda x,y: x.eval(current_state, events, memory) >= y.eval(current_state, events, memory),
            "<": lambda x,y: x.eval(current_state, events, memory) < y.eval(current_state, events, memory),
            "<=": lambda x,y: x.eval(current_state, events, memory) <= y.eval(current_state, events, memory),
            "+": lambda x,y: x.eval(current_state, events, memory) + y.eval(current_state, events, memory),
            "-": lambda x,y: x.eval(current_state, events, memory) - y.eval(current_state, events, memory),
            "*": lambda x,y: x.eval(current_state, events, memory) * y.eval(current_state, events, memory),
            "/": lambda x,y: x.eval(current_state, events, memory) / y.eval(current_state, events, memory),
            "//": lambda x,y: x.eval(current_state, events, memory) // y.eval(current_state, events, memory),
            "%": lambda x,y: x.eval(current_state, events, memory) % y.eval(current_state, events, memory),
            "**": lambda x,y: x.eval(current_state, events, memory) ** y.eval(current_state, events, memory),
        }[self.operator](self.lhs, self.rhs) # Borrow Python's lazy evaluation

    def render(self):
        return self.lhs.render() + ' ' + self.operator + ' ' + self.rhs.render()

@dataclass
class UnaryExpression(Expression):
    operator: str # token value from the grammar.
    expr: Expression

    def init_rvalue(self, scope) -> type:
        return self.expr.init_rvalue(scope)

    def eval(self, current_state, events, memory):
        return {
            "not": lambda x: not x.eval(current_state, events, memory),
            "-": lambda x: - x.eval(current_state, events, memory),
        }[self.operator](self.expr)

    def render(self):
        return self.operator + ' ' + self.expr.render()
