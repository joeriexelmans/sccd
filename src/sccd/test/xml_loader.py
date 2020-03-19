import os
import lxml.etree as etree
from lark import Lark, Transformer
from sccd.test.test import *
from sccd.model.model import *
from sccd.model.xml_loader import *
from sccd.syntax.statechart import *
from sccd.util.debug import *
from copy import deepcopy

class PseudoSucceededTest(unittest.TestCase):
  def __init__(self, name: str, msg):
    super().__init__()
    self.name = name
    self.msg = msg

  def __str__(self):
    return self.name

  def runTest(self):
    print_debug(self.msg)

class PseudoFailedTest(unittest.TestCase):
  def __init__(self, name: str, e: Exception):
    super().__init__()
    self.name = name
    self.e = e

  def __str__(self):
    return self.name

  def runTest(self):
    raise self.e

# Returned list contains more than one test if the semantic configuration contains wildcard values.
def load_test(src_file) -> List[Test]:
  should_fail = os.path.basename(src_file).startswith("fail_")

  context = Context()

  test_node = etree.parse(src_file).getroot()

  try:
    sc_node = test_node.find("statechart")
    src = sc_node.get("src")
    if src is None:
      statechart = load_statechart(context, sc_node)
    else:
      external_file = os.path.join(os.path.dirname(src_file), src)
      # print("loading", external_file, "...")
      external_node = etree.parse(external_file).getroot()
      statechart = load_statechart(context, external_node)
      semantics_node = sc_node.find("override_semantics")
      load_semantics(statechart.semantics, semantics_node)

    input_node = test_node.find("input")
    output_node = test_node.find("output")
    input = load_input(input_node)
    output = load_output(output_node)

    context.convert_durations_auto_delta()

    def variant_description(i, variant) -> str:
      if not variant:
        return ""
      return " (variant %d: %s)" % (i, ", ".join(str(val) for val in variant.values()))

    if should_fail:
      return [PseudoFailedTest(name=src_file, e=Exception("Unexpectedly succeeded at loading."))]
    else:
      return [
        Test(
          name=src_file + variant_description(i, variant),
          model=SingleInstanceModel(
            context,
            Statechart(tree=statechart.tree, datamodel=deepcopy(statechart.datamodel), semantics=dataclasses.replace(statechart.semantics, **variant))),
          input=input,
          output=output)
        for i, variant in enumerate(statechart.semantics.wildcard_cart_product())
      ]

  except Exception as e:
    if should_fail:
      return [PseudoSucceededTest(name=src_file, msg=str(e))]
    else:
      return [PseudoFailedTest(name=src_file, e=e)]

def load_input(input_node) -> TestInput:
  input = []
  if input_node is not None:
    for event_node in input_node:
      name = event_node.get("name")
      port = event_node.get("port")
      time = int(event_node.get("time"))
      input.append(InputEvent(name, port, [], time))
  return input

def load_output(output_node) -> TestOutput:
  output = []
  if output_node is not None: 
    for big_step_node in output_node:
      big_step = []
      for event_node in big_step_node:
        name = event_node.get("name")
        port = event_node.get("port")
        parameters = [] # todo: read params
        big_step.append(Event(id=0, name=name, port=port, parameters=parameters))
      output.append(big_step)
  return output
