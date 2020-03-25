from typing import *
from sccd.syntax.expression import *

# A statement is NOT an expression.
class Statement(ABC):
    # Execution typically has side effects.
    @abstractmethod
    def exec(self, current_state, events, datamodel):
        pass

    @abstractmethod
    def init_stmt(self, scope):
        pass

    @abstractmethod
    def render(self) -> str:
        pass

@dataclass
class Assignment(Statement):
    lhs: LValue
    operator: str # token value from the grammar.
    rhs: Expression

    def init_stmt(self, scope):
        rhs_t = self.rhs.init_rvalue(scope)
        self.lhs.init_lvalue(scope, rhs_t)

    def exec(self, current_state, events, datamodel):
        val = self.rhs.eval(current_state, events, datamodel)
        offset = self.lhs.eval_lvalue(current_state, events, datamodel).offset

        def load():
            return datamodel.load(offset)
        def store(val):
            datamodel.store(offset, val)

        def assign():
            store(val)
        def increment():
            store(load() + val)
        def decrement():
            store(load() - val)
        def multiply():
            store(load() * val)
        def divide():
            store(load() / val)

        {
            "=": assign,
            "+=": increment,
            "-=": decrement,
            "*=": multiply,
            "/=": divide,
        }[self.operator]()

    def render(self) -> str:
        return self.lhs.render() + ' ' + self.operator + ' ' + self.rhs.render()

@dataclass
class Block(Statement):
    stmts: List[Statement]

    def init_stmt(self, scope):
        local_scope = Scope("local", scope)
        for stmt in self.stmts:
            stmt.init_stmt(local_scope)

    def exec(self, current_state, events, datamodel):
        for stmt in self.stmts:
            stmt.exec(current_state, events, datamodel)

    def render(self) -> str:
        result = ""
        for stmt in self.stmts:
            result += stmt.render() + ' '
        return result

# e.g. a function call
@dataclass
class ExpressionStatement(Statement):
    expr: Expression

    def init_stmt(self, scope):
        self.expr.init_rvalue(scope)

    def exec(self, current_state, events, datamodel):
        self.expr.eval(current_state, events, datamodel)

    def render(self) -> str:
        return self.expr.render()
