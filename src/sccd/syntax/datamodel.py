from typing import *

class Variable:
    def __init__(self, value):
        self.value = value

class DataModel:
    def __init__(self):
        self.names: Dict[str, Variable] = {}
