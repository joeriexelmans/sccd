import os
from typing import Any
import lxml.etree as ET
from dataclasses import dataclass
import sccd.compiler
from sccd.runtime.xml_loader import load_model

schema_path = os.path.join(
  os.path.dirname(sccd.compiler.__file__),
  "schema",
  "sccd.xsd")
schema = ET.XMLSchema(ET.parse(schema_path))

@dataclass
class Module:
  Model: Any 
  Test: Any 

class Loader:

  def build_and_load(self, src_file: str):
    model, test = load_model(src_file)
    return Module(lambda: model, test)
