import lark
from sccd.action_lang.parser import text as action_lang
from sccd.statechart.static.tree import *
from sccd.statechart.static.globals import *
from sccd.statechart.static.state_ref import *

# Lark transformer for parsetree-less parsing of expressions
# Extends action language's ExpressionTransformer
class Transformer(action_lang.Transformer):
  def __init__(self, globals):
    super().__init__()
    self.globals = globals

  def absolute_path(self, node):
    # print("ABS", node[0])
    return StatePath(is_absolute=True, sequence=node[0])

  def relative_path(self, node):
    # print("REL", node[0])
    return StatePath(is_absolute=False, sequence=node[0])

  def path_sequence(self, node):
    # print("PATH_SEQ", node)
    if node[0].type == "PARENT_NODE":
      item = ParentNode()
    elif node[0].type == "CURRENT_NODE":
      item = CurrentNode()
    elif node[0].type == "IDENTIFIER":
      item = Identifier(value=node[0].value)

    # Concatenate with rest of path
    if len(node) == 2:
      return [item] + node[1]
    else:
      return [item]

  # override: all durations must be added to 'globals'
  def duration_literal(self, node):
    val = int(node[0])
    suffix = node[1]

    unit = {
      "d": None, # 'd' stands for "duration", the non-unit for all zero-durations.
                 # need this to parse zero-duration as a duration instead of int.
      "fs": FemtoSecond,
      "ps": PicoSecond,
      "ns": Nanosecond,
      "us": Microsecond,
      "ms": Millisecond,
      "s": Second,
      "m": Minute,
      "h": Hour
    }[suffix]

    d = SCDurationLiteral(duration(val, unit))
    self.globals.durations.append(d)
    return d

  # Event declaration parsing

  def event_decl_list(self, node):
    pos_events = []
    neg_events = []

    for n in node:
      if n.data == "pos":
        pos_events.append(n.children[0])
      elif n.data == "neg":
        neg_events.append(n.children[0])

    return (pos_events, neg_events)

  def event_decl(self, node):
    event_name = node[0].value
    return EventDecl(name=event_name, params_decl=node[1])

import os, pathlib
grammar_dir = os.path.dirname(__file__)
grammar_path = os.path.join(grammar_dir,"statechart.g")
with open(grammar_path) as file:
  # Concatenate Action Lang and SC grammars
  grammar = action_lang.grammar + file.read()
cache_file = action_lang.cache_file+'_'+str(pathlib.Path(grammar_path).stat().st_mtime_ns)


# Parses action language expressions and statements, and also event decls, state refs and semantic choices. 
class TextParser(action_lang.TextParser):
  def __init__(self, globals):
    # Building the parser is actually the slowest step of parsing a statechart model.
    # Doesn't have to happen every time, so should find a way to speed this up.
    parser = lark.Lark(grammar, parser="lalr", start=["expr", "block", "type_annot", "event_decl_list", "path", "semantic_choice"], transformer=Transformer(globals), cache=cache_file)
    super().__init__(parser)

  def parse_semantic_choice(self, text: str):
    return self.parser.parse(text, start="semantic_choice")

  def parse_events_decl(self, text: str) -> Tuple[List[EventDecl], List[EventDecl]]:
    return self.parser.parse(text, start="event_decl_list")

  def parse_path(self, text: str):
    return self.parser.parse(text, start="path")

  def parse_type(self, text: str):
    return self.parser.parse(text, start="type_annot")

  def parse_block(self, text: str) -> Statement:
    return self.parser.parse(text, start="block")
