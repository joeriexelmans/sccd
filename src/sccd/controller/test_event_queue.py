import unittest
from event_queue import EventQueue
  

class TestEventQueue(unittest.TestCase):

  def test_add_pop(self):
    q = EventQueue()
    self.assertEqual(q.earliest_timestamp(), None)
    q.add(10, 'a')
    q.add(11, 'b')
    q.add(11, 'c')
    q.add(11, 'd')
    q.add(11, 'e')
    q.remove('c')
    q.add(11, 'f')
    q.add(11, 'g')
    self.assertEqual(q.earliest_timestamp(), 10)
    self.assertEqual(q.pop(), (10,'a'))
    self.assertEqual(q.pop(), (11,'b'))
    self.assertEqual(q.pop(), (11,'d'))
    self.assertEqual(q.pop(), (11,'e'))
    self.assertEqual(q.pop(), (11,'f'))
    self.assertEqual(q.pop(), (11,'g'))
    self.assertEqual(q.earliest_timestamp(), None)

  def test_add_remove(self):
    q = EventQueue()

    class X:
      n = 0
      def __init__(self):
        self.x = X.n
        X.n += 1
      def __repr__(self):
        return "x%d"%self.x

    def testrange(N):
      Xs = []
      for i in range(10):
        x = X()
        Xs.append(x)
        q.add(i, x)
      for x in Xs:
        q.remove(x)

    testrange(1)
    testrange(10)
    testrange(100)
    testrange(1000)

  def test_due(self):
    q = EventQueue()
    q.add(10, 'a')
    q.add(11, 'b')
    q.add(12, 'c')
    q.add(20, 'd')
    ctr = 0
    for x in q.due(15):
      ctr += 1
    self.assertEqual(ctr, 3)
