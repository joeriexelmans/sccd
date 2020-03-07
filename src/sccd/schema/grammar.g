// Grammar file for Lark-parser
// At this time is only used for parsing target state references of transitions.
// In the future will contain rules for anything else that needs to be parsed, including our action language

%import common.WS
%ignore WS

%import common.SIGNED_NUMBER
%import common.ESCAPED_STRING

_PATH_SEP: "/" 
PARENT_NODE: ".." 
CURRENT_NODE: "." 
IDENTIFIER: /[A-Za-z_][A-Za-z_0-9]*/ 

// target of a transition
state_ref: _path | "(" _path ("," _path)+ ")" 

_path: absolute_path | relative_path 
absolute_path: _PATH_SEP _path_sequence
relative_path: _path_sequence
_path_sequence: (CURRENT_NODE | PARENT_NODE | IDENTIFIER) (_PATH_SEP _path_sequence)?




?expr: or_expr

?or_expr: and_expr
       | or_expr "||" and_expr -> or

?and_expr: atom
        | and_expr "&&" atom   -> and

?atom: IDENTIFIER               -> identifier
    | "-" atom                 -> neg
    | "(" expr ")"             -> group
    | literal                 
    | func_call
    | array

array: "[" (expr ("," expr)*)? "]"

?literal: ESCAPED_STRING -> string
        | SIGNED_NUMBER -> number
        | bool_literal -> bool
?bool_literal: TRUE | FALSE

func_call: atom "(" param_list ")"
param_list: ( expr ("," expr)* )?  -> params

TRUE: "true"
FALSE: "false"
