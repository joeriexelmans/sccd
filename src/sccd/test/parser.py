from sccd.statechart.parser.xml import *
from sccd.cd.globals import *
from sccd.controller.controller import InputEvent
from sccd.statechart.dynamic.event import Event
from sccd.cd.cd import *

@dataclass
class TestVariant:
  name: str
  model: Any
  input: list
  output: list

def test_parser_rules(statechart_parser_rules):
  globals = Globals()
  sc_rules = statechart_parser_rules(globals)
  input = []
  output = []

  def parse_test(el):
    def parse_input(el):
      def parse_input_event(el):
        name = require_attribute(el, "name")
        port = require_attribute(el, "port")
        time = require_attribute(el, "time")
        time_expr = parse_expression(globals, time)
        time_type = time_expr.init_expr(scope=None)
        check_duration_type(time_type)
        time_val = time_expr.eval(memory=None)
        input.append(InputEvent(name=name, port=port, params=[], time_offset=time_val))

      return [("event+", parse_input_event)]

    def parse_output(el):
      def parse_big_step(el):
        big_step = []
        output.append(big_step)

        def parse_output_event(el):
          name = require_attribute(el, "name")
          port = require_attribute(el, "port")
          params = []
          big_step.append(Event(id=0, name=name, port=port, params=params))

          def parse_param(el):
            val_text = require_attribute(el, "val")
            val_expr = parse_expression(globals, val_text)
            val = val_expr.eval(memory=None)
            params.append(val)

          return [("param*", parse_param)]

        return [("event+", parse_output_event)]

      return [("big_step+", parse_big_step)]

    def when_done(statechart):
      globals.set_delta(None)
      variants = statechart.semantics.generate_variants()

      def variant_description(i, variant) -> str:
        if not variant:
          return ""
        text = "Semantic variant %d of %d:" % (i+1, len(variants))
        for f in fields(variant):
          text += "\n  %s: %s" % (f.name, getattr(variant, f.name))
        return text

      return [TestVariant(
        name=variant_description(i, variant),
        model=SingleInstanceCD(
          globals,
          Statechart(
            semantics=variant,
            #  All other fields remain the same
            scope=statechart.scope,
            datamodel=statechart.datamodel,
            events=statechart.events,
            internal_events=statechart.internal_events,
            inport_events=statechart.inport_events,
            event_outport=statechart.event_outport,
            tree=statechart.tree)),
        input=input,
        output=output)
      for i, variant in enumerate(variants)]

    return (sc_rules + [("input?", parse_input), ("output?", parse_output)], when_done)

  return [("test", parse_test)]