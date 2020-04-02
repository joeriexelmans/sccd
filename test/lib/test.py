import unittest
import functools
from dataclasses import *
from sccd.model.model import *
from sccd.controller.controller import *
from lib.test_parser import *

import threading
import queue

class Test(unittest.TestCase):
  def __init__(self, src: str):
    super().__init__()
    self.src = src

  def __str__(self):
    return self.src

  def runTest(self):
    statechart_parser = functools.partial(create_statechart_parser, src_file=self.src)
    test_parser = create_test_parser(statechart_parser)
    try:
      test_variants = parse_f(self.src, test_parser)
    except Exception as e:
      print_debug(e)
      raise e

    for test in test_variants:
      print_debug('\n'+test.name)
      pipe = queue.Queue()
      # interrupt = queue.Queue()

      controller = Controller(test.model)

      for i in test.input:
        controller.add_input(i)

      def controller_thread():
        try:
          # Run as-fast-as-possible, always advancing time to the next item in event queue, no sleeping.
          # The call returns when the event queue is empty and therefore the simulation is finished.
          controller.run_until(None, pipe)
        except Exception as e:
          print_debug(e)
          pipe.put(e, block=True, timeout=None)
          return
        # Signal end of output
        pipe.put(None, block=True, timeout=None)

      # start the controller
      thread = threading.Thread(target=controller_thread)
      thread.start()

      # check output
      expected = test.output
      actual = []

      def fail(msg):
        thread.join()
        def repr(output):
          return '\n'.join("%d: %s" % (i, str(big_step)) for i, big_step in enumerate(output))
        self.fail('\n'+test.name + '\n'+msg + "\n\nActual:\n" + repr(actual) + "\n\nExpected:\n" + repr(expected))

      while True:
        data = pipe.get(block=True, timeout=None)

        if isinstance(data, Exception):
          raise data # Exception was caught in Controller thread, throw it here instead.

        elif data is None:
          # End of output
          if len(actual) < len(expected):
            fail("Less output than expected.")
          else:
            break

        else:
          big_step = data
          big_step_index = len(actual)
          actual.append(big_step)

          if len(actual) > len(expected):
            fail("More output than expected.")

          actual_bag = actual[big_step_index]
          expected_bag = expected[big_step_index]

          if len(actual_bag) != len(expected_bag):
            fail("Big step %d: output differs." % big_step_index)

          # Sort both expected and actual lists of events before comparing.
          # In theory the set of events at the end of a big step is unordered.
          # key_f = lambda e: "%s.%s"%(e.port, e.name)
          # actual_bag.sort(key=key_f)
          # expected_bag.sort(key=key_f)

          for (act_event, exp_event) in zip(actual_bag, expected_bag):
            if act_event != exp_event:
              fail("Big step %d: output differs." % big_step_index)


class FailingTest(Test):
  @unittest.expectedFailure
  def runTest(self):
    super().runTest()
