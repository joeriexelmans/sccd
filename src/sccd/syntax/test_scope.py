import unittest
from scope import *
from typing import *

class TestScope(unittest.TestCase):

  def test_scope(self):
    
    builtin = Scope("builtin", parent=None)

    # Lookup LHS value (creating it in the current scope if not found)

    variable = builtin.put_variable_assignment("in_state", Callable[[List[str]], bool])
    self.assertEqual(variable.offset, 0)

    globals = Scope("globals", parent=builtin)
    variable = globals.put_variable_assignment("x", int)
    self.assertEqual(variable.offset, 1)

    variable = globals.put_variable_assignment("in_state", Callable[[List[str]], bool])
    self.assertEqual(variable.offset, 0)

    local = Scope("local", parent=globals)
    variable = local.put_variable_assignment("x", int)
    self.assertEqual(variable.offset, 1)

    # Lookup RHS value (returning None if not found)
    variable = local.get("x")
    self.assertEqual(variable.offset, 1)

    # name 'y' doesn't exist in any scope
    self.assertRaises(Exception, lambda: local.get("y"))

    self.assertEqual(builtin.total_size(), 1)
    self.assertEqual(globals.total_size(), 2)
    self.assertEqual(local.total_size(), 2)