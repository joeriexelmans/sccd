from typing import *
from sccd.syntax.expression import *

# A statement is NOT an expression.
class Statement(ABC):
    # Execution typically has side effects.
    @abstractmethod
    def exec(self, current_state, events, memory):
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

    def exec(self, current_state, events, memory):
        val = self.rhs.eval(current_state, events, memory)
        offset = self.lhs.eval_lvalue(current_state, events, memory).offset

        def load():
            return memory.load(offset)
        def store(val):
            memory.store(offset, val)

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
    scope: Optional[Scope] = None

    def init_stmt(self, scope):
        self.scope = Scope("local", scope)
        for stmt in self.stmts:
            stmt.init_stmt(self.scope)

    def exec(self, current_state, events, memory):
        memory.grow_stack(self.scope)
        for stmt in self.stmts:
            stmt.exec(current_state, events, memory)
        memory.shrink_stack()

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

    def exec(self, current_state, events, memory):
        self.expr.eval(current_state, events, memory)

    def render(self) -> str:
        return self.expr.render()
