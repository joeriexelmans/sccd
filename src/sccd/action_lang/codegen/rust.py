from sccd.action_lang.static.statement import *

class UnsupportedFeature(Exception):
    pass

class ActionLangRustGenerator(Visitor):
    def __init__(self, w):
        self.w = w
        self.scopes = []

    def default(self, what):
        raise UnsupportedFeature(what)

    def visit_Block(self, stmt):
        # self.w.writeln("{")
        for s in stmt.stmts:
            s.accept(self)
        # self.w.writeln("}")

    def visit_Assignment(self, stmt):
        self.w.write('')
        stmt.lhs.accept(self)
        self.w.wno(" = ")
        stmt.rhs.accept(self)
        self.w.wnoln(";")
        self.w.writeln("eprintln!(\"%s\");" % termcolor.colored(stmt.render(),'blue'))

    def visit_IfStatement(self, stmt):
        self.w.wno("if ")
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
        self.w.wno("return ")
        stmt.expr.accept(self)
        self.w.writeln(";")

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
        self.w.wno(" (")

        if expr.operator == "**":
            raise UnsupportedFeature("exponent operator")
        else:
            expr.lhs.accept(self)
            self.w.wno(" %s " % expr.operator
                .replace('and', '&&')
                .replace('or', '||')
                .replace('//', '/')) # integer division
            expr.rhs.accept(self)

        self.w.wno(") ")

    def visit_UnaryExpression(self, expr):
        self.w.wno(expr.operator
            .replace('not', '!'))
        expr.expr.accept(self)

    def visit_Group(self, expr):
        # self.w.wno(" (")
        expr.subexpr.accept(self)
        # self.w.wno(") ")

    def visit_FunctionDeclaration(self, expr):
        self.w.wno("|")
        for p in expr.params_decl:
            p.accept(self)
            self.w.wno(", ")
        self.w.wnoln("| = {")
        self.w.indent()
        expr.body.accept(self)
        self.w.dedent()
        self.w.write("}")
        self.scopes.append(expr.scope)

    def visit_FunctionCall(self, expr):
        self.w.wno("(")
        expr.function.accept(self)
        self.w.wno(")(")
        for p in expr.params:
            p.accept(self)
            self.w.wno(", ")
        self.w.wno(")")

    def visit_Identifier(self, lval):
        self.w.wno("sc.data."+lval.name)

    def visit_Scope(self, scope):
        self.w.writeln("#[derive(Default)]")
        self.w.writeln("struct Scope_%s {" % scope.name)
        for v in scope.variables:
            self.w.write("  %s: " % v.name)
            v.type.accept(self)
            self.w.wnoln(",")
        self.w.writeln("}")
        self.w.writeln()


    def visit__SCCDSimpleType(self, type):
        self.w.wno(type.name
            .replace("int", "i32"))
