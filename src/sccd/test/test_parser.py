import os
from sccd.model.statechart_parser import *
from sccd.test.test import *
from copy import deepcopy


class TestParser(StatechartParser):

  def end_event(self, el):
    big_step = self.require("big_step")
    name = el.get("name")
    port = el.get("port")
    big_step.append(Event(id=0, name=name, port=port, parameters=[]))

  def start_big_step(self, el):
    self.require("test_output")
    self.push("big_step", [])

  def end_big_step(self, el):
    output = self.require("test_output")
    big_step = self.pop("big_step")
    output.append(big_step)

  def start_input(self, el):
    self.require("test_input")

  def end_input(self, el):
    pass

  def start_output(self, el):
    self.require("test_output")

  def end_output(self, el):
    pass

  def start_test(self, el):
    self.push("context", Context(fixed_delta = None))
    self.push("test_input", [])
    self.push("test_output", [])
    self.push("statecharts", [])

  def end_test(self, el):
    tests = self.require("tests")
    src_file = self.require("src_file")

    statecharts = self.pop("statecharts")
    input = self.pop("test_input")
    output = self.pop("test_output")
    context = self.pop("context")

    if len(statecharts) != 1:
      raise Exception("Expected exactly 1 <statechart> node, got %d." % len(statecharts))
    statechart = statecharts[0]

    context.process_durations()

    def variant_description(i, variant) -> str:
      if not variant:
        return ""
      return " (variant %d: %s)" % (i, ", ".join(str(val) for val in variant.values()))

    # Generate test variants for all semantic wildcards filled in
    tests.extend( 
      Test(
        name=src_file + variant_description(i, variant),
        model=SingleInstanceModel(
          context,
          Statechart(tree=statechart.tree, datamodel=deepcopy(statechart.datamodel), semantics=dataclasses.replace(statechart.semantics, **variant))),
        input=input,
        output=output)

      for i, variant in enumerate(statechart.semantics.wildcard_cart_product())
    )
