from sccd.parser.statechart_parser import *
from sccd.model.globals import *
from sccd.controller.controller import InputEvent
from sccd.execution.event import Event
from sccd.model.model import *

@dataclass
class TestVariant:
  name: str
  model: Any
  input: list
  output: list

def create_test_parser(create_statechart_parser):
  globals = Globals(fixed_delta=None)
  statechart_parser = create_statechart_parser(globals)
  input = []
  output = []

  def parse_test(el):
    def parse_input(el):
      def parse_input_event(el):
        name = require_attribute(el, "name")
        port = require_attribute(el, "port")
        time = require_attribute(el, "time")
        duration = parse_duration(globals, time)
        input.append(InputEvent(name=name, port=port, params=[], time_offset=duration))

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
            val = val_expr.eval(EvalContext(current_state=None, events=[], memory=None))
            params.append(val)

          return [("param*", parse_param)]

        return [("event+", parse_output_event)]

      return [("big_step+", parse_big_step)]

    def when_done(statechart):
      globals.process_durations()
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
        model=SingleInstanceModel(
          globals,
          Statechart(
            inport_events={},
            event_outport={},
            tree=statechart.tree,
            scope=statechart.scope,
            semantics=variant)),
        input=input,
        output=output)
      for i, variant in enumerate(variants)]

    return (statechart_parser + [("input?", parse_input), ("output?", parse_output)], when_done)

  return [("test", parse_test)]