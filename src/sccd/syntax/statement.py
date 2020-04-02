from typing import *
from sccd.syntax.expression import *

@dataclass
class Return:
    ret: bool
    val: Any = None

@dataclass(frozen=True)
class ReturnBehavior:

    class When(Enum):
        ALWAYS = auto()
        SOME_BRANCHES = auto()
        NEVER = auto()

    when: When
    type: Optional[type] = None

    def __post_init__(self):
        assert (self.when == ReturnBehavior.When.NEVER) == (self.type is None)

    # Check if two branches have combinable ReturnBehaviors and if so, combine them.
    @staticmethod
    def combine_branches(one: 'ReturnBehavior', two: 'ReturnBehavior') -> 'ReturnBehavior':
        if one == two:
            # Whether ALWAYS/SOME_BRANCHES/NEVER, when both branches
            # have the same 'when' and the same type, the combination
            # is valid and has that type too :)
            return one
        if one.when == ReturnBehavior.When.NEVER:
            # two will not be NEVER
            return ReturnBehavior(ReturnBehavior.When.SOME_BRANCHES, two.type)
        if two.when == ReturnBehavior.When.NEVER:
            # one will not be NEVER
            return ReturnBehavior(ReturnBehavior.When.SOME_BRANCHES, one.type)
        # Only remaining case: ALWAYS & SOME_BRANCHES.
        # Now the types must match:
        if one.type != two.type:
            raise StaticTypeError("Return types differ: One branch returns %s, the other %s" % (str(one.type), str(two.type)))
        return ReturnBehavior(ReturnBehavior.When.SOME_BRANCHES, one.type)

    # If a statement with known ReturnBehavior is followed by another statement with known ReturnBehavior, what is the ReturnBehavior of their sequence? Also, raises if their sequence is illegal.
    @staticmethod
    def sequence(earlier: 'ReturnBehavior', later: 'ReturnBehavior') -> 'ReturnBehavior':
        if earlier.when == ReturnBehavior.When.NEVER:
            return later
        if earlier.when == ReturnBehavior.When.SOME_BRANCHES:
            if later.when == ReturnBehavior.When.NEVER:
                return earlier
            if later.when == ReturnBehavior.When.SOME_BRANCHES:
                if earlier.type != later.type:
                    raise StaticTypeError("Return types differ: Earlier statement may return %s, later statement may return %s" % (str(earlier.type), str(later.type)))
                return earlier
            if earlier.type != later.type:
                raise StaticTypeError("Return types differ: Earlier statement may return %s, later statement returns %s" % (str(earlier.type), str(later.type)))
            return later
        raise StaticTypeError("Earlier statement always returns %s, cannot be followed by another statement" % str(earlier.type))

# A statement is NOT an expression.
class Statement(ABC):
    # Execution typically has side effects.
    @abstractmethod
    def exec(self, ctx: EvalContext) -> Return:
        pass

    @abstractmethod
    def init_stmt(self, scope: Scope) -> ReturnBehavior:
        pass

    @abstractmethod
    def render(self) -> str:
        pass

@dataclass
class Assignment(Statement):
    lhs: LValue
    operator: str # token value from the grammar.
    rhs: Expression

    def init_stmt(self, scope: Scope) -> ReturnBehavior:
        rhs_t = self.rhs.init_rvalue(scope)
        self.lhs.init_lvalue(scope, rhs_t)
        return ReturnBehavior(ReturnBehavior.When.NEVER)

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

    def init_stmt(self, scope: Scope) -> ReturnBehavior:
        self.scope = Scope("local", scope)
        earlier = ReturnBehavior(ReturnBehavior.When.NEVER)
        for i, stmt in enumerate(self.stmts):
            later = stmt.init_stmt(self.scope)
            earlier = ReturnBehavior.sequence(earlier, later)
        return earlier

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

    def init_stmt(self, scope: Scope) -> ReturnBehavior:
        self.expr.init_rvalue(scope)
        return ReturnBehavior(ReturnBehavior.When.NEVER)

    def exec(self, ctx: EvalContext) -> Return:
        self.expr.eval(ctx)
        return Return(False)

    def render(self) -> str:
        return self.expr.render()

@dataclass
class ReturnStatement(Statement):
    expr: Expression

    def init_stmt(self, scope: Scope) -> ReturnBehavior:
        t = self.expr.init_rvalue(scope)
        return ReturnBehavior(ReturnBehavior.When.ALWAYS, t)

    def exec(self, ctx: EvalContext) -> Return:
        val = self.expr.eval(ctx)
        return Return(True, val)

    def render(self) -> str:
        return "return " + self.expr.render()

@dataclass
class IfStatement(Statement):
    cond: Expression
    if_body: Statement
    else_body: Optional[Statement] = None

    def init_stmt(self, scope: Scope) -> ReturnBehavior:
        cond_t = self.cond.init_rvalue(scope)
        if_ret = self.if_body.init_stmt(scope)
        if self.else_body is None:
            else_ret = ReturnBehavior(ReturnBehavior.When.NEVER)
        else:
            else_ret = self.else_body.init_stmt(scope)
        return ReturnBehavior.combine_branches(if_ret, else_ret)

    def exec(self, ctx: EvalContext) -> Return:
        val = self.cond.eval(ctx)
        if val:
            return self.if_body.exec(ctx)
        return Return(False)

    def render(self) -> str:
        return "if (%s) [[" % self.cond.render() + self.if_body.render() + "]]"

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

    def init_stmt(self, scope: Scope) -> ReturnBehavior:
        self.scope = Scope("function_params", scope)
        # Reserve space for arguments on stack
        for p in self.params:
            p.init_param(self.scope)
        ret = self.body.init_stmt(self.scope)
        if ret.when == ReturnBehavior.When.ALWAYS:
            self.return_type = ret.type
        elif ret.when == ReturnBehavior.When.SOME_BRANCHES:
            raise StaticTypeError("Cannot statically infer function return type: Some branches return %s, others return nothing." % str(ret.type))

        # Execution of function declaration doesn't return (or do) anything
        return ReturnBehavior(ReturnBehavior.When.NEVER)

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
