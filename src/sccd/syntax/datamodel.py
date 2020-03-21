from typing import *
from sccd.util.namespace import *

class Variable:
    def __init__(self, value, type):
        self.value = value
        self.type = type

    def __repr__(self):
      return "Var(" + str(self.type) + ' = ' + str(self.value) + ")"

class DataModel:
    def __init__(self):
        self.names: Dict[str, int] = {}
        self.storage = []

        # Reserved variable. This is dirty, find better solution
        self.create("INSTATE", None, Callable[[List[str]], bool])

    def create(self, name: str, value, _type=None) -> int:
        if _type is None:
            _type = type(value)
        if name in self.names:
            raise Exception("Name already in use.")
        id = len(self.storage)
        self.storage.append(Variable(value, _type))
        self.names[name] = id
        return id

    def lookup(self, name) -> Tuple[int, type]:
        id = self.names[name]
        var = self.storage[id]
        return (id, var.type)

    def set(self, name, value):
        id = self.names[name]
        var = self.storage[id]
        var.value = value

    def __repr__(self):
        return "DataModel(" + ", ".join(name + ': '+str(self.storage[offset]) for name,offset in self.names.items()) + ")"