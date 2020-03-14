import unittest
from duration import *


class TestDuration(unittest.TestCase):

  def test_equal(self):
    # The same amount of time, but objects not considered equal.
    x = Duration(1000, Millisecond)
    y = Duration(1, Second)

    self.assertNotEqual(x, y)

    self.assertEqual(x.normalize(), y.normalize())

    # original objects left intact by normalize() operation
    self.assertNotEqual(x, y)

  def test_convert_unit(self):
    x = Duration(2, Second)

    x2 = x.convert(Microsecond)

    self.assertEqual(x2, Duration(2000000, Microsecond))

  def test_convert_zero(self):
    x = Duration(0)

    x2 = x.convert(Millisecond)

    self.assertEqual(x2, Duration(0))

  def test_normalize(self):
    x = Duration(1000, Millisecond)
    y = Duration(1000000, Microsecond)
    z = Duration(0)

    self.assertEqual(x.normalize(), Duration(1, Second))
    self.assertEqual(y.normalize(), Duration(1, Second))
    self.assertEqual(z.normalize(), Duration(0))

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
