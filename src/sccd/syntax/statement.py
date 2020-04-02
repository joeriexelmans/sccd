from typing import *
from sccd.syntax.expression import *

@dataclass
class Return:
    ret: bool
    val: Any = None

@dataclass
class ReturnType:
    ret: bool
    type: Optional[type] = None

# A statement is NOT an expression.
class Statement(ABC):
    # Execution typically has side effects.
    @abstractmethod
    def exec(self, ctx: EvalContext) -> Return:
        pass

    @abstractmethod
    def init_stmt(self, scope: Scope) -> ReturnType:
        pass

    @abstractmethod
    def render(self) -> str:
        pass

@dataclass
class Assignment(Statement):
    lhs: LValue
    operator: str # token value from the grammar.
    rhs: Expression

    def init_stmt(self, scope: Scope) -> ReturnType:
        rhs_t = self.rhs.init_rvalue(scope)
        self.lhs.init_lvalue(scope, rhs_t)
        return ReturnType(False)

    def exec(self, ctx: EvalContext) -> Return:
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

        return Return(False)

    def render(self) -> str:
        return self.lhs.render() + ' ' + self.operator + ' ' + self.rhs.render()

@dataclass
class Block(Statement):
    stmts: List[Statement]
    scope: Optional[Scope] = None

    def init_stmt(self, scope: Scope) -> ReturnType:
        self.scope = Scope("local", scope)
        for stmt in self.stmts:
            ret = stmt.init_stmt(self.scope)
            if ret.ret:
                break
        return ret

    def exec(self, ctx: EvalContext) -> Return:
        ctx.memory.grow_stack(self.scope)
        for stmt in self.stmts:
            ret = stmt.exec(ctx)
            if ret.ret:
                break
        ctx.memory.shrink_stack()
        return ret

    def render(self) -> str:
        result = ""
        for stmt in self.stmts:
            result += stmt.render() + '⁏ '
        return result

# e.g. a function call
@dataclass
class ExpressionStatement(Statement):
    expr: Expression

    def init_stmt(self, scope: Scope) -> ReturnType:
        self.expr.init_rvalue(scope)
        return ReturnType(False)

    def exec(self, ctx: EvalContext) -> Return:
        self.expr.eval(ctx)
        return Return(False)

    def render(self) -> str:
        return self.expr.render()

@dataclass
class ReturnStatement(Statement):
    expr: Expression

    def init_stmt(self, scope: Scope) -> ReturnType:
        t = self.expr.init_rvalue(scope)
        return ReturnType(True, t)

    def exec(self, ctx: EvalContext) -> Return:
        val = self.expr.eval(ctx)
        return Return(True, val)

    def render(self) -> str:
        return "return " + self.expr.render()

@dataclass
class IfStatement(Statement):
    cond: Expression
    body: Statement

    def init_stmt(self, scope: Scope) -> ReturnType:
        cond_t = self.cond.init_rvalue(scope)
        # todo: assert cond_t is bool
        ret = self.body.init_stmt(scope) # return type is only if cond evaluates to True...
        return Return(False)

    def exec(self, ctx: EvalContext) -> Return:
        val = self.cond.eval(ctx)
        if val:
            return self.body.exec(ctx)
        return Return(False)

    def render(self) -> str:
        return "if (%s) [[" % self.cond.render() + self.body.render() + "]]"

# Used in EventDecl and Function
@dataclass
class Param:
    name: str
    type: type

    variable: Optional[Variable] = None

    def init_param(self, scope: Scope):
        self.variable = scope.add_variable(self.name, self.type)

@dataclass
class Function(Statement):
    params: List[Param]
    body: Block
    scope: Optional[Scope] = None
    return_type: Optional[type] = None

    def init_stmt(self, scope: Scope) -> ReturnType:
        self.scope = Scope("function_params", scope)
        # Reserve space for arguments on stack
        for p in self.params:
            p.init_param(self.scope)
        self.return_type = self.body.init_stmt(self.scope).type

        # Execution of function declaration doesn't do anything
        return ReturnType(False)

    def exec(self, ctx: EvalContext) -> Return:
        # Execution of function declaration doesn't do anything
        return Return(False)

    def __call__(self, ctx: EvalContext, *params) -> Any:
        ctx.memory.grow_stack(self.scope)
        # Copy arguments to stack
        for val, p in zip(params, self.params):
            p.variable.store(ctx, val)
        ret = self.body.exec(ctx)
        ctx.memory.shrink_stack()
        return ret.val

    def render(self) -> str:
        return "" # todo
