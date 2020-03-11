from abc import *
from typing import *
from dataclasses import *

class Variable:
    def __init__(self, value):
        self.value = value

class DataModel:
    def __init__(self):
        self.names: Dict[str, Variable] = {}


class Expression(ABC):
    # Evaluation should NOT have side effects.
    # Motivation is that the evaluation of a guard condition cannot have side effects.
    @abstractmethod
    def eval(self, events, datamodel):
        pass

class LHS(Expression):
    @abstractmethod
    def lhs(self, events, datamodel) -> Variable:
        pass

    # LHS types are expressions too!
    def eval(self, events, datamodel):
        return self.lhs(events, datamodel).value

# A statement is NOT an expression.
class Statement(ABC):
    # Execution typically has side effects.
    @abstractmethod
    def exec(self, events, datamodel):
        pass


@dataclass
class Identifier(LHS):
    name: str

    def lhs(self, events, datamodel):
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

@dataclass
class IntLiteral(Expression):
    i: int 

    def eval(self, events, datamodel):
        return self.i

    def render(self):
        return str(self.i)

@dataclass
class BoolLiteral(Expression):
    b: bool 

    def eval(self, events, datamodel):
        return self.b

    def render(self):
        return "true" if self.b else "false"

@dataclass
class Array(Expression):
    elements: List[Any]

    def eval(self, events, datamodel):
        return [e.eval(events, datamodel) for e in self.elements]

    def render(self):
        return '['+','.join([e.render() for e in self.elements])+']'

# Does not add anything semantically, but ensures that when rendering an expression,
# the parenthesis are not lost
@dataclass
class Group(Expression):
    subexpr: Expression

    def eval(self, events, datamodel):
        return self.subexpr.eval(events, datamodel)

    def render(self):
        return '('+self.subexpr.render()+')'

@dataclass
class BinaryExpression(Expression):
    lhs: Expression
    operator: str # token name from the grammar.
    rhs: Expression

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

@dataclass
class Assignment(Statement):
    lhs: LHS
    operator: str # token value from the grammar.
    rhs: Expression

    def exec(self, events, datamodel):
        rhs = self.rhs.eval(events, datamodel)
        lhs = self.lhs.lhs(events, datamodel)

        def assign(x,y):
            x.value = y
        def increment(x,y):
            x.value += y
        def decrement(x,y):
            x.value -= y
        def multiply(x,y):
            x.value *= y
        def divide(x,y):
            x.value /= y

        {
            "=": assign,
            "+=": increment,
            "-=": decrement,
            "*=": multiply,
            "/=": divide,
        }[self.operator](lhs, rhs)

@dataclass
class Block(Statement):
    stmts: List[Statement]

    def exec(self, events, datamodel):
        for stmt in self.stmts:
            stmt.exec(events, datamodel)
