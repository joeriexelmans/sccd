from typing import *
from sccd.syntax.expression import *

# A statement is NOT an expression.
class Statement(ABC):
    # Execution typically has side effects.
    @abstractmethod
    def exec(self, events, datamodel):
        pass

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
