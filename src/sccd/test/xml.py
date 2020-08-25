from sccd.statechart.parser.xml import *
from sccd.statechart.static.globals import *
from sccd.statechart.dynamic.event import InternalEvent
from sccd.cd.static.cd import *

_empty_scope = Scope("test", parent=None)

@dataclass
class TestInputEvent:
  event: InternalEvent
  port: str
  timestamp: Expression

@dataclass
class TestVariant:
  name: str
  cd: AbstractCD
  input: List[TestInputEvent]
  output: List[List[OutputEvent]]

def test_parser_rules(statechart_parser_rules):
  globals = Globals()
  input = []
  output = []

  def parse_test(el):
    def parse_input(el):
      def parse_input_event(el):
        name = require_attribute(el, "name")
        port = require_attribute(el, "port")
        time = require_attribute(el, "time")
        time_expr = parse_expression(globals, time)
        time_type = time_expr.init_expr(scope=_empty_scope)
        check_duration_type(time_type)
        params = []
        event_id = globals.events.get_id(name)
        input.append(TestInputEvent(
          event=InternalEvent(id=event_id, name=name, params=params),
          port=port,
          timestamp=time_expr))

        def parse_param(el):
          text = require_attribute(el, "expr")
          expr = parse_expression(globals, text)
          expr.init_expr(scope=_empty_scope)
          params.append(expr.eval(memory=None))

        return [("param*", parse_param)]

      return [("event+", parse_input_event)]

    def parse_output(el):
      def parse_big_step(el):
        big_step = []
        output.append(big_step)

        def parse_output_event(el):
          name = require_attribute(el, "name")
          port = require_attribute(el, "port")
          params = []
          big_step.append(OutputEvent(name=name, port=port, params=params))

          def parse_param(el):
            val_text = require_attribute(el, "val")
            val_expr = parse_expression(globals, val_text)
            val_expr.init_expr(scope=_empty_scope)
            val = val_expr.eval(memory=None)
            params.append(val)

          return [("param*", parse_param)]

        return [("event+", parse_output_event)]

      return [("big_step+", parse_big_step)]

    def finish_test(statechart):
      globals.init_durations(delta=None)
      variants = statechart.generate_semantic_variants()

      def variant_description(i, variant) -> str:
        if not variant:
          return ""
        text = "Semantic variant %d of %d:" % (i+1, len(variants))
        text += str(variant)
        return text

      return [TestVariant(
        name=variant_description(i, variant.semantics),
        cd=SingleInstanceCD(globals=globals, statechart=variant),
        input=input,
        output=output)
      for i, variant in enumerate(variants)]

    sc_rules = statechart_parser_rules(globals)
    return ([("statechart", sc_rules), ("input?", parse_input), ("output?", parse_output)], finish_test)

  return [("test", parse_test)]