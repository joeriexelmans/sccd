from abc import *
from typing import *
from dataclasses import *
from inspect import signature
from sccd.syntax.types import *
import itertools

# Superclass for all "user errors", errors in the model being loaded.
class ModelError(Exception):
  pass

class ScopeError(ModelError):
  def __init__(self, scope, msg):
    super().__init__(msg + '\n\nCurrent scope:\n' + str(scope))

@dataclass
class EvalContext:
    current_state: 'StatechartState'
    events: List['Event']
    memory: 'MemorySnapshot'

@dataclass(frozen=True)
class Value(ABC):
  _name: str
  type: SCCDType

  @property
  def name(self):
    import termcolor
    return termcolor.colored(self._name, 'yellow')
  

  @abstractmethod
  def is_read_only(self) -> bool:
    pass

  @abstractmethod
  def load(self, ctx: EvalContext) -> Any:
    pass
    
  @abstractmethod
  def store(self, ctx: EvalContext, value):
    pass

# Stateless stuff we know about a variable
@dataclass(frozen=True)
class Variable(Value):
  scope: 'Scope'
  offset: int # wrt. scope variable belongs to

  def is_read_only(self) -> bool:
    return False

  def load(self, ctx: EvalContext) -> Any:
    return ctx.memory.load(self.scope, self.offset)

  def store(self, ctx: EvalContext, value):
    ctx.memory.store(self.scope, self.offset, value)

  def __str__(self):
    return "Variable(%s, type=%s, offset=%s+%d)" %(self.name, str(self.type), self.scope.name, self.offset)

class EventParam(Variable):
  def __init__(self, name, type, scope, offset, event_name, param_offset):
    super().__init__(name, type, scope, offset)
    self.event_name: str = event_name
    self.param_offset: int = param_offset # offset within event parameters

  def is_read_only(self) -> bool:
    return True

  def load(self, ctx: EvalContext) -> Any:
    from_stack = Variable.load(self, ctx)
    if from_stack is not None:
      return from_stack
    else:
      # find event in event list and get the parameter we're looking for
      e = [e for e in ctx.events if e.name == self.event_name][0]
      value = e.params[self.param_offset]
      # "cache" the parameter value on our reserved stack position so the next
      # 'load' will be faster
      Variable.store(self, ctx, value)
      return value

  def store(self, ctx: EvalContext, value):
    # Bug in the code: should never attempt to write to EventParam
    assert False

# Constants are special: their values are stored in the object itself, not in
# any instance's "memory"
@dataclass(frozen=True)
class Constant(Value):
  value: Any

  def is_read_only(self) -> bool:
    return True

  def load(self, ctx: EvalContext) -> Any:
    return self.value

  def store(self, ctx: EvalContext, value):
    # Bug in the code: should never attempt to write to Constant
    assert False

# Stateless stuff we know about a scope (= set of named values)
class Scope:
  def __init__(self, name: str, parent: 'Scope'):
    self.name = name
    self.parent = parent

    if parent:
      self.parent_offset = parent.total_size()
    else:
      self.parent_offset = 0

    # Mapping from name to Value
    self.named_values: Dict[str, Value] = {}

    # All non-constant values, ordered by memory position
    self.variables: List[Variable] = []

  def local_size(self) -> int:
    return len(self.variables)

  def offset(self) -> int:
    if self.parent:
      return self.parent.total_size()
    else:
      return 0

  def total_size(self) -> int:
    return self.parent_offset + len(self.variables)

  def all_variables(self):
    if self.parent:
      return itertools.chain(self.parent.all_variables(), self.variables)
    else:
      return self.variables

  def list_scope_names(self):
    if self.parent:
      return [self.name] + self.parent.list_scope_names()
    else:
      return [self.name]

  def __str__(self):
    s = "  scope: '%s'\n" % self.name
    is_empty = True
    for v in reversed(self.variables):
      s += "    %s: %s\n" % (v.name, str(v.type))
      is_empty = False
    constants = [v for v in self.named_values.values() if v not in self.variables]
    for c in constants:
      s += "    %s (constant): %s\n" % (c.name, str(c.type))
      is_empty = False
    if is_empty:
      s += "   (empty)\n"
    if self.parent:
      s += self.parent.__str__()
    return s

  def _internal_lookup(self, name: str) -> Optional[Tuple['Scope', Value]]:
    try:
      return (self, self.named_values[name])
    except KeyError:
      if self.parent is not None:
        return self.parent._internal_lookup(name)
      else:
        return None

  def get(self, name: str) -> Value:
    found = self._internal_lookup(name)
    if not found:
      # return None
      raise ScopeError(self, "No variable with name '%s' found in any of scopes: %s" % (name, str(self.list_scope_names())))
    else:
      return found[1]

  # Add name to scope if it does not exist yet, otherwise return existing Variable for name.
  # This is done when encountering an assignment statement in a block.
  def put_variable_assignment(self, name: str, expected_type: SCCDType) -> Variable:
    found = self._internal_lookup(name)
    if found:
      scope, variable = found
      if variable.is_read_only():
        raise ScopeError(self, "Cannot assign to name '%s': Is read-only value of type '%s' in scope '%s'" %(name, str(variable.type), scope.name))
      if variable.type != expected_type:
        raise ScopeError(self, "Cannot assign type %s to variable of type %s" % (expected_type, variable.type))
      return variable
    else:
      variable = Variable(name, expected_type, scope=self,offset=self.local_size())
      self.named_values[name] = variable
      self.variables.append(variable)
      return variable

  def _assert_name_available(self, name: str):
    found = self._internal_lookup(name)
    if found:
      scope, variable = found
      raise ScopeError(self, "Name '%s' already in use in scope '%s'" % (name, scope.name))

  def add_constant(self, name: str, value: Any, type: SCCDType) -> Constant:
    self._assert_name_available(name)
    c = Constant(name, type, value=value)
    self.named_values[name] = c
    return c

  def add_variable(self, name: str, expected_type: SCCDType) -> Variable:
    self._assert_name_available(name)
    variable = Variable(name, expected_type, scope=self, offset=self.local_size())
    self.named_values[name] = variable
    self.variables.append(variable)
    return variable

  def add_event_parameter(self, event_name: str, param_name: str, type: SCCDType, param_offset=int) -> EventParam:
    self._assert_name_available(param_name)
    param = EventParam(param_name, type,
      scope=self, offset=self.local_size(),
      event_name=event_name, param_offset=param_offset)
    self.named_values[param_name] = param
    self.variables.append(param)
    return param
