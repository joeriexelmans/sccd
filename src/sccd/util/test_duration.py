import unittest
from duration import *

class TestDuration(unittest.TestCase):

  def test_equal(self):
    # The same amount of time, but objects not considered equal.
    x = Duration(1000, Millisecond)
    y = Duration(1, Second)
    z = Duration(3, Day)

    self.assertEqual(x, y)
    self.assertEqual(y, x)

    self.assertNotEqual(x, z)

  def test_gcd(self):
    x = Duration(20, Second)
    y = Duration(100, Microsecond)

    u = gcd(x, y)
    v = gcd(y, x)

    self.assertEqual(u, Duration(100, Microsecond))
    self.assertEqual(v, Duration(100, Microsecond))

  def test_gcd_zero(self):
    x = Duration(0)
    y = Duration(100, Microsecond)

    u = gcd(x, y)
    v = gcd(y, x)

    self.assertEqual(u, Duration(100, Microsecond))
    self.assertEqual(v, Duration(100, Microsecond))

  def test_gcd_many(self):
    l = [Duration(3, Microsecond), Duration(0), Duration(10, Millisecond)]

    u = gcd(*l)

    self.assertEqual(u, Duration(1, Microsecond))

  def test_gcd_few(self):
    l = [Duration(3, Microsecond)]

    u = gcd(*l)

    self.assertEqual(u, Duration(3, Microsecond))

  def test_gcd_none(self):
    l = []

    u = gcd(*l)

    self.assertEqual(u, Duration(0))

  def test_mult(self):
    x = Duration(10, Millisecond)
    
    self.assertEqual(x * 10, Duration(100, Millisecond))
    self.assertEqual(10 * x, Duration(100, Millisecond))

  def test_floordiv(self):
    x = Duration(100, Millisecond)
    y = Duration(10, Millisecond)
    z = Duration(3, Millisecond)

    # Duration divided by duration is factor
    self.assertEqual(x // y, 10)
    self.assertEqual(y // x, 0)
    self.assertEqual(x // z, 33)

    self.assertRaises(ZeroDivisionError, lambda: x // Duration(0))

  def test_mod(self):
    x = Duration(100, Millisecond)
    y = Duration(10, Microsecond)
    z = Duration(1, Second)
    i = Duration(3, Millisecond)

    self.assertEqual(x % y, Duration(0))
    self.assertEqual(x % z, Duration(100, Millisecond))
    self.assertEqual(x % i, Duration(1, Millisecond))
