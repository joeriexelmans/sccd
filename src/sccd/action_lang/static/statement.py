from typing import *
from sccd.action_lang.static.expression import *
from sccd.util.debug import *

@dataclass(frozen=True)
class Return:
    ret: bool
    val: Any = None

    def __post_init__(self):
        assert self.ret == (self.val is not None)

DontReturn = Return(False)
DoReturn = lambda v: Return(True, v)

@dataclass(frozen=True)
class ReturnBehavior:

    class When(Enum):
        ALWAYS = auto()
        SOME_BRANCHES = auto()
        NEVER = auto()

    when: When
    type: Optional[SCCDType] = None

    def __post_init__(self):
        assert (self.when == ReturnBehavior.When.NEVER) == (self.type is None)

    def get_return_type(self) -> type:
        if self.when == ReturnBehavior.When.ALWAYS:
            return self.type
        elif self.when == ReturnBehavior.When.SOME_BRANCHES:
            raise StaticTypeError("Cannot statically infer return type: Some branches return %s, others return nothing." % str(self.type))

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

NeverReturns = ReturnBehavior(ReturnBehavior.When.NEVER)
AlwaysReturns = lambda t: ReturnBehavior(ReturnBehavior.When.ALWAYS, t)

# A statement is NOT an expression.
class Statement(ABC):
    # Run static analysis on the statement.
    # Looks up identifiers in the given scope, and adds new identifiers to the scope.
    @abstractmethod
    def init_stmt(self, scope: Scope) -> ReturnBehavior:
        pass

    # Execute the statement.
    # Execution typically has side effects.
    @abstractmethod
    def exec(self, memory: MemoryInterface) -> Return:
        pass

    @abstractmethod
    def render(self) -> str:
        pass

@dataclass
class Assignment(Statement):
    lhs: LValue
    rhs: Expression

    def init_stmt(self, scope: Scope) -> ReturnBehavior:
        rhs_t = self.rhs.init_expr(scope)
        self.lhs.init_lvalue(scope, rhs_t)
        return NeverReturns

    def exec(self, memory: MemoryInterface) -> Return:
        rhs_val = self.rhs.eval(memory)
        offset = self.lhs.eval_lvalue()

        memory.store(offset, rhs_val)

        return DontReturn

    def render(self) -> str:
        return self.lhs.render() + ' = ' + self.rhs.render() + ';'



@dataclass
class Block(Statement):
    stmts: List[Statement]

    def init_stmt(self, scope: Scope) -> ReturnBehavior:
        so_far = NeverReturns
        for i, stmt in enumerate(self.stmts):
            now_what = stmt.init_stmt(scope)
            so_far = ReturnBehavior.sequence(so_far, now_what)            
        return so_far

    def exec(self, memory: MemoryInterface) -> Return:
        ret = DontReturn
        for stmt in self.stmts:
            if DEBUG:
                print("    "+termcolor.colored(stmt.render(), 'grey'))
            ret = stmt.exec(memory)
            if ret.ret:
                break
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
        self.expr.init_expr(scope)
        return NeverReturns

    def exec(self, memory: MemoryInterface) -> Return:
        self.expr.eval(memory)
        return DontReturn

    def render(self) -> str:
        return self.expr.render()

@dataclass
class ReturnStatement(Statement):
    expr: Expression

    def init_stmt(self, scope: Scope) -> ReturnBehavior:
        t = self.expr.init_expr(scope)
        if t is None:
            raise StaticTypeError("Return statement: Expression does not evaluate to a value.")
        return AlwaysReturns(t)

    def exec(self, memory: MemoryInterface) -> Return:
        val = self.expr.eval(memory)
        return DoReturn(val)

    def render(self) -> str:
        return "return " + self.expr.render() + ";"

@dataclass
class IfStatement(Statement):
    cond: Expression
    if_body: Statement
    else_body: Optional[Statement] = None

    def init_stmt(self, scope: Scope) -> ReturnBehavior:
        cond_t = self.cond.init_expr(scope)
        if_ret = self.if_body.init_stmt(scope)
        if self.else_body is None:
            else_ret = NeverReturns
        else:
            else_ret = self.else_body.init_stmt(scope)
        return ReturnBehavior.combine_branches(if_ret, else_ret)

    def exec(self, memory: MemoryInterface) -> Return:
        val = self.cond.eval(memory)
        if val:
            return self.if_body.exec(memory)
        elif self.else_body is not None:
            return self.else_body.exec(memory)
        return DontReturn

    def render(self) -> str:
        return "if (%s) [[" % self.cond.render() + self.if_body.render() + "]]"


@dataclass
class ImportStatement(Statement):
    module_name: str

    # Offsets and values of imported stuff
    declarations: Optional[List[Tuple[int, Any]]] = None

    def init_stmt(self, scope: Scope) -> ReturnBehavior:
        import importlib
        self.module = importlib.import_module(self.module_name)
        self.declarations = []
        for name, (value, type) in self.module.SCCD_EXPORTS.items():
            offset = scope.declare(name, type, const=True)
            if isinstance(type, SCCDFunction):
                # Function values are a bit special, in the action language they are secretly passed a MemoryInterface object as first parameter, followed by the other (visible) parameters.
                # I don't really like this solution, but it works for now.
                def make_wrapper(func):
                    def wrapper(memory: MemoryInterface, *params):
                        return func(*params)
                    return wrapper
                self.declarations.append((offset, make_wrapper(value)))
            else:
                self.declarations.append((offset, value))
        return NeverReturns

    def exec(self, memory: MemoryInterface) -> Return:
        for offset, value in self.declarations:
            memory.store(offset, value)
        return DontReturn

    def render(self) -> str:
        return "import " + self.module_name + ";"
