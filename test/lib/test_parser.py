import os
from sccd.parser.statechart_parser import *
from sccd.parser.expression_parser import *
from lib.test import *
from copy import deepcopy

@dataclass
class TestVariant:
  name: str
  model: Any
  input: list
  output: list

# Parses <test> element and all its children (including <statechart>)
class TestParser(StatechartParser):

  def __init__(self):
    super().__init__()
    self.tests = XmlParser.Context("tests")
    self.globals = XmlParser.Context("globals")
    self.test_input = XmlParser.Context("test_input")
    self.test_output = XmlParser.Context("test_output")
    self.big_step = XmlParser.Context("big_step")

  def end_event(self, el):
    big_step = self.big_step.require()
    name = el.get("name")
    port = el.get("port")

    if name is None:
      raise Exception("missing attribute 'name'")
    if port is None:
      raise Exception("missing attribute 'port'")
      
    big_step.append(Event(id=0, name=name, port=port, parameters=[]))

  def start_big_step(self, el):
    self.test_output.require()
    self.big_step.push([])

  def end_big_step(self, el):
    output = self.test_output.require()
    big_step = self.big_step.pop()
    output.append(big_step)

  def end_input_event(self, el):
    input = self.test_input.require()
    globals = self.globals.require()
    name = el.get("name")
    port = el.get("port")
    time = el.get("time")

    if name is None:
      raise Exception("missing attribute 'name'")
    if port is None:
      raise Exception("missing attribute 'port'")
    if time is None:
      raise Exception("missing attribute 'time'")

    duration = parse_duration(globals, time)
    input.append(InputEvent(name=name, port=port, parameters=[], time_offset=duration))

  def start_input(self, el):
    self.test_input.require()

  def end_input(self, el):
    pass

  def start_output(self, el):
    self.test_output.require()

  def end_output(self, el):
    pass

  def start_test(self, el):
    self.globals.push(Globals(fixed_delta = None))
    self.test_input.push([])
    self.test_output.push([])
    self.statecharts.push([])

  def end_test(self, el):
    tests = self.tests.require()
    src_file = self.src_file.require()

    statecharts = self.statecharts.pop()
    input = self.test_input.pop()
    output = self.test_output.pop()
    globals = self.globals.pop()

    if len(statecharts) != 1:
      raise Exception("Expected exactly 1 <statechart> node, got %d." % len(statecharts))
    statechart = statecharts[0]

    globals.process_durations()

    def variant_description(i, variant) -> str:
      if not variant:
        return ""
      return "Variant %d: %s" % (i, ", ".join(str(val) for val in variant.values()))

    # Generate test variants for all semantic wildcards filled in
    tests.extend( 
      TestVariant(
        name=variant_description(i, variant),
        model=SingleInstanceModel(
          globals,
          Statechart(tree=statechart.tree, scope=statechart.scope, semantics=dataclasses.replace(statechart.semantics, **variant))),
        input=input,
        output=output)

      for i, variant in enumerate(statechart.semantics.wildcard_cart_product())
    )
