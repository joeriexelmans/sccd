import os
from lark import Lark
from sccd.action_lang.parser import text as action_lang
from sccd.statechart.static.tree import *
from sccd.model.globals import *

_grammar_dir = os.path.dirname(__file__)

with open(os.path.join(_grammar_dir, "statechart.g")) as file:
  _sc_grammar = action_lang.action_lang_grammar + file.read()


# Lark transformer for parsetree-less parsing of expressions
class StatechartTransformer(action_lang.ExpressionTransformer):
  def __init__(self):
    super().__init__()
    self.globals: Globals = None

  # override: add all durations to 'globals'
  def duration(self, node):
    d = action_lang.ExpressionTransformer.duration(self, node)
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
    event_id = self.globals.events.assign_id(event_name)
    return EventDecl(id=event_id, name=event_name, params_decl=node[1])


# Global variables so we don't have to rebuild our parser every time
# Obviously not thread-safe
_transformer = StatechartTransformer()
_parser = Lark(_sc_grammar, parser="lalr", start=["expr", "block", "event_decl_list", "state_ref", "semantic_choice"], transformer=_transformer)

# Exported functions:

def parse_expression(globals: Globals, text: str) -> Expression:
  _transformer.globals = globals
  return _parser.parse(text, start="expr")

def parse_block(globals: Globals, text: str) -> Block:
  _transformer.globals = globals
  return _parser.parse(text, start="block")

def parse_events_decl(globals: Globals, text: str) -> Tuple[List[EventDecl], List[EventDecl]]:
  _transformer.globals = globals
  return _parser.parse(text, start="event_decl_list")

def parse_state_ref(text: str):
  return _parser.parse(text, start="state_ref")

def parse_semantic_choice(text: str):
  return _parser.parse(text, start="semantic_choice")