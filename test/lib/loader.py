from typing import Any
from dataclasses import dataclass
from sccd.runtime.xml_loader import load_model

@dataclass
class Module:
  Model: Any 
  Test: Any 

class Loader:

  def build_and_load(self, src_file: str):
    model, test = load_model(src_file)
    return Module(lambda: model, test)
