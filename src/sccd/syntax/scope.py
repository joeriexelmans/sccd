from typing import *
from dataclasses import *
import itertools

# Stateless stuff we know about a variable
@dataclass
class Variable:
  # offset in memory
  offset: int
  # type of variable
  type: type

  default_value: Any = None

# Stateless stuff we know about a scope (= set of variable names)
class Scope:
  def __init__(self, name: str, wider_scope: 'Scope'):
    self.name = name
    self.wider_scope = wider_scope
    if wider_scope:
      self.start_offset = wider_scope.start_offset + len(wider_scope.names)
    else:
      self.start_offset = 0
    self.names: Dict[str, Variable] = {}

  def size(self) -> int:
    return self.start_offset + len(self.names)

  def all(self):
    if self.wider_scope:
      return itertools.chain(self.wider_scope.all(), self.names.items())
    else:
      return self.names.items()

  def _internal_lookup(self, name: str) -> Optional[Tuple['Scope', Variable]]:
    try:
      return (self, self.names[name])
    except KeyError:
      if self.wider_scope is not None:
        return self.wider_scope._internal_lookup(name)

  def assert_available(self, name: str):
    found = self._internal_lookup(name)
    if found is not None:
      scope, variable = found
      raise Exception("Name '%s' already in use in scope '%s'" % (name, scope.name))

  def get_rvalue(self, name: str) -> Variable:
    found = self._internal_lookup(name)
    if not found:
      # return None
      raise Exception("No variable with name '%s' found in any scope." % name)
    else:
      return found[1]

  def put_lvalue(self, name: str, expected_type: type) -> Variable:
    found = self._internal_lookup(name)

    if found:
      scope, variable = found
      if variable.type == expected_type:
        # name in use, but type matches
        return variable
      else:
        raise Exception("Cannot use name '%s' as LValue of type '%s' in scope '%s'. Name already refers to variable of type '%s' in scope '%s'" % (name, str(expected_type), self.name, str(variable.type), scope.name))
    else:
      # name still available: add it to this scope
      variable = Variable(offset=self.size(), type=expected_type)
      self.names[name] = variable
      return variable

  def put_lvalue_default(self, name: str, default_value) -> Variable:
    self.assert_available(name)
    expected_type = type(default_value)
    variable = self.put_lvalue(name, expected_type)
    variable.default_value = default_value
    return variable
