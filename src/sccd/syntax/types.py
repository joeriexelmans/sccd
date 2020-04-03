from abc import *
from dataclasses import *
from typing import *

class SCCDType(ABC):
    @abstractmethod
    def _str(self):
        pass
        
    def __str__(self):
        import termcolor
        return termcolor.colored(self._str(), 'blue')

@dataclass(frozen=True)
class SCCDSimpleType(SCCDType):
    name: str

    def _str(self):
        return self.name

@dataclass(frozen=True)
class SCCDFunction(SCCDType):
    param_types: List[SCCDType]
    return_type: Optional[SCCDType] = None

    def _str(self):
        if self.param_types:
            s = "func(" + ",".join(str(p) for p in self.param_types) + ")"
        else:
            s = "func"
        if self.return_type:
            s += " -> " + str(self.return_type)
        return s

@dataclass(frozen=True)
class SCCDArray(SCCDType):
    element_type: SCCDType

    def _str(self):
        return "[" + str(self.element_type) + "]"

SCCDBool = SCCDSimpleType("bool")
SCCDInt = SCCDSimpleType("int")
SCCDFloat = SCCDSimpleType("float")
SCCDDuration = SCCDSimpleType("dur")
SCCDString = SCCDSimpleType("str")
