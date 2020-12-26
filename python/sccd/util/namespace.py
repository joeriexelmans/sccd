from typing import *

# Assigns unique integer IDs (counting from 0) to names.
class Namespace:
  def __init__(self):
    self.ids: Dict[str, int] = {}
    self.names: List[str] = []

  def assign_id(self, name: str) -> int:
    id = self.ids.setdefault(name, len(self.names))
    if id == len(self.names):
        self.names.append(name)
    return id

  def get_id(self, name: str) -> int:
    return self.ids[name]

  def get_name(self, id: int) -> str:
    return self.names[id]
