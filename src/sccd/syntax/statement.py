from typing import *
from sccd.syntax.expression import *

# A statement is NOT an expression.
class Statement(ABC):
    # Execution typically has side effects.
    @abstractmethod
    def exec(self, ctx: EvalContext):
        pass

    @abstractmethod
    def init_stmt(self, scope: Scope):
        pass

    @abstractmethod
    def render(self) -> str:
        pass

@dataclass
class Assignment(Statement):
    lhs: LValue
    operator: str # token value from the grammar.
    rhs: Expression

    def init_stmt(self, scope: Scope):
        rhs_t = self.rhs.init_rvalue(scope)
        self.lhs.init_lvalue(scope, rhs_t)

    def exec(self, ctx: EvalContext):
        rhs_val = self.rhs.eval(ctx)
        variable = self.lhs.eval_lvalue(ctx)

        def load():
            return variable.load(ctx)
        def store(val):
            variable.store(ctx, val)

        def assign():
            store(rhs_val)
        def increment():
            store(load() + rhs_val)
        def decrement():
            store(load() - rhs_val)
        def multiply():
            store(load() * rhs_val)
        def divide():
            store(load() / rhs_val)

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

    def init_stmt(self, scope: Scope):
        self.scope = Scope("local", scope)
        for stmt in self.stmts:
            stmt.init_stmt(self.scope)

    def exec(self, ctx: EvalContext):
        ctx.memory.grow_stack(self.scope)
        for stmt in self.stmts:
            stmt.exec(ctx)
        ctx.memory.shrink_stack()

    def render(self) -> str:
        result = ""
        for stmt in self.stmts:
            result += stmt.render() + ' '
        return result

# e.g. a function call
@dataclass
class ExpressionStatement(Statement):
    expr: Expression

    def init_stmt(self, scope: Scope):
        self.expr.init_rvalue(scope)

    def exec(self, ctx: EvalContext):
        self.expr.eval(ctx)

    def render(self) -> str:
        return self.expr.render()

@dataclass
class ReturnStatement(Statement):
    expr: Expression

    def init_stmt(self, scope: Scope):
        pass
