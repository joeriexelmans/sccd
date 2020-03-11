// Grammar file for Lark-parser

// Parsing target of a transition as a sequence of nodes

%import common.WS
%ignore WS

%import common.SIGNED_NUMBER
%import common.ESCAPED_STRING

_PATH_SEP: "/" 
PARENT_NODE: ".." 
CURRENT_NODE: "." 
IDENTIFIER: /[A-Za-z_][A-Za-z_0-9]*/ 

// target of a transition
state_ref: path | "(" path ("," path)+ ")" 

?path: absolute_path | relative_path 
absolute_path: _PATH_SEP _path_sequence
relative_path: _path_sequence
_path_sequence: (CURRENT_NODE | PARENT_NODE | IDENTIFIER) (_PATH_SEP _path_sequence)?


// Parsing expressions

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
     | array

func_call: atom "(" param_list ")"
param_list: ( expr ("," expr)* )?  -> params

array: "[" (expr ("," expr)*)? "]"

?literal: ESCAPED_STRING -> string
        | INT -> int
        | bool_literal -> bool

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

?bool_literal: TRUE | FALSE

TRUE: "True"
FALSE: "False"

INT: /[0-9]+/


// Statement parsing

block: stmt (";" stmt)*

?stmt: assignment

assignment: lhs assign_operator expr

increment: lhs "+=" expr

?lhs: IDENTIFIER -> identifier

?assign_operator: ASSIGN | INCREMENT | DECREMENT | MULTIPLY | DIVIDE

ASSIGN: "="
INCREMENT: "+="
DECREMENT: "-="
MULTIPLY: "*="
DIVIDE: "/="
