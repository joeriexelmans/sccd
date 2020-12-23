import lark
from sccd.action_lang.static.statement import *
from collections import defaultdict

# Lark transformer for generating a parse tree of our own types.
class Transformer(lark.Transformer):

  def __init__(self):
    self.macros = defaultdict(list)

  def set_macro(self, macro_id, constructor):
    self.macros[macro_id].append(constructor)

  def unset_macro(self, macro_id):
    self.macros[macro_id].pop()

  array = Array

  block = Block

  def string_literal(self, node):
    return StringLiteral(node[0][1:-1])

  def int_literal(self, node):
    return IntLiteral(int(node[0].value))

  def float_literal(self, node):
    return FloatLiteral(float(node[0].value))

  def bool_literal(self, node):
    return BoolLiteral({
      "True": True,
      "False": False,
      }[node[0].value])

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

    return DurationLiteral(duration(val, unit))

  def func_call(self, node):
    return FunctionCall(node[0], node[1].children)

  def macro_call(self, node):
    macro_id = node[0]
    params = node[1].children
    try:
      constructor = self.macros[macro_id][-1]
    except IndexError as e:
      raise Exception("Unknown macro: %s" % macro_id) from e

    return constructor(params)

  def array_indexed(self, node):
    return ArrayIndexed(node[0], node[1])

  def identifier(self, node):
    name = node[0].value
    return Identifier(name)

  def binary_expr(self, node):
    return BinaryExpression(node[0], node[1].value, node[2])

  def unary_expr(self, node):
    return UnaryExpression(node[0].value, node[1])

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

  def expression_stmt(self, node):
    return ExpressionStatement(node[0])

  def return_stmt(self, node):
    return ReturnStatement(node[0])

  def if_stmt(self, node):
    if len(node) == 2:
      return IfStatement(cond=node[0], if_body=node[1])
    else:
      return IfStatement(cond=node[0], if_body=node[1], else_body=node[2])

  def import_stmt(self, node):
    return ImportStatement(module_name=node[0])

  params_decl = list

  def param_decl(self, node):
    return ParamDecl(name=node[0].value, formal_type=node[1])

  def type_annot(self, node):
    return {
      "int": SCCDInt,
      "str": SCCDString,
      "float": SCCDFloat,
      "dur": SCCDDuration,
    }[node[0]]

  def func_type(self, node):
    if len(node) > 1:
      return SCCDFunction(param_types=node[0], return_type=node[1])
    else:
      return SCCDFunction(param_types=node[0])

  param_types = list

  def func_decl(self, node):
    return FunctionDeclaration(params_decl=node[0], body=node[1])

import os, tempfile, pathlib
grammar_dir = os.path.dirname(__file__)
grammar_path = os.path.join(grammar_dir,"action_lang.g")
with open(grammar_path) as file:
  grammar = file.read()
cache_file = tempfile.gettempdir()+'/lark_cache_'+str(pathlib.Path(grammar_path).stat().st_mtime_ns)

class TextParser:
  def __init__(self, parser=None):
    if parser is None:
      self.parser = lark.Lark(grammar, parser="lalr", start=["expr", "stmt"], transformer=Transformer(), cache=cache_file)
    else:
      self.parser = parser

  def parse_expr(self, text: str) -> Expression:
    return self.parser.parse(text, start="expr")

  def parse_stmt(self, text: str) -> Statement:
    return self.parser.parse(text, start="block")
