// Grammar file for Lark-parser
// At this time is only used for parsing target state references of transitions.
// In the future will contain rules for anything else that needs to be parsed, including our action language

WHITESPACE: (" " | "\t" | "\n")+
%ignore WHITESPACE

_PATH_SEP: "/" 
PARENT_NODE: ".." 
CURRENT_NODE: "." 
IDENTIFIER: /[A-Za-z_][A-Za-z_0-9]*/ 

// target of a transition
target_expr: _path | "(" _path ("," _path)+ ")" 

_path: absolute_path | relative_path 
absolute_path: _PATH_SEP _path_sequence
relative_path: _path_sequence
_path_sequence: (CURRENT_NODE | PARENT_NODE | IDENTIFIER) (_PATH_SEP _path_sequence)?
