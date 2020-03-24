import unittest
from duration import *

class TestDuration(unittest.TestCase):

  def test_equal(self):
    # The same amount of time, but objects not considered equal.
    x = duration(1000, Millisecond)
    y = duration(1, Second)
    z = duration(3, Day)

    self.assertEqual(x, y)
    self.assertEqual(y, x)

    self.assertNotEqual(x, z)

  def test_gcd(self):
    x = duration(20, Second)
    y = duration(100, Microsecond)

    u = gcd(x, y)
    v = gcd(y, x)

    self.assertEqual(u, duration(100, Microsecond))
    self.assertEqual(v, duration(100, Microsecond))

  def test_gcd_zero(self):
    x = duration(0)
    y = duration(100, Microsecond)

    u = gcd(x, y)
    v = gcd(y, x)

    self.assertEqual(u, duration(100, Microsecond))
    self.assertEqual(v, duration(100, Microsecond))

  def test_gcd_many(self):
    l = [duration(3, Microsecond), duration(0), duration(10, Millisecond)]

    u = gcd(*l)

    self.assertEqual(u, duration(1, Microsecond))

  def test_gcd_few(self):
    l = [duration(3, Microsecond)]

    u = gcd(*l)

    self.assertEqual(u, duration(3, Microsecond))

  def test_gcd_none(self):
    l = []

    u = gcd(*l)

    self.assertEqual(u, duration(0))

  def test_mult(self):
    x = duration(10, Millisecond)
    
    self.assertEqual(x * 10, duration(100, Millisecond))
    self.assertEqual(10 * x, duration(100, Millisecond))

  def test_floordiv(self):
    x = duration(100, Millisecond)
    y = duration(10, Millisecond)
    z = duration(3, Millisecond)

    # Duration divided by duration is factor
    self.assertEqual(x // y, 10)
    self.assertEqual(y // x, 0)
    self.assertEqual(x // z, 33)

    self.assertRaises(ZeroDivisionError, lambda: x // duration(0))

  def test_mod(self):
    x = duration(100, Millisecond)
    y = duration(10, Microsecond)
    z = duration(1, Second)
    i = duration(3, Millisecond)

    self.assertEqual(x % y, duration(0))
    self.assertEqual(x % z, duration(100, Millisecond))
    self.assertEqual(x % i, duration(1, Millisecond))
