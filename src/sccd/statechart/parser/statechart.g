// Partial grammar file for Lark-parser
// Concatenate this file with sccd/action_lang/parser/action_lang.g

%import common.WS
%ignore WS
%import common.ESCAPED_STRING


// Parsing target of a transition as a sequence of nodes

state_ref: path

?path: absolute_path | relative_path 
absolute_path: _PATH_SEP _path_sequence
relative_path: _path_sequence
_path_sequence: (CURRENT_NODE | PARENT_NODE | IDENTIFIER) (_PATH_SEP _path_sequence)?

_PATH_SEP: "/" 
PARENT_NODE: ".." 
CURRENT_NODE: "."



// Event declaration parsing

event_decl_list: neg_event_decl ("," neg_event_decl)*

?neg_event_decl: event_decl -> pos
               | "not" event_decl -> neg

?event_decl: IDENTIFIER params_decl



// Semantic option parsing

WILDCARD: "*"
?semantic_choice: WILDCARD -> wildcard
                | IDENTIFIER ("," IDENTIFIER)* -> list
