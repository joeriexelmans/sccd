from abc import *
from dataclasses import *
from typing import *
import termcolor
from sccd.util.visitable import *
from functools import reduce

class SCCDType(ABC, Visitable):
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
    function: Optional['FunctionDeclaration'] = None

    def _str(self):
        if self.param_types:
            s = "func(" + ", ".join(p._str() for p in self.param_types) + ")"
        else:
            s = "func"
        if self.return_type:
            s += " -> " + self.return_type._str()
        return s

    def __eq__(self, other):
        return isinstance(other, SCCDFunction) and self.param_types == other.param_types and self.return_type == other.return_type

@dataclass(frozen=True, repr=False)
class SCCDArray(SCCDType):
    element_type: SCCDType

    def _str(self):
        return "[" + self.element_type._str() + "]"

    def is_eq(self, other):
        if isinstance(other, SCCDArray) and self.element_type.is_eq(other.element_type):
            return True
        return False

@dataclass(frozen=True, repr=False)
class SCCDTuple(SCCDType):
    element_types: List[SCCDType]

    def _str(self):
        return "(" + ", ".join(t._str for t in self.element_types) + ")"

    def is_eq(self, other):
        return instance(other, SCCDTuple) and len(self.element_types) == len(other.element_types) and reduce(lambda x,y: x and y, (t1.is_eq(t2) for (t1, t2) in zip(self.element_types, other.element_types)))

@dataclass(frozen=True, repr=False)
class SCCDClosureObject(SCCDType):
    scope: 'Scope'
    function_type: SCCDFunction

    def _str(self):
        return "Closure(scope=%s, func=%s)" % (self.scope.name, self.function_type._str())


# @dataclass(frozen=True, repr=False)
# class SCCDFunctionCallResult(SCCDType):
#     function_type: SCCDFunction
#     return_type: SCCDType

#     def _str(self):
#         return "CallResult(%s)" % self.return_type._str()

#     def is_eq(self, other):
#         return return_type.is_eq(other)

# @dataclass(frozen=True, repr=False)
# class SCCDScope(SCCDType):
#     scope: 'Scope'

#     def _str(self):
#         return "Scope(%s)" % scope.name

#     def is_eq(self, other):
#         return self.scope is other.scope

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
