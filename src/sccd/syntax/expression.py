from abc import *
from typing import *
from dataclasses import *
from sccd.util.duration import *
from sccd.syntax.scope import *

# Thrown if the type checker encountered something illegal.
# Not to be confused with Python's TypeError exception.
class StaticTypeError(ModelError):
    pass

class Expression(ABC):
    # Must be called exactly once on each expression, before any call to eval is made.
    # Determines the static type of the expression. May throw if there is a type error.
    # Returns static type of expression.
    @abstractmethod
    def init_rvalue(self, scope: Scope) -> SCCDType:
        pass

    # Evaluation should NOT have side effects.
    # Motivation is that the evaluation of a guard condition cannot have side effects.
    @abstractmethod
    def eval(self, ctx: EvalContext):
        pass

# The LValue type is any type that can serve as an expression OR an LValue (left hand of assignment)
# Either 'init_rvalue' or 'init_lvalue' is called to initialize the LValue.
# Then either 'eval' or 'eval_lvalue' can be called any number of times.
class LValue(Expression):
    # Initialize the LValue as an LValue. 
    @abstractmethod
    def init_lvalue(self, scope: Scope, expected_type: SCCDType):
        pass

    @abstractmethod
    def eval_lvalue(self, ctx: EvalContext) -> Variable:
        pass

    # LValues can also serve as expressions!
    def eval(self, ctx: EvalContext):
        variable = self.eval_lvalue(ctx)
        return variable.load(ctx)

@dataclass
class Identifier(LValue):
    name: str
    variable: Optional[Variable] = None

    def init_rvalue(self, scope: Scope) -> SCCDType:
        # assert self.variable is None
        self.variable = scope.get(self.name)
        # print("init rvalue", self.name, "as", self.variable)
        return self.variable.type

    def init_lvalue(self, scope: Scope, expected_type):
        # assert self.variable is None
        self.variable = scope.put_variable_assignment(self.name, expected_type)
        # print("init lvalue", self.name, "as", self.variable)

    def eval_lvalue(self, ctx: EvalContext) -> Variable:
        return self.variable

    def render(self):
        return self.name

@dataclass
class FunctionCall(Expression):
    function: Expression
    params: List[Expression]

    type: Optional[type] = None

    def init_rvalue(self, scope: Scope) -> SCCDType:
        function_type = self.function.init_rvalue(scope)
        if not isinstance(function_type, SCCDFunction):
            raise StaticTypeError("Function call: Expression '%s' is not a function" % self.function.render())

        formal_types = function_type.param_types
        return_type = function_type.return_type

        # We always secretly pass an EvalContext object with every function call
        # Not visible to the user.
        # assert formal_types[0] == EvalContext

        actual_types = [p.init_rvalue(scope) for p in self.params]
        for i, (formal, actual) in enumerate(zip(formal_types, actual_types)):
            if formal != actual:
                raise StaticTypeError("Function call, argument %d: %s is not expected type %s, instead is %s" % (i, self.params[i].render(), str(formal), str(actual)))
        return return_type

    def eval(self, ctx: EvalContext):
        f = self.function.eval(ctx)
        p = [p.eval(ctx) for p in self.params]
        return f(ctx, *p)

    def render(self):
        return self.function.render()+'('+','.join([p.render() for p in self.params])+')'

# Used in EventDecl and FunctionDeclaration
@dataclass
class ParamDecl:
    name: str
    type: type

    variable: Optional[Variable] = None

    def init_param(self, scope: Scope):
        self.variable = scope.add_variable(self.name, self.type)

@dataclass
class FunctionDeclaration(Expression):
    params_decl: List[ParamDecl]
    body: 'Statement'
    scope: Optional[Scope] = None

    def init_rvalue(self, scope: Scope) -> SCCDType:
        self.scope = Scope("function", scope)
        # Reserve space for arguments on stack
        for p in self.params_decl:
            p.init_param(self.scope)
        ret = self.body.init_stmt(self.scope)
        return_type = ret.get_return_type()
        return SCCDFunction([p.type for p in self.params_decl], return_type)

    def eval(self, ctx: EvalContext):
        def FUNCTION(ctx: EvalContext, *params):
            ctx.memory.push_local_scope(self.scope)
            # Copy arguments to stack
            for val, p in zip(params, self.params_decl):
                p.variable.store(ctx, val)
            ret = self.body.exec(ctx)
            ctx.memory.pop_local_scope(self.scope)
            return ret.val
        return FUNCTION

    def render(self) -> str:
        return "" # todo
        

@dataclass
class StringLiteral(Expression):
    string: str

    def init_rvalue(self, scope: Scope) -> SCCDType:
        return SCCDString

    def eval(self, ctx: EvalContext):
        return self.string

    def render(self):
        return '"'+self.string+'"'


@dataclass
class IntLiteral(Expression):
    i: int 

    def init_rvalue(self, scope: Scope) -> SCCDType:
        return SCCDInt

    def eval(self, ctx: EvalContext):
        return self.i

    def render(self):
        return str(self.i)

@dataclass
class BoolLiteral(Expression):
    b: bool 

    def init_rvalue(self, scope: Scope) -> SCCDType:
        return SCCDBool

    def eval(self, ctx: EvalContext):
        return self.b

    def render(self):
        return "true" if self.b else "false"

@dataclass
class DurationLiteral(Expression):
    d: Duration

    def init_rvalue(self, scope: Scope) -> SCCDType:
        return SCCDDuration

    def eval(self, ctx: EvalContext):
        return self.d

    def render(self):
        return str(self.d)

@dataclass
class Array(Expression):
    elements: List[Any]

    element_type: Optional[SCCDType] = None

    def init_rvalue(self, scope: Scope) -> SCCDType:
        for e in self.elements:
            t = e.init_rvalue(scope)
            if self.element_type and self.element_type != t:
                raise StaticTypeError("Mixed element types in Array expression: %s and %s" % (str(self.element_type), str(t)))
            self.element_type = t

        return SCCDArray(self.element_type)

    def eval(self, ctx: EvalContext):
        return [e.eval(ctx) for e in self.elements]

    def render(self):
        return '['+','.join([e.render() for e in self.elements])+']'

# Does not add anything semantically, but ensures that when rendering an expression,
# the parenthesis are not lost
@dataclass
class Group(Expression):
    subexpr: Expression

    def init_rvalue(self, scope: Scope) -> SCCDType:
        return self.subexpr.init_rvalue(scope)

    def eval(self, ctx: EvalContext):
        return self.subexpr.eval(ctx)

    def render(self):
        return '('+self.subexpr.render()+')'

@dataclass
class BinaryExpression(Expression):
    lhs: Expression
    operator: str # token name from the grammar.
    rhs: Expression

    def init_rvalue(self, scope: Scope) -> SCCDType:
        lhs_t = self.lhs.init_rvalue(scope)
        rhs_t = self.rhs.init_rvalue(scope)

        def comparison_type():
            same_type()
            return SCCDBool

        def same_type():
            if lhs_t != rhs_t:
                raise StaticTypeError("Mixed LHS and RHS types in '%s' expression: %s and %s" % (self.operator, str(lhs_t), str(rhs_t)))
            return lhs_t

        def mult_type():
            if lhs_t == rhs_t:
                if lhs_t == Duration:
                    raise StaticTypeError("Cannot multiply 'Duration' and 'Duration'")
                return lhs_t
            key = lambda x: {SCCDInt: 1, SCCDFloat: 2, SCCDDuration: 3}[x]
            [smallest_type, largest_type] = sorted([lhs_t, rhs_t], key=key)
            if largest_type == SCCDDuration and smallest_type == SCCDFloat:
                raise StaticTypeError("Cannot multiply 'float' and 'Duration'")
            return largest_type

        return {
            "and": SCCDBool,
            "or":  SCCDBool,
            "==":  comparison_type(),
            "!=":  comparison_type(),
            ">":   comparison_type(),
            ">=":  comparison_type(),
            "<":   comparison_type(),
            "<=":  comparison_type(),
            "+":   same_type(),
            "-":   same_type(),
            "*":   mult_type(),
            "/":   SCCDFloat,
            "//":  same_type(),
            "%":   same_type(),
            "**":  same_type(),
        }[self.operator]

    def eval(self, ctx: EvalContext):
        
        return {
            "and": lambda x,y: x.eval(ctx) and y.eval(ctx),
            "or": lambda x,y: x.eval(ctx) or y.eval(ctx),
            "==": lambda x,y: x.eval(ctx) == y.eval(ctx),
            "!=": lambda x,y: x.eval(ctx) != y.eval(ctx),
            ">": lambda x,y: x.eval(ctx) > y.eval(ctx),
            ">=": lambda x,y: x.eval(ctx) >= y.eval(ctx),
            "<": lambda x,y: x.eval(ctx) < y.eval(ctx),
            "<=": lambda x,y: x.eval(ctx) <= y.eval(ctx),
            "+": lambda x,y: x.eval(ctx) + y.eval(ctx),
            "-": lambda x,y: x.eval(ctx) - y.eval(ctx),
            "*": lambda x,y: x.eval(ctx) * y.eval(ctx),
            "/": lambda x,y: x.eval(ctx) / y.eval(ctx),
            "//": lambda x,y: x.eval(ctx) // y.eval(ctx),
            "%": lambda x,y: x.eval(ctx) % y.eval(ctx),
            "**": lambda x,y: x.eval(ctx) ** y.eval(ctx),
        }[self.operator](self.lhs, self.rhs) # Borrow Python's lazy evaluation

    def render(self):
        return self.lhs.render() + ' ' + self.operator + ' ' + self.rhs.render()

@dataclass
class UnaryExpression(Expression):
    operator: str # token value from the grammar.
    expr: Expression

    def init_rvalue(self, scope: Scope) -> SCCDType:
        expr_type = self.expr.init_rvalue(scope)
        return {
            "not": SCCDBool,
            "-":   expr_type,
        }[self.operator]

    def eval(self, ctx: EvalContext):
        return {
            "not": lambda x: not x.eval(ctx),
            "-": lambda x: - x.eval(ctx),
        }[self.operator](self.expr)

    def render(self):
        return self.operator + ' ' + self.expr.render()
