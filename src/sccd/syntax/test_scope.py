import unittest
from scope import *
from typing import *

class TestScope(unittest.TestCase):

  def test_scope(self):
    
    builtin = Scope("builtin", wider_scope=None)

    # Lookup LHS value (creating it in the current scope if not found)

    variable = builtin.lookup_lhs("in_state", Callable[[List[str]], bool])

    self.assertEqual(variable.offset, 0)

    globals = Scope("globals", wider_scope=builtin)

    variable = globals.lookup_lhs("x", int)

    self.assertEqual(variable.offset, 1)

    variable = globals.lookup_lhs("in_state", Callable[[List[str]], bool])

    self.assertEqual(variable.offset, 0)

    local = Scope("local", wider_scope=globals)

    variable = local.lookup_lhs("x", int)

    self.assertEqual(variable.offset, 1)

    # Lookup RHS value (returning None if not found)

    variable = local.lookup_rhs("x")

    self.assertEqual(variable.offset, 1)

    found = local.lookup_rhs("y")

    self.assertIs(found, None)

    # Cannot use 'in_state' as string LValue, already another type

    self.assertRaises(Exception, lambda: local.lookup_lhs("in_state", str))