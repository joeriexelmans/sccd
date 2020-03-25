import unittest
from scope import *
from typing import *

class TestScope(unittest.TestCase):

  def test_scope(self):
    
    builtin = Scope("builtin", wider_scope=None)

    # Lookup LHS value (creating it in the current scope if not found)

    variable = builtin.put("in_state", Callable[[List[str]], bool])
    self.assertEqual(variable.offset, 0)

    globals = Scope("globals", wider_scope=builtin)
    variable = globals.put("x", int)
    self.assertEqual(variable.offset, 1)

    variable = globals.put("in_state", Callable[[List[str]], bool])
    self.assertEqual(variable.offset, 0)

    local = Scope("local", wider_scope=globals)
    variable = local.put("x", int)
    self.assertEqual(variable.offset, 1)

    # Lookup RHS value (returning None if not found)
    variable = local.get("x")
    self.assertEqual(variable.offset, 1)

    # name 'y' doesn't exist in any scope
    self.assertRaises(Exception, lambda: local.get("y"))

    # Cannot use 'in_state' as string LValue, already another type
    self.assertRaises(Exception, lambda: local.get("in_state", str))

    self.assertEqual(builtin.size(), 1)
    self.assertEqual(globals.size(), 2)
    self.assertEqual(local.size(), 2)