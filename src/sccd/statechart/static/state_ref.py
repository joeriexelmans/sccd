from abc import abstractmethod
from dataclasses import dataclass
from typing import *

class PathError(Exception):
    pass

class PathItem:
    @abstractmethod
    def type(self):
        pass

class ParentNode(PathItem):
    def type(self):
        return "PARENT_NODE"

    def __repr__(self):
        return "ParentNode()"

class CurrentNode(PathItem):
    def type(self):
        return "CURRENT_NODE"

    def __repr__(self):
        return "CurrentNode()"

@dataclass
class Identifier(PathItem):
    value: str # state's short name

    def type(self):
        return "IDENTIFIER"

    def __repr__(self):
        return "Identifier(%s)" % self.value

@dataclass
class StatePath:
    is_absolute: bool
    sequence: List[PathItem]

# Used by Transition and INSTATE-macro
@dataclass(eq=False)
class StateRef:
    source: 'State'
    path: StatePath

    target: Optional['State'] = None

    def resolve(self, root):
        if self.path.is_absolute:
            state = root
        else:
            state = self.source

        for item in self.path.sequence:
            item_type = item.type()
            if item_type == "PARENT_NODE":
                state = state.parent
            elif item_type == "CURRENT_NODE":
                continue
            elif item_type == "IDENTIFIER":
                try:
                    state = [x for x in state.children if x.short_name == item.value][0]
                except IndexError as e:
                    raise PathError("%s has no child \"%s\"." % ("Root state" if state.parent is None else '"%s"'%state.short_name, item.value)) from e
        if state.parent is None:
            raise PathError("Root cannot be target of StateRef.")
        self.target = state
