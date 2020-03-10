from abc import *
from typing import *
from dataclasses import *

class Variable:
    def __init__(self, value):
        self.value = value

class DataModel:
    def __init__(self, names: Dict[str, Variable]):
        self.names = names

@dataclass
class Expression(ABC):
    pass

    @abstractmethod
    def eval(self, events, datamodel):
        pass

@dataclass
class Identifier(Expression):
    identifier: str

    def eval(self, events, datamodel):
        return datamodel.names[self.identifier].value

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
class Array(Expression):
    elements: List[Any]

    def eval(self, events, datamodel):
        return [e.eval(events, datamodel) for e in self.elements]

    def render(self):
        return '['+','.join([e.render() for e in self.elements])+']'
