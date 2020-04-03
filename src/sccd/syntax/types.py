from abc import *
from dataclasses import *
from typing import *

class SCCDType(ABC):
    @abstractmethod
    def __str__(self):
        pass

@dataclass(frozen=True)
class SCCDSimpleType(SCCDType):
    name: str

    def __str__(self):
        return self.name

@dataclass(frozen=True)
class SCCDFunction(SCCDType):
    param_types: List[SCCDType]
    return_type: Optional[SCCDType] = None

    def __str__(self):
        if self.params:
            s = "func(" + ",".join(str(p) for p in self.params) + ")"
        else:
            s = "func"
        if self.ret:
            s += " -> " + str(self.ret)
        return s

@dataclass(frozen=True)
class SCCDArray(SCCDType):
    element_type: SCCDType

    def __str__(self):
        return "[" + str(element_type) + "]"

SCCDBool = SCCDSimpleType("bool")
SCCDInt = SCCDSimpleType("int")
SCCDFloat = SCCDSimpleType("float")
SCCDDuration = SCCDSimpleType("dur")
SCCDString = SCCDSimpleType("str")
