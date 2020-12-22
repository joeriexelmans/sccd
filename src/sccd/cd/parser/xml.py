from sccd.statechart.parser.text import *
from sccd.statechart.parser.xml import *
from sccd.cd.static.cd import *

def cd_parser_rules(statechart_parser_rules, default_delta = duration(100, Microsecond)):
  globals = Globals()
  text_parser = TextParser(globals)
  sc_rules = statechart_parser_rules(globals, text_parser=text_parser)
  delta = default_delta

  def parse_single_instance_cd(el):

    def parse_delta(el):
      nonlocal delta
      delta_expr = text_parser.parse_expr(el.text)
      delta = delta_expr.eval(None)

    def finish_single_instance_cd(statechart):
      globals.init_durations(delta)

      return SingleInstanceCD(globals, statechart)

    return ([("delta?", parse_delta), ("statechart", sc_rules)], finish_single_instance_cd)

  return parse_single_instance_cd

# This is usually how you would want to load a class diagram:
def load_cd(src):
  import os
  sc_rules = functools.partial(statechart_parser_rules, path=os.path.dirname(src))
  cd_rules = cd_parser_rules(sc_rules)
  return parse_f(src, rules=cd_rules)
