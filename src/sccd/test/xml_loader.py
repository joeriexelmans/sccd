import os
import lxml.etree as ET
from lark import Lark, Transformer
from sccd.test.test import *
from sccd.model.model import *
from sccd.model.xml_loader import *
from sccd.syntax.statechart import *
from copy import deepcopy

# For a test with "should_fail_load" attribute set, we generate a succeeding test if the loading failed :)
class PseudoTest(unittest.TestCase):
  def __init__(self, name: str, failed: bool = False, msg: str = ""):
    super().__init__()
    self.name = name
    self.failed = failed
    self.msg = msg

  def __str__(self):
    return self.name

  def runTest(self):
    if self.failed:
      self.fail(self.msg)


# Returned list contains more than one test if the semantic configuration contains wildcard values.
def load_test(src_file) -> List[Test]:
  print("loading", src_file, "...")
  namespace = Context()

  test_node = ET.parse(src_file).getroot()
  # should_fail_load = test_node.get("should_fail_load", "") == "true"

# try:
  sc_node = test_node.find("statechart")
  src = sc_node.get("src")
  if src is None:
    statechart = load_statechart(namespace, sc_node)
  else:
    external_file = os.path.join(os.path.dirname(src_file), src)
    print("loading", external_file, "...")
    external_node = ET.parse(external_file).getroot()
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

# except Exception as e:
#   if should_fail_load:
#     print("load failed as expected:", e)
#     return [ PseudoTest(name=src_file) ]
#   else:
#     return [ PseudoTest(name=src_file, failed=True, msg=str(e)) ]

# if should_fail_load:
#   return [ PseudoTest(name=src_file, failed=True, msg="Should not have succeeded at loading test.") ]

  return [
    Test(
      name=src_file + variant_description(i, variant),
      model=SingleInstanceModel(
        namespace,
        Statechart(tree=statechart.tree, datamodel=deepcopy(statechart.datamodel), semantics=dataclasses.replace(statechart.semantics, **variant))),
      input=input,
      output=output)
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
