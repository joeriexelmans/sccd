import unittest
from event_queue import EventQueue, EventQueueDeque

def add_pop(q, unit):
  unit.assertEqual(q.earliest_timestamp(), None)
  q.add(10, 'a')
  q.add(11, 'b')
  q.add(11, 'c')
  q.add(11, 'd')
  q.add(11, 'e')
  q.remove('c')
  q.add(11, 'f')
  q.add(11, 'g')
  unit.assertEqual(q.earliest_timestamp(), 10)
  unit.assertEqual(q.pop(), (10,'a'))
  unit.assertEqual(q.pop(), (11,'b'))
  unit.assertEqual(q.pop(), (11,'d'))
  unit.assertEqual(q.pop(), (11,'e'))
  unit.assertEqual(q.pop(), (11,'f'))
  unit.assertEqual(q.pop(), (11,'g'))
  unit.assertEqual(q.earliest_timestamp(), None)

def add_remove(q, unit):
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
    unit.assertFalse(q.is_empty())
    for x in Xs:
      q.remove(x)
    unit.assertTrue(q.is_empty())
  testrange(1)
  testrange(10)
  testrange(100)
  testrange(1000)

def due(q, unit):
  q.add(10, 'a')
  q.add(11, 'b')
  q.add(12, 'c')
  q.add(20, 'd')
  ctr = 0
  for x in q.due(15):
    ctr += 1
  unit.assertEqual(ctr, 3)
  

class TestEventQueue(unittest.TestCase):

  def test_add_pop(self):
    q = EventQueue()
    add_pop(q, self)

  def test_add_remove(self):
    q = EventQueue()
    add_remove(q, self)

  def test_due(self):
    q = EventQueue()
    due(q, self)

class TestEventQueueDeque(unittest.TestCase):

  def test_add_pop(self):
    q = EventQueueDeque()
    add_pop(q, self)

  def test_add_remove(self):
    q = EventQueueDeque()
    add_remove(q, self)

  def test_due(self):
    q = EventQueueDeque()
    due(q, self)
