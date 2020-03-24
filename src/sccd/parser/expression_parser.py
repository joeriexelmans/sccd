import os
from lark import Lark, Transformer
from sccd.syntax.statement import *
from sccd.model.globals import *

_grammar_dir = os.path.join(os.path.dirname(__file__), "grammar")

with open(os.path.join(_grammar_dir,"action_language.g")) as file:
  _action_lang_grammar = file.read()

with open(os.path.join(_grammar_dir,"state_ref.g")) as file:
  _state_ref_grammar = file.read()


# Lark transformer for parsetree-less parsing of expressions
class _ExpressionTransformer(Transformer):
  def __init__(self):
    super().__init__()
    self.globals: Globals = None
    self.datamodel: DataModel = None

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
    try:
      offset, type = self.datamodel.lookup(name)
    except Exception as e:
      raise Exception("Unknown variable '%s'" % name) from e
    return Identifier(name, offset, type)

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
    return Assignment(node[0], node[1].value, node[2])

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

# Global variables so we don't have to rebuild our parser every time
# Obviously not thread-safe
_transformer = _ExpressionTransformer()
_action_lang_parser = Lark(_action_lang_grammar, parser="lalr", start=["expr", "block", "duration"], transformer=_transformer)
_state_ref_parser = Lark(_state_ref_grammar, parser="lalr", start=["state_ref"])

# Exported functions:

def parse_expression(globals: Globals, datamodel, expr: str) -> Expression:
  _transformer.globals = globals
  _transformer.datamodel = datamodel
  return _action_lang_parser.parse(expr, start="expr")

def parse_duration(globals: Globals, expr:str) -> Duration:
  _transformer.globals = globals
  return _action_lang_parser.parse(expr, start="duration")

def parse_block(globals: Globals, datamodel, block: str) -> Statement:
  _transformer.globals = globals
  _transformer.datamodel = datamodel
  return _action_lang_parser.parse(block, start="block")

def parse_state_ref(state_ref: str):
  return _state_ref_parser.parse(state_ref, start="state_ref")
