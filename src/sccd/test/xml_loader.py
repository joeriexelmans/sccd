import os
import lxml.etree as ET
from lark import Lark, Transformer
from sccd.test.test import *
from sccd.model.model import *
from sccd.model.xml_loader import *
from sccd.syntax.statechart import *
from copy import deepcopy

# Returned list contains more than one test if the semantic configuration contains wildcard values.
def load_test(src_file) -> List[Test]:
  namespace = Namespace()

  test_node = ET.parse(src_file).getroot()
  sc_node = test_node.find("statechart")
  src = sc_node.get("src")
  if src is None:
    statechart = load_statechart(namespace, sc_node)
  else:
    external_node = ET.parse(os.path.join(os.path.dirname(src_file), src)).getroot()
    statechart = load_statechart(namespace, external_node)
    semantics_node = sc_node.find("override_semantics")
    load_semantics(statechart.semantics, semantics_node)

  input_node = test_node.find("input")
  output_node = test_node.find("output")
  input = load_input(input_node)
  output = load_output(output_node)

  def variant_description(i, variant) -> str:
    if not variant:
      return ""
    return " (variant %d: %s)" % (i, ",".join(str(val) for val in variant.values()))

  return [
    Test(
      src_file + variant_description(i, variant),
      SingleInstanceModel(
        namespace,
        Statechart(tree=statechart.tree, datamodel=deepcopy(statechart.datamodel), semantics=dataclasses.replace(statechart.semantics, **variant))),
      input,
      output)
    for i, variant in enumerate(statechart.semantics.wildcard_cart_product())
  ]

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
