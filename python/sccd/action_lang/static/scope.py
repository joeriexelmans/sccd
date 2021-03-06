from abc import *
from typing import *
from dataclasses import *
from inspect import signature
from sccd.action_lang.static.types import *
from sccd.common.exceptions import *
from sccd.util.visitable import *
import itertools
import termcolor
from collections import defaultdict

class ScopeError(ModelStaticError):
  def __init__(self, scope, msg):
    super().__init__(msg + '\n\n' + str(scope))


# Stateless stuff we know about a variable existing within a scope.
@dataclass(frozen=True)
class _Variable(ABC):
  __slots__ = ["_name", "offset", "type", "const", "initial_value"]
  
  _name: str # only used to print error messages
  offset: int # Offset within variable's scope. Always >= 0.
  type: SCCDType
  const: bool
  initial_value: 'Expression'

  @property
  def name(self):
    return self._name
    # return termcolor.colored(self._name, 'yellow')

  def __str__(self):
    return "+%d: %s%s: %s" % (self.offset, "(const) "if self.const else "", self.name, str(self.type))

# _scope_ctr = 0

# Stateless stuff we know about a scope (= set of named values)
class Scope(Visitable):
  __slots__ = ["name", "parent", "parent_offset", "names", "variables"]

  def __init__(self, name: str, parent: 'Scope'):
    # global _scope_ctr
    # self.id = _scope_ctr # just a unique ID within the AST (for code generation)
    # _scope_ctr += 1


    self.name = name

    self.parent = parent
    self.children = defaultdict(list) # mapping from offset to child scope

    if parent is not None:
      # Position of the start of this scope, seen from the parent scope
      self.parent_offset = parent.size()
      # Append to parent
      parent.children[self.parent_offset].append(self)
    else:
      self.parent_offset = None # value should never be used

    # Mapping from name to Value
    self.names: Dict[str, _Variable] = {}

    # All non-constant values, ordered by memory position
    self.variables: List[_Variable] = []

    self.deepest_lookup = 0


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

  def __repr__(self):
    return "Scope(%s)" % self.name

  def _internal_lookup(self, name, offset=0) -> Optional[Tuple['Scope', int, _Variable]]:
    try:
      return (self, offset, self.names[name])
    except KeyError:
      if self.parent is not None:
        got_it = self.parent._internal_lookup(name, offset - self.parent_offset)
        if got_it:
          scope, off, v = got_it
          self.deepest_lookup = max(self.deepest_lookup, self.nested_levels(off))
        return got_it
      else:
        return None

  def nested_levels(self, offset):
    if offset >= 0:
      return 0
    else:
      if self.parent is not None:
        return 1 + self.parent.nested_levels(offset + self.parent_offset)
      else:
        return 0

  # Create name in this scope
  # Precondition: _internal_lookup of name returns 'None'
  def _internal_add(self, name, type, const, initial_value: 'Expression') -> int:
    offset = len(self.variables)
    var = _Variable(name, offset, type, const, initial_value)
    self.names[name] = var
    self.variables.append(var)
    return offset

  # This is what we do when we encounter an assignment expression:
  # Add name to current scope if it doesn't exist yet in current or any parent scope.
  # Or assign to existing variable, if the name already exists, if the types match.
  # Returns tuple:
  #  - offset relative to the beginning of this scope (may be a postive or negative number).
  #  - whether a new variable was declared (and initialized)
  def put_lvalue(self, name: str, type: SCCDType, value: 'Expression') -> (int, bool):
    found = self._internal_lookup(name)
    if found:
      scope, scope_offset, var = found
      if var.type == type:
        # Cannot assign to const
        if var.const:
          raise ScopeError(self, "Cannot assign to %s: %s of scope '%s': Variable is constant." % (var.name, str(var.type), scope.name))
        # Assign to existing variable
        return (scope_offset + var.offset, False)
      else:
        # Types don't match
        raise ScopeError(self, "Cannot assign %s to %s: %s of scope '%s'" %(str(type), var.name, str(var.type), scope.name))
    else:
      # Declare new variable
      return (self._internal_add(name, type, const=False, initial_value=value), True)

  # Lookup name in this scope and its ancestors. Raises exception if not found.
  # Returns offset relative to the beginning of this scope, just like put_lvalue, and also the type of the variable.
  def get_rvalue(self, name: str) -> Tuple[int, SCCDType]:
    found = self._internal_lookup(name)
    if not found:
      raise ScopeError(self, "Name '%s' not found in any scope." % name)

    scope, scope_offset, var = found
    return (scope_offset + var.offset, var.type)

  # Attempt to declare given name in this scope.
  # Similar to put_lvalue, but only succeeds if the name does not exist yet in any scope.
  # Returns offset relative to this scope (always a positive number since this function only creates new variables in this scope)
  def declare(self, name: str, type: SCCDType, const: bool = False) -> int:
    found = self._internal_lookup(name)
    if found:
      scope, scope_offset, var = found
      raise ScopeError(self, "Cannot declare '%s' in scope '%s': Name already exists in scope '%s'" % (var.name, self.name, scope.name))

    return self._internal_add(name, type, const, initial_value=None)
