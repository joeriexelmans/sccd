import os
from lark import Lark, Transformer
from sccd.action_lang.static.statement import *
from sccd.model.globals import *
from sccd.action_lang.static.scope import *
from sccd.statechart.static.tree import *

_grammar_dir = os.path.dirname(__file__)

with open(os.path.join(_grammar_dir,"action_language.g")) as file:
  _action_lang_grammar = file.read()


# Lark transformer for parsetree-less parsing of expressions
class ExpressionTransformer(Transformer):
  def __init__(self):
    super().__init__()
    self.globals: Globals = None

  # Expression and statement parsing

  array = Array

  block = Block

  def string(self, node):
    return StringLiteral(node[0][1:-1])

  def int(self, node):
    return IntLiteral(int(node[0].value))

  def func_call(self, node):
    return FunctionCall(node[0], node[1].children)

  def identifier(self, node):
    name = node[0].value
    return Identifier(name)

  def binary_expr(self, node):
    return BinaryExpression(node[0], node[1].value, node[2])

  def unary_expr(self, node):
    return UnaryExpression(node[0].value, node[1])

  def bool(self, node):
    return BoolLiteral({
      "True": True,
      "False": False,
      }[node[0].value])

  def group(self, node):
    return Group(node[0])

  def assignment(self, node):
    operator = node[1].value
    if operator == "=":
      return Assignment(node[0], node[2])
    else:
      # Increment, decrement etc. operators are just syntactic sugar
      bin_operator = {"+=": "+", "-=": "-", "*=": "*", "/=": "/", "//=": "//"}[operator]
      return Assignment(node[0], BinaryExpression(node[0], bin_operator, node[2]))

  def duration_literal(self, node):
    return DurationLiteral(node[0])

  def duration(self, node):
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

    d = duration(val, unit)
    self.globals.durations.append(d)
    return d

  def expression_stmt(self, node):
    return ExpressionStatement(node[0])

  def return_stmt(self, node):
    return ReturnStatement(node[0])

  def if_stmt(self, node):
    if len(node) == 2:
      return IfStatement(cond=node[0], if_body=node[1])
    else:
      return IfStatement(cond=node[0], if_body=node[1], else_body=node[2])

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

  params_decl = list

  def param_decl(self, node):
    type = {
      "int": SCCDInt,
      "str": SCCDString,
      "float": SCCDFloat,
      "dur": SCCDDuration
    }[node[1]]
    return ParamDecl(name=node[0].value, formal_type=type)

  def func_decl(self, node):
    return FunctionDeclaration(params_decl=node[0], body=node[1])

# Global variables so we don't have to rebuild our parser every time
# Obviously not thread-safe
_transformer = ExpressionTransformer()
_parser = Lark(_action_lang_grammar, parser="lalr", start=["expr", "block", "duration", "event_decl_list", "func_decl", "state_ref", "semantic_choice"], transformer=_transformer)

# Exported functions:

def parse_expression(globals: Globals, text: str) -> Expression:
  _transformer.globals = globals
  return _parser.parse(text, start="expr")

def parse_duration(globals: Globals, text: str) -> Duration:
  _transformer.globals = globals
  return _parser.parse(text, start="duration")

def parse_block(globals: Globals, text: str) -> Statement:
  _transformer.globals = globals
  return _parser.parse(text, start="block")

def parse_events_decl(globals: Globals, text: str):
  _transformer.globals = globals
  return _parser.parse(text, start="event_decl_list")

# def parse_func_decl(text: str) -> Tuple[str, List[Param]]:
#   return _parser.parse(text, start="func_decl")

def parse_state_ref(text: str):
  return _parser.parse(text, start="state_ref")

def parse_semantic_choice(choice: str):
  return _parser.parse(choice, start="semantic_choice")
