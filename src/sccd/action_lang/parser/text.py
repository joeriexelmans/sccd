import os
from lark import Lark, Transformer
from sccd.action_lang.static.statement import *

_grammar_dir = os.path.dirname(__file__)

with open(os.path.join(_grammar_dir,"action_lang.g")) as file:
  action_lang_grammar = file.read()


# Lark transformer for generating a parse tree of our own types.
class ExpressionTransformer(Transformer):

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

    return duration(val, unit)

  def expression_stmt(self, node):
    return ExpressionStatement(node[0])

  def return_stmt(self, node):
    return ReturnStatement(node[0])

  def if_stmt(self, node):
    if len(node) == 2:
      return IfStatement(cond=node[0], if_body=node[1])
    else:
      return IfStatement(cond=node[0], if_body=node[1], else_body=node[2])

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
_parser = Lark(action_lang_grammar, parser="lalr", start=["expr", "block", "stmt"], transformer=_transformer)

# Exported functions:

def parse_expression(text: str) -> Expression:
  return _parser.parse(text, start="expr")

def parse_block(text: str) -> Block:
  return _parser.parse(text, start="block")

def parse_stmt(text: str) -> Statement:
  return _parser.parse(text, start="stmt")