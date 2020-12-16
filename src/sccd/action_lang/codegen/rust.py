from sccd.action_lang.static.statement import *
from collections import defaultdict

class UnsupportedFeature(Exception):
    pass

def ident_scope_type(scope):
    return "Scope_%s" % (scope.name)

def ident_scope_constructor(scope):
    return "new_" + ident_scope_type(scope)

@dataclass(frozen=True)
class ScopeCommit:
    type_name: str
    supertype_name: str
    start: int
    end: int

@dataclass
class ScopeStackEntry:
    scope: Scope
    committed: int = 0

class ScopeHelper():
    def __init__(self):
        self.scope_stack = []
        self.scope_structs = defaultdict(dict)
        self.scope_names = {}

    def root(self):
        return self.scope_stack[0].scope

    def push(self, scope):
        self.scope_stack.append( ScopeStackEntry(scope) )

    def pop(self):
        self.scope_stack.pop()

    def current(self):
        return self.scope_stack[-1]

    def basename(self, scope):
        return self.scope_names.setdefault(scope, "Scope%d_%s" % (len(self.scope_names), scope.name))
    
    def type(self, scope, end):
        if end == 0:
            return "Empty"
        else:
            return self.basename(scope) + "_l" + str(end)

    def commit(self, offset, writer):
        start = self.current().committed
        end = offset
        type_name = self.type(self.current().scope, end)

        if start != end  and  end > 0:
            if start == 0:
                supertype_name = "Empty"
            else:
                supertype_name = self.scope_structs[self.current().scope][start].type_name

            commit = ScopeCommit(type_name, supertype_name, start, end)
            self.scope_structs[self.current().scope][end] = commit

            writer.writeln("let mut scope = %s {" % type_name)
            writer.writeln("  _base: scope,")
            for v in self.current().scope.variables[start:end]:
                writer.writeln("  %s," % v.name)
            writer.writeln("};")

        self.current().committed = end
        return type_name

class ActionLangRustGenerator(Visitor):
    def __init__(self, w):
        self.w = w
        self.scope = ScopeHelper()
        self.functions_to_write = [] # Function and Rust identifier

        self.function_types = {} # maps Function to Rust type

    def default(self, what):
        self.w.wno("<%s>" % what)
        # raise UnsupportedFeature(what)

    def debug_print_stack(self):
        # Print Python stack in Rust file as a comment
        import traceback
        for line in ''.join(traceback.format_stack()).split('\n'):
            self.w.writeln("// "+line)

    def write_parent_params(self, scope, with_identifiers=True):
        ctr = 1
        while scope is not self.scope.root():
            if ctr > scope.deepest_lookup:
                break
            if with_identifiers:
                self.w.wno("parent%d: " % ctr)
            self.w.wno("&mut %s, " % self.scope.type(scope.parent, scope.parent_offset))
            ctr += 1
            scope = scope.parent

    def write_parent_call_params(self, scope, skip=0):
        ctr = 0
        while scope is not self.scope.root():
            if ctr == skip:
                break
            ctr += 1
            scope = scope.parent

        while scope is not self.scope.root():
            if ctr > scope.deepest_lookup:
                break
            if ctr == skip:
                self.w.wno("&mut scope, ")
            else:
                self.w.wno("&mut parent%d, " % ctr-skip)
            ctr += 1
            scope = scope.parent

    # This is not a visit method because Scopes may be encountered whenever there's a function call, but they are written as structs and constructor functions, which can only be written at the module level.
    # When compiling Rust code, the Visitable.accept method must be called on the root of the AST, to write code wherever desired (e.g. in a main-function) followed by 'write_scope' at the module level.
    def write_decls(self):

        function_types = {}

        # Write functions
        for function, identifier in self.functions_to_write:
            scope = function.scope
            # self.w.write("fn %s(parent_scope: &mut %s, " % (identifier, self.scope.type(scope.parent, scope.parent_offset)))
            self.w.write("fn %s(" % (identifier))

            self.write_parent_params(scope)

            for p in function.params_decl:
                p.accept(self)

            # self.w.wno(") -> (%s," % self.scope.type(scope, scope.size()))
            self.w.wno(") -> ")
            self.write_return_type(function)
            self.w.wnoln(" {")
            self.w.indent()
            self.w.writeln("let scope = Empty{};")

            self.scope.push(function.scope)
            # Parameters are part of function's scope
            self.scope.commit(len(function.params_decl), self.w)
            function.body.accept(self)
            self.scope.pop()

            self.w.dedent()
            self.w.writeln("}")
            self.w.writeln()

        # Write function scopes (as structs)
        for scope, structs in self.scope.scope_structs.items():
            for end, commit in structs.items():
                self.w.writeln("inherit_struct! {")
                self.w.indent()
                self.w.writeln("%s (%s) {" % (commit.type_name, commit.supertype_name))
                for v in scope.variables[commit.start: commit.end]:
                    self.w.write("  %s: " % v.name)
                    v.type.accept(self)
                    self.w.wnoln(", ")
                self.w.writeln("}")
                self.w.dedent()
                self.w.writeln("}")
                self.w.writeln()

    def visit_Block(self, stmt):
        for s in stmt.stmts:
            s.accept(self)

    def visit_Assignment(self, stmt):
        #self.w.write('') # indent
        stmt.lhs.accept(self)
        self.w.wno(" = ")
        stmt.rhs.accept(self)
        self.w.wnoln(";")
        self.w.writeln("eprintln!(\"%s\");" % termcolor.colored(stmt.render(),'blue'))

    def visit_IfStatement(self, stmt):
        self.w.write("if ")
        stmt.cond.accept(self)
        self.w.wnoln(" {")
        self.w.indent()
        stmt.if_body.accept(self)
        self.w.dedent()
        self.w.writeln("}")
        if stmt.else_body is not None:
            self.w.writeln("else {")
            self.w.indent()
            stmt.else_body.accept(self)
            self.w.dedent()
            self.w.writeln("}")

    def visit_ReturnStatement(self, stmt):
        self.w.write("return ")

        return_type = stmt.expr.get_type()
        returns_closure_obj = (
            isinstance(return_type, SCCDFunction) and
            return_type.function.scope.parent is stmt.scope
        )

        # self.w.write("return (scope, ")
        if returns_closure_obj:
            self.w.wno("(scope, ")
        stmt.expr.accept(self)
        # self.w.wnoln(");")
        if returns_closure_obj:
            self.w.wno(")")

        self.w.wnoln(";")

    def visit_ExpressionStatement(self, stmt):
        self.w.write('')
        stmt.expr.accept(self)
        self.w.wnoln(";")

    def visit_BoolLiteral(self, expr):
        self.w.wno("true" if expr.b else "false")

    def visit_IntLiteral(self, expr):
        self.w.wno(str(expr.i))

    def visit_StringLiteral(self, expr):
        self.w.wno('"'+expr.string+'"')

    def visit_Array(self, expr):
        self.w.wno("[")
        for el in expr.elements:
            el.accept(self)
            self.w.wno(", ")
        self.w.wno("]")

    def visit_BinaryExpression(self, expr):
        if expr.operator == "**":
            raise UnsupportedFeature("exponent operator")
        else:
            # always put parentheses
            self.w.wno("(")
            expr.lhs.accept(self)
            self.w.wno(" %s " % expr.operator
                .replace('and', '&&')
                .replace('or', '||')
                .replace('//', '/')) # integer division
            expr.rhs.accept(self)
            self.w.wno(")")

    def visit_UnaryExpression(self, expr):
        self.w.wno(expr.operator
            .replace('not', '! '))
        expr.expr.accept(self)

    def visit_Group(self, expr):
        # self.w.wno(" (")
        expr.subexpr.accept(self)
        # self.w.wno(") ")

    def visit_ParamDecl(self, expr):
        self.w.wno(expr.name)
        self.w.wno(": ")
        expr.formal_type.accept(self)

    def visit_FunctionDeclaration(self, expr):
        function_identifier = "f%d_%s" % (len(self.functions_to_write), expr.scope.name)
        self.functions_to_write.append( (expr, function_identifier) )
        self.w.wno(function_identifier)

    def visit_FunctionCall(self, expr):
        if isinstance(expr.function.get_type(), SCCDClosureObject):
            self.w.wno("call_closure!(")
            expr.function.accept(self) # an Identifier or a FunctionDeclaration (=anonymous function)
            self.w.wno(", ")

            self.write_parent_call_params(expr.function_being_called.scope, skip=1)
        else:
            self.w.wno("(")
            expr.function.accept(self) # an Identifier or a FunctionDeclaration (=anonymous function)
            self.w.wno(")(")

            # Parent scope mut refs
            self.write_parent_call_params(expr.function_being_called.scope, skip=1)

        # Call parameters
        for p in expr.params:
            p.accept(self)
            self.w.wno(", ")
        self.w.wno(")")

        # if not isinstance(expr.get_type(), SCCDClosureObject):
        #     # In our generated code, a function always returns a pair of
        #     #   0) the called function's scope
        #     #   1) the returned value <- pick this
        #     self.w.wno(".1")


    def visit_Identifier(self, lval):

        if lval.is_lvalue:
            # self.debug_print_stack()
            # self.w.writeln("// offset: %d, branches: %s" % (lval.offset, self.scope.current().scope.children.keys()))
            if lval.offset in self.scope.current().scope.children:
                # a child scope exists at the current offset (typically because we encountered a function declaration) - so we must commit our scope
                self.scope.commit(lval.offset, self.w)

            self.w.write('') # indent

        if lval.is_init:
            self.w.wno("let mut ")
        else:
            if lval.offset < 0:
                self.w.wno("parent%d." % self.scope.current().scope.nested_levels(lval.offset))
            elif lval.offset < self.scope.current().committed:
                self.w.wno("scope.")

        self.w.wno(lval.name)

    def visit_SCCDClosureObject(self, type):
        # self.w.wno("<closure type> ")

        self.w.wno("(%s, " % self.scope.type(type.scope, type.scope.parent_offset))
        type.function_type.accept(self)
        self.w.wno(")")

    def write_return_type(self, function: FunctionDeclaration):
        # self.w.wno("(%s, " % self.scope.type(function.scope, function.scope.size()))
        # type.function_type.accept(self)
        if function.return_type is None:
            self.w.wno("Empty")
        else:
            function.return_type.accept(self)
        # self.w.wno(")")

    def visit_SCCDFunction(self, type):
        # self.w.wno("<function type> ")
        scope = type.function.scope
        # self.w.wno("fn(&mut %s, " % (self.scope.type(scope.parent, scope.parent_offset)))
        self.w.wno("fn(")

        self.write_parent_params(scope, with_identifiers=False)

        for p in type.param_types:
            p.accept(self)
            self.w.wno(", ")

        self.w.wno(") -> ")
        self.write_return_type(type.function)

    def visit__SCCDSimpleType(self, type):
        self.w.wno(type.name
            .replace("int", "i32")
            .replace("float", "f64"))
