from abc import *
from typing import *
from dataclasses import *
from inspect import signature
import itertools

@dataclass
class EvalContext:
    current_state: 'StatechartState'
    events: List['Event']
    memory: 'MemorySnapshot'

@dataclass
class Value(ABC):
  name: str
  type: type

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
@dataclass
class Variable(Value):
  offset: int
  initial: Any = None

  def is_read_only(self) -> bool:
    return False

  def load(self, ctx: EvalContext) -> Any:
    return ctx.memory.load(self.offset)

  def store(self, ctx: EvalContext, value):
    ctx.memory.store(self.offset, value)

class EventParam(Variable):
  def __init__(self, name, type, offset, event_name, param_offset):
    super().__init__(name, type, offset)
    self.event_name: str = event_name
    self.param_offset: int = param_offset

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
      Variable.store(self, ctx)
      return value

  def store(self, ctx: EvalContext, value):
    # Bug in the code: should never attempt to write to EventParam
    assert False

# Constants are special: their values are stored in the object itself, not in
# any instance's "memory"
@dataclass
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
    self.frozen = False

    if parent:
      self.parent_offset = parent.total_size()
      self.parent.frozen = True
    else:
      self.parent_offset = 0

    # Mapping from name to Value
    self.named_values: Dict[str, Value] = {}

    # All non-constant values, ordered by memory position
    self.variables: List[Value] = []

  def local_size(self) -> int:
    return len(self.variables)

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
      raise Exception("No variable with name '%s' found in any of scopes: %s" % (name, str(self.list_scope_names())))
    else:
      return found[1]

  # Add name to scope if it does not exist yet, otherwise return existing Variable for name.
  # This is done when encountering an assignment statement in a block.
  def put_variable_assignment(self, name: str, expected_type: type) -> Variable:
    assert not self.frozen

    found = self._internal_lookup(name)
    if found:
      scope, variable = found
      if variable.is_read_only():
        raise Exception("Cannot assign to name '%s': Is read-only value of type '%s' in scope '%s'" %(name, str(variable.type), scope.name))
      if variable.type == expected_type:
        return variable
    else:
      variable = Variable(name=name, type=expected_type, offset=self.total_size())
      self.named_values[name] = variable
      self.variables.append(variable)
      return variable

  def _assert_name_available(self, name: str):
    found = self._internal_lookup(name)
    if found:
      scope, variable = found
      raise Exception("Name '%s' already in use in scope '%s'" % (name, scope.name))

  def add_constant(self, name: str, value) -> Constant:
    assert not self.frozen
    self._assert_name_available(name)
    c = Constant(name=name, type=type(value), value=value)
    self.named_values[name] = c
    return c

  def add_variable_w_initial(self, name: str, initial: Any) -> Variable:
    assert not self.frozen
    self._assert_name_available(name)
    variable = Variable(name=name, type=type(initial), offset=self.total_size(), initial=initial)
    self.named_values[name] = variable
    self.variables.append(variable)
    return variable

  def add_event_parameter(self, event_name: str, param_name: str, type: type, param_offset=int) -> EventParam:
    assert not self.frozen
    self._assert_name_available(param_name)
    param = EventParam(
      name=param_name, type=type, offset=self.total_size(),
      event_name=event_name, param_offset=param_offset)
    self.named_values[param_name] = param
    self.variables.append(param)
    return param

  def add_function(self, name: str, function: Callable) -> Constant:
    sig = signature(function)
    return_type = sig.return_annotation
    args = list(sig.parameters.values())[1:] # hide 'EvalContext' parameter to user
    param_types = [a.annotation for a in args]
    function_type = Callable[param_types, return_type]
    
    c = Constant(name=name, type=function_type, value=function)
    self.named_values[name] = c
    return c
