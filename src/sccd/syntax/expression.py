from abc import *
from typing import *
from dataclasses import *
from sccd.syntax.datamodel import *
from sccd.util.duration import *

class Expression(ABC):
    # Evaluation should NOT have side effects.
    # Motivation is that the evaluation of a guard condition cannot have side effects.
    @abstractmethod
    def eval(self, events, datamodel):
        pass

    # Types of expressions are statically checked in SCCD.
    # @abstractmethod
    def get_static_type(self) -> type:
        pass

class LHS(Expression):
    @abstractmethod
    def lhs(self, events, datamodel) -> Variable:
        pass

    # LHS types are expressions too!
    def eval(self, events, datamodel):
        return self.lhs(events, datamodel).value

@dataclass
class Identifier(LHS):
    name: str

    def lhs(self, events, datamodel) -> Variable:
        return datamodel.names[self.name]

    def render(self):
        return self.name

@dataclass
class FunctionCall(Expression):
    function: Expression
    parameters: List[Expression]

    def eval(self, events, datamodel):
        f = self.function.eval(events, datamodel)
        p = [p.eval(events, datamodel) for p in self.parameters]
        return f(*p)

    def render(self):
        return self.function.render()+'('+','.join([p.render() for p in self.parameters])+')'

@dataclass
class StringLiteral(Expression):
    string: str

    def eval(self, events, datamodel):
        return self.string

    def render(self):
        return '"'+self.string+'"'

    def get_static_type(self) -> type:
        return str

@dataclass
class IntLiteral(Expression):
    i: int 

    def eval(self, events, datamodel):
        return self.i

    def render(self):
        return str(self.i)

    def get_static_type(self) -> type:
        return int

@dataclass
class BoolLiteral(Expression):
    b: bool 

    def eval(self, events, datamodel):
        return self.b

    def render(self):
        return "true" if self.b else "false"

    def get_static_type(self) -> type:
        return bool

@dataclass
class DurationLiteral(Expression):
    original: Duration

    # All duration expressions in a model evaluate to a duration with the same unit.
    normalized: Optional[Duration] = None

    def eval(self, events, datamodel):
        return self.normalized

    def render(self):
        return self.original.__str__()

    def get_static_type(self) -> type:
        return Duration

@dataclass
class Array(Expression):
    elements: List[Any]
    t: type = None

    def __post_init__(self):
        for e in self.elements:
            t = e.get_static_type()
            if self.t and self.t != t:
                raise Exception("Mixed element types in Array expression: %s and %s" % (str(self.t), str(t)))
            self.t = t

    def eval(self, events, datamodel):
        return [e.eval(events, datamodel) for e in self.elements]

    def render(self):
        return '['+','.join([e.render() for e in self.elements])+']'

    def get_static_type(self) -> type:
        return List[self.t]

# Does not add anything semantically, but ensures that when rendering an expression,
# the parenthesis are not lost
@dataclass
class Group(Expression):
    subexpr: Expression

    def eval(self, events, datamodel):
        return self.subexpr.eval(events, datamodel)

    def render(self):
        return '('+self.subexpr.render()+')'

    def get_static_type(self) -> type:
        return subexpr.get_static_type()

@dataclass
class BinaryExpression(Expression):
    lhs: Expression
    operator: str # token name from the grammar.
    rhs: Expression

    def __post_init__(self):
        lhs_t = self.lhs.get_static_type()
        rhs_t = self.rhs.get_static_type()
        if lhs_t != rhs_t:
            raise Exception("Mixed LHS and RHS types in '%s' expression: %s and %s" % (self.operator, str(lhs_t), str(rhs_t)))

    def eval(self, events, datamodel):
        
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

            "and": lambda x,y: x.eval(events, datamodel) and y.eval(events, datamodel),
            "or": lambda x,y: x.eval(events, datamodel) or y.eval(events, datamodel),
            "==": lambda x,y: x.eval(events, datamodel) == y.eval(events, datamodel),
            "!=": lambda x,y: x.eval(events, datamodel) != y.eval(events, datamodel),
            ">": lambda x,y: x.eval(events, datamodel) > y.eval(events, datamodel),
            ">=": lambda x,y: x.eval(events, datamodel) >= y.eval(events, datamodel),
            "<": lambda x,y: x.eval(events, datamodel) < y.eval(events, datamodel),
            "<=": lambda x,y: x.eval(events, datamodel) <= y.eval(events, datamodel),
            "+": lambda x,y: x.eval(events, datamodel) + y.eval(events, datamodel),
            "-": lambda x,y: x.eval(events, datamodel) - y.eval(events, datamodel),
            "*": lambda x,y: x.eval(events, datamodel) * y.eval(events, datamodel),
            "/": lambda x,y: x.eval(events, datamodel) / y.eval(events, datamodel),
            "//": lambda x,y: x.eval(events, datamodel) // y.eval(events, datamodel),
            "%": lambda x,y: x.eval(events, datamodel) % y.eval(events, datamodel),
            "**": lambda x,y: x.eval(events, datamodel) ** y.eval(events, datamodel),
        }[self.operator](self.lhs, self.rhs) # Borrow Python's lazy evaluation

    def render(self):
        return self.lhs.render() + ' ' + self.operator + ' ' + self.rhs.render()

    def get_static_type(self) -> type:
        return self.lhs.get_static_type()

@dataclass
class UnaryExpression(Expression):
    operator: str # token value from the grammar.
    expr: Expression

    def eval(self, events, datamodel):
        return {
            "not": lambda x: not x.eval(events, datamodel),
            "-": lambda x: - x.eval(events, datamodel),
        }[self.operator](self.expr)

    def render(self):
        return self.operator + ' ' + self.expr.render()

    def get_static_type(self) -> type:
        return self.expr.get_static_type()
