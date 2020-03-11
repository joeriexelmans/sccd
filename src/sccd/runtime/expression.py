from abc import *
from typing import *
from dataclasses import *

class Variable:
    def __init__(self, value):
        self.value = value

class DataModel:
    def __init__(self, names: Dict[str, Variable]):
        self.names = names


class Expression(ABC):
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

class Statement(ABC):
    @abstractmethod
    def exec(self, events, datamodel):
        pass


@dataclass
class Identifier(LHS):
    identifier: str

    def lhs(self, events, datamodel):
        return datamodel.names[self.identifier]

    def render(self):
        return self.identifier

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
class Array(Expression):
    elements: List[Any]

    def eval(self, events, datamodel):
        return [e.eval(events, datamodel) for e in self.elements]

    def render(self):
        return '['+','.join([e.render() for e in self.elements])+']'

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


            "and": lambda x,y: x and y,
            "or": lambda x,y: x or y,
            "==": lambda x,y: x == y,
            "!=": lambda x,y: x != y,
            ">": lambda x,y: x > y,
            ">=": lambda x,y: x >= y,
            "<": lambda x,y: x < y,
            "<=": lambda x,y: x <= y,
            "+": lambda x,y: x + y,
            "-": lambda x,y: x - y,
            "*": lambda x,y: x * y,
            "/": lambda x,y: x / y,
            "//": lambda x,y: x // y,
            "%": lambda x,y: x % y,
            "**": lambda x,y: x ** y,
        }[self.operator](self.lhs.eval(events, datamodel), self.rhs.eval(events, datamodel))

    def render(self):
        return self.lhs.render() + ' ' + self.operator + ' ' + self.rhs.render()

@dataclass
class UnaryExpression(Expression):
    operator: str # token name from the grammar.
    expr: Expression

    def eval(self, events, datamodel):
        return {
            "NOT": lambda x: not x,
            "MINUS": lambda x: -x,
        }[self.operator](self.expr.eval(events, datamodel))

@dataclass
class Assignment(Statement):
    lhs: LHS
    rhs: Expression

    def exec(self, events, datamodel):
        self.lhs.lhs(events, datamodel).value = rhs.eval(events, datamodel)