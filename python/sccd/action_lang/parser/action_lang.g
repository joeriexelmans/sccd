// Grammar file for Lark-parser

%import common.WS
%ignore WS
%import common.ESCAPED_STRING


// Expression parsing

// We use the same operators and operator precedence rules as Python

?expr: or_expr

?or_expr: and_expr
        | or_expr OR and_expr    -> binary_expr

?and_expr: not_expr
         | and_expr AND not_expr  -> binary_expr

?not_expr: comp_expr
         | NOT comp_expr           -> unary_expr

?comp_expr: add_expr
          | comp_expr compare_operator add_expr -> binary_expr

?add_expr: mult_expr
         | add_expr add_operator mult_expr -> binary_expr

?mult_expr: unary
          | mult_expr mult_operator unary -> binary_expr

?unary: exponent
      | MINUS exponent  -> unary_expr

?exponent: atom
         | atom EXP exponent -> binary_expr

?atom: IDENTIFIER               -> identifier
     | "(" expr ")"             -> group
     | literal
     | func_call
     | macro_call
     | array_indexed
     | func_decl
     | array

IDENTIFIER: /[A-Za-z_][A-Za-z_0-9]*/ 

MACRO_IDENTIFIER: "@" IDENTIFIER
macro_call: MACRO_IDENTIFIER "(" param_list ")"

func_call: atom "(" param_list ")"
param_list: ( expr ("," expr)* )?  -> params

array_indexed: atom "[" expr "]"

func_decl: "func" params_decl stmt
params_decl: ( "(" param_decl ("," param_decl)* ")" )?
?param_decl: IDENTIFIER ":" type_annot
type_annot: TYPE_INT | TYPE_STR | TYPE_DUR | TYPE_FLOAT | TYPE_BOOL
          | "func" param_types? return_type? -> func_type

param_types: "(" type_annot ( "," type_annot )* ")"
?return_type: "->" type_annot

TYPE_INT: "int"
TYPE_STR: "str"
TYPE_DUR: "dur"
TYPE_FLOAT: "float"
TYPE_BOOL: "bool"

array: "[" (expr ("," expr)*)? "]"

?literal: ESCAPED_STRING -> string_literal
        | INT -> int_literal
        | FLOAT -> float_literal
        | bool_literal
        | duration_literal

?compare_operator: EQ | NEQ | GT | GEQ | LT | LEQ
?add_operator: PLUS | MINUS
?mult_operator: MULT | DIV | FLOORDIV | MOD

AND: "and"
OR: "or"
EQ: "=="
NEQ: "!="
GT: ">"
GEQ: ">="
LT: "<"
LEQ: "<="
PLUS: "+"
MINUS: "-"
MULT: "*"
DIV: "/"
FLOORDIV: "//"
MOD: "%"
EXP: "**"
NOT: "not"

bool_literal: TRUE | FALSE

TRUE: "True"
FALSE: "False"

INT: /[0-9]+/
FLOAT: /[0-9]+\.[0-9]*/

duration_literal: (INT duration_unit)+

?duration_unit: TIME_H | TIME_M | TIME_S | TIME_MS | TIME_US | TIME_NS | TIME_PS | TIME_FS | TIME_D

TIME_H: "h"
TIME_M: "m"
TIME_S: "s"
TIME_MS: "ms"
TIME_US: "us"
TIME_NS: "ns"
TIME_PS: "ps"
TIME_FS: "fs"

TIME_D: "d" // for zero-duration


// Statement parsing

?block: (stmt)*

MODULE_NAME: IDENTIFIER ("." IDENTIFIER)*

?stmt: assignment ";"
     | expr ";" -> expression_stmt
     | "return" expr ";" -> return_stmt
     | "{" block "}" -> block
     | "if" "(" expr ")" stmt ("else" stmt)? -> if_stmt
     | "import" MODULE_NAME ";" -> import_stmt

assignment: lhs assign_operator expr

increment: lhs "+=" expr

?lhs: IDENTIFIER -> identifier
    | array_indexed

?assign_operator: ASSIGN | INCREMENT | DECREMENT | MULTIPLY | DIVIDE

ASSIGN: "="
INCREMENT: "+="
DECREMENT: "-="
MULTIPLY: "*="
DIVIDE: "/="
FLOORDIVIDE: "//="

COMMENT: "#" /(.)*/ "\n"
%ignore COMMENT
