from typing import *

class Namespace:
  def __init__(self):
    self.names: Dict[str, int] = {}

  def assign_id(self, name: str) -> int:
    return self.names.setdefault(name, len(self.names))

  def get_id(self, name: str) -> int:
    return self.names[name]
