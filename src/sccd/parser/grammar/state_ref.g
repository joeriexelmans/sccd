// Grammar file for Lark-parser

// Parsing target of a transition as a sequence of nodes

%import common.WS
%ignore WS
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
