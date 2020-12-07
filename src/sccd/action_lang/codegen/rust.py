from sccd.action_lang.static.statement import *

class UnsupportedFeature(Exception):
    pass


class ActionLangRustGenerator(Visitor):
    def __init__(self, w):
        self.w = w
        self.scopes = {}
        self.scopes_written = set()

    def default(self, what):
        raise UnsupportedFeature(what)

    def debug_print_stack(self):
        # Print Python stack in Rust file as a comment
        import traceback
        for line in ''.join(traceback.format_stack()).split('\n'):
            self.w.writeln("// "+line)


    def ident_scope(self, scope):
        return self.scopes.setdefault(scope, "Scope%d_%s" % (len(self.scopes), scope.name))

    def ident_new_scope(self, scope):
        return "new_" + self.ident_scope(scope)

    def write_scopes(self):
        def scopes_to_write():
            to_write = []
            for s in self.scopes:
                if s not in self.scopes_written:
                    to_write.append(s)
            return to_write

        while True:
            to_write = scopes_to_write()
            if len(to_write) == 0:
                return
            else:
                for scope in to_write:
                    scope.accept(self)


    def visit_Block(self, stmt):
        # self.w.writeln("{")
        for s in stmt.stmts:
            s.accept(self)
        # self.w.writeln("}")

    def visit_Assignment(self, stmt):
        if not stmt.is_initialization:
            self.w.write('') # indent
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
        stmt.expr.accept(self)
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
        self.w.wno("|")
        for i, p in enumerate(expr.params_decl):
            p.accept(self)
            if i != len(expr.params_decl)-1:
                self.w.wno(", ")
        self.w.wnoln("| {")
        self.w.indent()
        self.w.writeln("let scope = %s();" % self.ident_new_scope(expr.scope))
        expr.body.accept(self)
        self.w.dedent()
        self.w.write("}")

    def visit_FunctionCall(self, expr):
        self.w.wno("(")
        expr.function.accept(self)
        self.w.wno(")(")
        for p in expr.params:
            p.accept(self)
            self.w.wno(", ")
        self.w.wno(")")

    def visit_Identifier(self, lval):
        self.w.wno("scope."+lval.name)

    def visit_Scope(self, scope):
        # Map variable to template param name (for functions)
        mapping = {}
        for i,v in enumerate(scope.variables):
            if isinstance(v.type, SCCDFunction):
                mapping[i] = "F%d" % len(mapping)

        def write_template_params_with_trait():
            for i,v in enumerate(scope.variables):
                if i in mapping:
                    self.w.wno("%s: " % mapping[i])
                    v.type.accept(self)
                    self.w.wno(", ")

        def write_template_params():
            for i,v in enumerate(scope.variables):
                if i in mapping:
                    self.w.wno("%s, " % mapping[i])

        def write_opaque_params():
            for i,v in enumerate(scope.variables):
                if i in mapping:
                    self.w.wno("impl ")
                    v.type.accept(self)
                    self.w.wno(", ")

        # Write type
        self.w.write("struct %s<" % self.ident_scope(scope))
        write_template_params_with_trait()
        self.w.wnoln("> {")
        for i,v in enumerate(scope.variables):
            self.w.write("  %s: " % v.name)
            if i in mapping:
                self.w.wno(mapping[i])
            else:
                v.type.accept(self)
            self.w.wnoln(",")
        self.w.writeln("}")

        # Write type-parameterless constructor:
        self.w.write("fn %s() -> %s<" % (self.ident_new_scope(scope), self.ident_scope(scope)))
        write_opaque_params()
        self.w.wnoln("> {")
        self.w.indent()
        for v in scope.variables:
            if v.initial_value is not None:
                self.w.writeln("eprintln!(\"%s\");" % termcolor.colored("(init) %s = %s;" % (v.name, v.initial_value.render()),'blue'))
        self.w.writeln("%s {" % self.ident_scope(scope))
        self.w.indent()
        for v in scope.variables:
            if v.initial_value is not None:
                self.w.write("%s: " % v.name)
                v.initial_value.accept(self)
                self.w.wnoln(",")
            else:
                self.w.writeln("%s: Default::default()," % v.name)
        self.w.dedent()
        self.w.writeln("}")
        self.w.dedent()
        self.w.writeln("}")
        self.w.writeln()

        self.scopes_written.add(scope)

    def visit_SCCDFunction(self, type):
        self.w.wno("FnMut(")
        for i, t in enumerate(type.param_types):
            t.accept(self)
            if i != len(type.param_types)-1:
                self.w.wno(", ")
        self.w.wno(")")

    def visit__SCCDSimpleType(self, type):
        self.w.wno(type.name
            .replace("int", "i32"))
