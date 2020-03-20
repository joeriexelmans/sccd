import os
from lark import Lark, Transformer
import sccd.schema
from sccd.syntax.statement import *
from sccd.model.context import *

_schema_dir = os.path.dirname(sccd.schema.__file__)

with open(os.path.join(_schema_dir,"expr.g")) as file:
  _expr_grammar = file.read()

with open(os.path.join(_schema_dir,"state_ref.g")) as file:
  _state_ref_grammar = file.read()


# Lark transformer for parsetree-less parsing of expressions
class _ExpressionTransformer(Transformer):
  def __init__(self):
    super().__init__()
    self.context: Context = None
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
    except:
      raise Exception("Unknown variable '%s'" % name)
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

  def duration(self, node):
    unit = {
      "fs": FemtoSecond,
      "ps": PicoSecond,
      "ns": Nanosecond,
      "us": Microsecond,
      "ms": Millisecond,
      "s": Second,
      "m": Minute,
      "h": Hour
    }[node[0].children[1]]
    d = DurationLiteral(Duration(int(node[0].children[0]),unit))
    self.context.durations.append(d)
    return d

# Global variables so we don't have to rebuild our parser every time
# Obviously not thread-safe
_transformer = _ExpressionTransformer()
_expr_parser = Lark(_expr_grammar, parser="lalr", start=["expr", "block"], transformer=_transformer)
_state_ref_parser = Lark(_state_ref_grammar, parser="lalr", start=["state_ref"])

# Exported functions:

def parse_expression(context: Context, datamodel, expr: str) -> Expression:
  _transformer.context = context
  _transformer.datamodel = datamodel
  return _expr_parser.parse(expr, start="expr")

def parse_block(context: Context, datamodel, block: str) -> Statement:
  _transformer.context = context
  _transformer.datamodel = datamodel
  return _expr_parser.parse(block, start="block")

def parse_state_ref(state_ref: str):
  return _state_ref_parser.parse(state_ref, start="state_ref")
