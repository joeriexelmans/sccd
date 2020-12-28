from sccd.action_lang.static.statement import *
from collections import defaultdict

class UnsupportedFeature(Exception):
    pass

def ident_scope_type(scope):
    return "Scope_%s" % (scope.name)

def ident_scope_constructor(scope):
    return "new_" + ident_scope_type(scope)

def ident_local(name):
    if name[0] == '@':
        return "builtin_" + name[1:]
    else:
        return "local_" + name

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
            return "action_lang::Empty"
        else:
            return self.basename(scope) + "_l" + str(end)

    def commit(self, offset, writer):
        start = self.current().committed
        end = offset
        type_name = self.type(self.current().scope, end)

        if start != end  and  end > 0:
            if start == 0:
                supertype_name = "action_lang::Empty"
            else:
                supertype_name = self.scope_structs[self.current().scope][start].type_name

            commit = ScopeCommit(type_name, supertype_name, start, end)
            self.scope_structs[self.current().scope][end] = commit

            writer.writeln("let mut scope = %s {" % type_name)
            writer.writeln("  _base: scope,")
            for v in self.current().scope.variables[start:end]:
                writer.writeln("  %s," % ident_local(v.name))
            writer.writeln("};")

        self.current().committed = end
        return type_name

    def write_rvalue(self, name, offset, writer):
        if offset < 0:
            writer.write("parent%d." % self.current().scope.nested_levels(offset))
            writer.write(ident_local(name))
        elif offset < self.current().committed:
            writer.write("scope.")
            writer.write(ident_local(name))
        else:
            writer.write(ident_local(name))


class ActionLangRustGenerator(Visitor):
    def __init__(self, w):
        self.w = w
        self.scope = ScopeHelper()
        self.functions_to_write = [] # Function and Rust identifier

    def default(self, what):
        # self.w.write("<%s>" % what)
        raise UnsupportedFeature(what)

    def debug_print_stack(self):
        # Print Python stack in Rust file as a comment
        import traceback
        for line in ''.join(traceback.format_stack()).split('\n'):
            self.w.writeln("// "+line)

    def write_parent_params(self, scope, with_identifiers=True):
        args = []
        ctr = 1
        while scope is not self.scope.root() and scope.deepest_lookup > 0:
            arg = ""
            if with_identifiers:
                arg += "parent%d: " % ctr
            arg += "&mut %s" % self.scope.type(scope.parent, scope.parent_offset)
            args.append(arg)
            ctr += 1
            scope = scope.parent

        self.w.write(", ".join(reversed(args)))

    def write_parent_call_params(self, scope, skip: int = 0):
        args = []
        ctr = 0
        while scope is not self.scope.root() and scope.deepest_lookup > 0:
            if ctr == skip:
                # args.append("&mut scope")
                args.append("&mut scope")
            elif ctr > skip:
                args.append("parent%d" % (ctr-skip))
            ctr += 1
            scope = scope.parent

        self.w.write(", ".join(reversed(args)))

    # This is not a visit method because Scopes may be encountered whenever there's a function call, but they are written as structs and constructor functions, which can only be written at the module level.
    # When compiling Rust code, the Visitable.accept method must be called on the root of the AST, to write code wherever desired (e.g. in a main-function) followed by 'write_scope' at the module level.
    def write_decls(self):

        # Write functions
        for function, identifier in self.functions_to_write:
            scope = function.scope

            self.w.write("fn %s(" % (identifier))

            for p in function.params_decl:
                p.accept(self)
                self.w.write(", ")

            self.write_parent_params(scope)

            self.w.write(") -> ")

            self.write_return_type(function)

            self.w.writeln(" {")
            self.w.indent()
            self.w.writeln("let scope = action_lang::Empty{};")

            self.scope.push(function.scope)
            
            # Parameters are part of function's scope
            self.scope.commit(len(function.params_decl), self.w)

            # Visit the body. This may cause new functions to be added to self.functions_to_write, which we are iterating over (which is allowed in Python), so those will also be dealt with in this loop.
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
                    self.w.write("  %s: " % ident_local(v.name))
                    v.type.accept(self)
                    self.w.writeln(",")
                self.w.writeln("}")
                self.w.dedent()
                self.w.writeln("}")
                self.w.writeln()

    def visit_Block(self, stmt):
        for s in stmt.stmts:
            s.accept(self)

    def visit_Assignment(self, stmt):
        stmt.lhs.accept(self)
        self.w.write(" = ")
        stmt.rhs.accept(self)
        self.w.writeln(";")
        if DEBUG:
            self.w.writeln("eprintln!(\"%s\");" % termcolor.colored(stmt.render(),'blue'))

    def visit_IfStatement(self, stmt):
        self.w.write("if ")
        stmt.cond.accept(self)
        self.w.writeln(" {")
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
        return_type = stmt.expr.get_type()
        returns_closure_obj = (
            isinstance(return_type, SCCDFunction) and
            return_type.function.scope.parent is stmt.scope
        )

        self.w.write("return ")
        if returns_closure_obj:
            self.w.write("(scope, ")
        stmt.expr.accept(self)
        if returns_closure_obj:
            self.w.write(")")
        self.w.writeln(";")

    def visit_ExpressionStatement(self, stmt):
        self.w.write('')
        stmt.expr.accept(self)
        self.w.writeln(";")

    def visit_BoolLiteral(self, expr):
        self.w.write("true" if expr.b else "false")

    def visit_IntLiteral(self, expr):
        self.w.write(str(expr.i))

    def visit_StringLiteral(self, expr):
        self.w.write('"'+expr.string+'"')

    def visit_Array(self, expr):
        self.w.write("[")
        for el in expr.elements:
            el.accept(self)
            self.w.write(", ")
        self.w.write("]")

    def visit_BinaryExpression(self, expr):
        if expr.operator == "**":
            raise UnsupportedFeature("exponent operator")
        else:
            # always put parentheses
            self.w.write("(")
            expr.lhs.accept(self)
            self.w.write(" %s " % expr.operator
                .replace('and', '&&')
                .replace('or', '||')
                .replace('//', '/')) # integer division
            expr.rhs.accept(self)
            self.w.write(")")

    def visit_UnaryExpression(self, expr):
        self.w.write(expr.operator
            .replace('not', '! '))
        expr.expr.accept(self)

    def visit_Group(self, expr):
        expr.subexpr.accept(self)

    def visit_ParamDecl(self, expr):
        self.w.write(ident_local(expr.name))
        self.w.write(": ")
        expr.formal_type.accept(self)

    def visit_FunctionDeclaration(self, expr):
        function_identifier = "f%d_%s" % (len(self.functions_to_write), expr.scope.name)
        self.functions_to_write.append( (expr, function_identifier) )
        self.w.write(function_identifier)

    def visit_FunctionCall(self, expr):
        if isinstance(expr.function.get_type(), SCCDClosureObject):
            self.w.write("call_closure!(")
            expr.function.accept(self)
            self.w.write(", ")
        else:
            self.w.write("(")
            expr.function.accept(self)
            self.w.write(")(")

        # Call parameters
        for p in expr.params:
            p.accept(self)
            self.w.write(", ")

        if isinstance(expr.function.get_type(), SCCDClosureObject):
            self.write_parent_call_params(expr.function_being_called.scope, skip=1)
        else:
            self.write_parent_call_params(expr.function_being_called.scope)

        self.w.write(")")


    def visit_Identifier(self, lval):

        if lval.is_lvalue:
            # self.debug_print_stack()
            if lval.offset in self.scope.current().scope.children:
                # a child scope exists at the current offset (typically because we encountered a function declaration) - so we must commit our scope
                self.scope.commit(lval.offset, self.w)

            self.w.write('') # indent

        if lval.is_init:
            self.w.write("let mut ")
            self.w.write(ident_local(lval.name))
        else:
            self.scope.write_rvalue(lval.name, lval.offset, self.w)

    def visit_SCCDClosureObject(self, type):
        self.w.write("(%s, " % self.scope.type(type.scope, type.scope.size()))
        type.function_type.accept(self)
        self.w.write(")")

    def write_return_type(self, function: FunctionDeclaration):
        if function.return_type is None:
            self.w.write("()")
        else:
            function.return_type.accept(self)

    def visit_SCCDFunction(self, type):
        scope = type.function.scope
        self.w.write("fn(")

        for p in type.param_types:
            p.accept(self)
            self.w.write(", ")

        self.write_parent_params(scope, with_identifiers=False)

        self.w.write(") -> ")
        self.write_return_type(type.function)

    def visit__SCCDSimpleType(self, type):
        self.w.write(type.name
            .replace("int", "i32")
            .replace("float", "f64")
            .replace("str", "&'static str")
        )
