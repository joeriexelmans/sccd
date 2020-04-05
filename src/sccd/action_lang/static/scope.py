from abc import *
from typing import *
from dataclasses import *
from inspect import signature
from sccd.action_lang.static.types import *
from sccd.action_lang.static.exceptions import *
import itertools


class ScopeError(ModelError):
  def __init__(self, scope, msg):
    super().__init__(msg + '\n\nCurrent scope:\n' + str(scope))


# Stateless stuff we know about a variable existing within a scope.
@dataclass(frozen=True)
class _Variable(ABC):
  _name: str # only used to print error messages
  offset: int # Offset within variable's scope. Always >= 0.
  type: SCCDType
  const: bool

  @property
  def name(self):
    import termcolor
    return termcolor.colored(self._name, 'yellow')

  def __str__(self):
    return "+%d: %s%s: %s" % (self.offset, "(const) "if self.const else "", self.name, str(self.type))


# Stateless stuff we know about a scope (= set of named values)
class Scope:
  def __init__(self, name: str, parent: 'Scope'):
    self.name = name
    self.parent = parent
    if parent:
      # Position of the start of this scope, seen from the parent scope
      self.parent_offset = self.parent.size()
    else:
      self.parent_offset = None # value should never be used

    # Mapping from name to Value
    self.names: Dict[str, _Variable] = {}

    # All non-constant values, ordered by memory position
    self.variables: List[_Variable] = []


  def size(self) -> int:
    return len(self.variables)

  def __str__(self):
    s = "  scope: '%s'\n" % self.name

    is_empty = True
    for v in reversed(self.variables):
      s += "    %s\n" % str(v)
      is_empty = False

    if is_empty:
      s += "    ø\n"

    if self.parent:
      s += self.parent.__str__()

    return s

  def _internal_lookup(self, name, offset=0) -> Optional[Tuple['Scope', int, _Variable]]:
    try:
      return (self, offset, self.names[name])
    except KeyError:
      if self.parent is not None:
        return self.parent._internal_lookup(name, offset - self.parent_offset)
      else:
        return None

  # Create name in this scope
  def _internal_add(self, name, type, const) -> int:
    offset = len(self.variables)
    var = _Variable(name, offset, type, const)
    self.names[name] = var
    self.variables.append(var)
    return offset

  # This is what we do when we encounter an assignment expression:
  # Add name to current scope if it doesn't exist yet in current or any parent scope.
  # Or assign to existing variable, if the name already exists, if the types match.
  # Returns offset relative to the beginning of this scope (may be a postive or negative number).
  def put_lvalue(self, name: str, type: SCCDType) -> int:
    found = self._internal_lookup(name)
    if found:
      scope, scope_offset, var = found
      if var.type == type:
        if var.const:
          raise ScopeError(self, "Cannot assign to %s: %s of scope '%s': Variable is constant." % (var.name, str(var.type), scope.name))
        return scope_offset + var.offset
      else:
        raise ScopeError(self, "Cannot assign %s to %s: %s of scope '%s'" %(str(type), var.name, str(var.type), scope.name))

    return self._internal_add(name, type, const=False)

  # Lookup name in this scope and its ancestors. Raises exception if not found.
  # Returns offset relative to the beginning of this scope, just like put_lvalue, and also the type of the variable.
  def get_rvalue(self, name: str) -> Tuple[int, SCCDType]:
    found = self._internal_lookup(name)
    if not found:
      raise ScopeError(self, "Name '%s' not found in any scope." % name)

    scope, scope_offset, var = found
    return (scope_offset + var.offset, var.type)

  # Attempt to declare given name in this scope. Only succeeds if name does not exist yet in any scope.
  # Returns offset relative to this scope (always a positive number since this function only creates new variables in this scope)
  def declare(self, name: str, type: SCCDType, const: bool = False) -> int:
    found = self._internal_lookup(name)
    if found:
      scope, scope_offset, var = found
      raise ScopeError(self, "Cannot declare '%s' in scope '%s': Name already exists in scope '%s'" % (var.name, self.name, scope.name))

    return self._internal_add(name, type, const)
