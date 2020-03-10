import unittest
from dataclasses import *
from sccd.runtime.model import *
from sccd.runtime.controller import *

import threading
import queue

TestInput = List[InputEvent]
TestOutput = List[List[Event]]

class Test(unittest.TestCase):
  def __init__(self, name: str, model: Model, input: TestInput, output: TestOutput):
    super().__init__()
    self.name = name
    self.model = model
    self.input = input
    self.output = output

  def __str__(self):
    return self.name

  def runTest(self):
    pipe = queue.SimpleQueue()
    interrupt = queue.SimpleQueue()

    controller = Controller(self.model)

    for i in self.input:
      controller.add_input(i)

    def controller_thread():
      try:
        # Run as-fast-as-possible, always advancing time to the next item in event queue, no sleeping.
        # The call returns when the event queue is empty and therefore the simulation is finished.
        controller.run_until(None, pipe, interrupt)
      except Exception as e:
        pipe.put(e, block=True, timeout=None)
        return
      # Signal end of output
      pipe.put(None, block=True, timeout=None)

    # start the controller
    thread = threading.Thread(target=controller_thread)
    thread.start()

    # check output
    expected = self.output
    actual = []

    def fail(msg, kill=False):
      if kill:
        interrupt.put(None)
      thread.join()
      self.fail(msg + "\nExpected: " + str(expected) + "\nActual: " + str(actual) + ("\n(killed)" if kill else ""))

    while True:
      data = pipe.get(block=True, timeout=None)

      if isinstance(data, Exception):
        raise data # Exception was caught in Controller thread, throw it here instead.

      elif data is None:
        # End of output
        if len(actual) < len(expected):
          fail("Less output than expected.")
        else:
          return

      else:
        big_step = data
        big_step_index = len(actual)
        actual.append(big_step)

        if len(actual) > len(expected):
          fail("More output than expected.", kill=True)

        actual_bag = actual[big_step_index]
        expected_bag = expected[big_step_index]

        if len(actual_bag) != len(expected_bag):
          fail("Big step %d: output differs." % big_step_index, kill=True)

        # Sort both expected and actual lists of events before comparing.
        # In theory the set of events at the end of a big step is unordered.
        key_f = lambda e: "%s.%s"%(e.port, e.name)
        actual_bag.sort(key=key_f)
        expected_bag.sort(key=key_f)

        for (act_event, exp_event) in zip(actual_bag, expected_bag):
          matches = True
          if exp_event.name != act_event.name :
            matches = False
          if exp_event.port != act_event.port :
            matches = False
          if len(exp_event.parameters) != len(act_event.parameters) :
            matches = False
          for index in range(len(exp_event.parameters)) :
            if exp_event.parameters[index] !=  act_event.parameters[index]:
              matches = False
          if not matches:
            fail("Big step %d: output differs." % big_step_index, kill=True)
