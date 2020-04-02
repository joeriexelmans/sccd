from typing import *
from sccd.syntax.expression import *

@dataclass
class Return:
    ret: bool
    val: Any = None

@dataclass
class ReturnType:

    class When(Enum):
        ALWAYS = auto()
        SOME_BRANCHES = auto()
        NEVER = auto()

    when: When
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
        return ReturnType(ReturnType.When.NEVER)

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
        earlier_return_type = ReturnType(ReturnType.When.NEVER)
        for i, stmt in enumerate(self.stmts):
            ret = stmt.init_stmt(self.scope)
            if ret.when == ReturnType.When.ALWAYS:
                if earlier_return_type.when == ReturnType.When.SOME_BRANCHES:
                    if earlier_return_type.type != ret.type:
                        raise Exception("Not all branches have same return type: %s and %s" % (str(ret.type), str(earlier_return_type.type)))
                # A return statement is encountered, don't init the rest of the statements since they are unreachable
                if i < len(self.stmts)-1:
                    print_debug("Warning: statements after return statement ignored.")
                return ret
            elif ret.when == ReturnType.When.SOME_BRANCHES:
                if earlier_return_type.when == ReturnType.When.SOME_BRANCHES:
                    if earlier_return_type.type != ret.type:
                        raise Exception("Not all branches have same return type: %s and %s" % (str(ret.type), str(earlier_return_type.type)))
                earlier_return_type = ret

        return earlier_return_type

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
        return ReturnType(ReturnType.When.NEVER)

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
        return ReturnType(ReturnType.When.ALWAYS, t)

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
        if ret.when == ReturnType.When.NEVER:
            return ReturnType(ReturnType.When.NEVER)
        else:
            return ReturnType(ReturnType.When.SOME_BRANCHES, ret.type)

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
        ret = self.body.init_stmt(self.scope)
        if ret.when == ReturnType.When.ALWAYS:
            self.return_type = ret.type
        elif ret.when == ReturnType.When.SOME_BRANCHES:
            raise Exception("Cannot statically infer function return type: Some branches return %s, others return nothing." % str(ret.type))

        # Execution of function declaration doesn't return (or do) anything
        return ReturnType(ReturnType.When.NEVER)

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
