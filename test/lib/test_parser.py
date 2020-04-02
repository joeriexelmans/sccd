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

def create_test_parser(src_file, load_external = True):
  globals = Globals(fixed_delta=None)
  statechart_parser = create_statechart_parser(globals, src_file, load_external)
  input = []
  output = []

  def parse_test(el):
    def parse_input(el):
      def parse_input_event(el):
        name = el.get("name")
        port = el.get("port")
        time = el.get("time")

        if name is None:
          raise XmlError("missing attribute 'name'")
        if port is None:
          raise XmlError("missing attribute 'port'")
        if time is None:
          raise XmlError("missing attribute 'time'")

        duration = parse_duration(globals, time)
        input.append(InputEvent(name=name, port=port, params=[], time_offset=duration))

      return [("event+", parse_input_event)]

    def parse_output(el):
      def parse_big_step(el):
        big_step = []
        output.append(big_step)

        def parse_output_event(el):
          name = el.get("name")
          port = el.get("port")

          if name is None:
            raise XmlError("missing attribute 'name'")
          if port is None:
            raise XmlError("missing attribute 'port'")

          big_step.append(Event(id=0, name=name, port=port, params=[]))

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