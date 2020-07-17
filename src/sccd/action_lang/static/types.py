from abc import *
from dataclasses import *
from typing import *
import termcolor

class SCCDType(ABC):
    @abstractmethod
    def _str(self):
        pass
        
    def __str__(self):
        return termcolor.colored(self._str(), 'cyan')

    def __repr__(self):
        return "SCCDType(" + self._str() + ")"

    def is_neg(self):
        return False

    def is_summable(self, other):
        return False

    def floordiv(self, other) -> Optional['SCCDType']:
        return None

    def mult(self, other) -> Optional['SCCDType']:
        return None

    def div(self, other) -> Optional['SCCDType']:
        return None

    def exp(self, other) -> Optional['SCCDType']:
        return None

    # Can the type be used as input to '==' and '!=' operations?
    def is_eq(self, other):
        return False

    # Can the type be used as input to '<', '<=', ... operations?
    def is_ord(self, other):
        return False

    def is_bool_castable(self):
        return False

@dataclass(eq=False, repr=False)
class _SCCDSimpleType(SCCDType):
    name: str
    neg: bool = False
    summable: bool = False
    eq: bool = False
    ord: bool = False
    bool_cast: bool = False

    floordiv_dict: Dict[SCCDType, SCCDType] = field(default_factory=dict)
    mult_dict: Dict[SCCDType, SCCDType] = field(default_factory=dict)
    div_dict: Dict[SCCDType, SCCDType] = field(default_factory=dict)
    exp_dict: Dict[SCCDType, SCCDType] = field(default_factory=dict)

    def _str(self):
        return self.name

    def is_neg(self):
        return self.neg

    def is_summable(self, other):
        if other is self:
            return self.summable

    def __dict_lookup(self, dict, other):
        try:
            return dict[other]
        except KeyError:
            return None

    def floordiv(self, other):
        return self.__dict_lookup(self.floordiv_dict, other)

    def mult(self, other):
        return self.__dict_lookup(self.mult_dict, other)

    def div(self, other):
        return self.__dict_lookup(self.div_dict, other)

    def exp(self, other):
        return self.__dict_lookup(self.exp_dict, other)

    def is_eq(self, other):
        if other is self:
            return self.eq

    def is_ord(self, other):
        if other is self:
            return self.ord

    def is_bool_castable(self):
        return self.bool_cast

@dataclass(frozen=True, repr=False)
class SCCDFunction(SCCDType):
    param_types: List[SCCDType]
    return_type: Optional[SCCDType] = None

    def _str(self):
        if self.param_types:
            s = "func(" + ", ".join(p._str() for p in self.param_types) + ")"
        else:
            s = "func"
        if self.return_type:
            s += " -> " + self.return_type._str()
        return s

@dataclass(frozen=True, repr=False)
class SCCDArray(SCCDType):
    element_type: SCCDType

    def _str(self):
        return "[" + self.element_type._str() + "]"

    def is_eq(self, other):
        if isinstance(other, SCCDArray) and self.element_type.is_eq(other.element_type):
            return True
        return False

SCCDBool = _SCCDSimpleType("bool", eq=True, bool_cast=True)
SCCDInt = _SCCDSimpleType("int", neg=True, summable=True, eq=True, ord=True, bool_cast=True)
SCCDFloat = _SCCDSimpleType("float", neg=True, summable=True, eq=True, ord=True)
SCCDDuration = _SCCDSimpleType("dur", neg=True, summable=True, eq=True, ord=True, bool_cast=True)
SCCDString = _SCCDSimpleType("str", summable=True, eq=True)

# Supported operations between simple types:

SCCDInt.mult_dict = {SCCDInt: SCCDInt, SCCDFloat: SCCDFloat, SCCDDuration: SCCDDuration}
SCCDFloat.mult_dict = {SCCDInt: SCCDFloat, SCCDFloat: SCCDFloat}
SCCDDuration.mult_dict = {SCCDInt: SCCDDuration}

SCCDInt.div_dict = {SCCDInt: SCCDFloat, SCCDFloat: SCCDFloat}
SCCDFloat.div_dict = {SCCDInt: SCCDFloat, SCCDFloat: SCCDFloat}

SCCDInt.floordiv_dict = {SCCDInt: SCCDInt}
SCCDFloat.floordiv_dict = {SCCDInt: SCCDFloat, SCCDFloat: SCCDFloat}
SCCDDuration.floordiv_dict = {SCCDInt: SCCDDuration, SCCDDuration: SCCDInt}

SCCDInt.exp_dict = {SCCDInt: SCCDInt, SCCDFloat: SCCDFloat}
SCCDFloat.exp_dict = {SCCDInt: SCCDFloat, SCCDFloat: SCCDFloat}
