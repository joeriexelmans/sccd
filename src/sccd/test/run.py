import argparse
import unittest
import threading
import queue
import functools
from sccd.util.os_tools import *
from sccd.util.debug import *
from sccd.cd.cd import *
from sccd.controller.controller import *
from sccd.test.parser import *
from sccd.util import timer

import sys
if sys.version_info.minor >= 7:
  QueueImplementation = queue.SimpleQueue
else:
  QueueImplementation = queue.Queue

# A TestCase loading and executing a statechart test file.
class Test(unittest.TestCase):
  def __init__(self, src: str):
    super().__init__()
    self.src = src

  def __str__(self):
    return self.src

  def runTest(self):
    # assume external statechart files in same directory as test
    
    path = os.path.dirname(self.src)
    sc_rules = functools.partial(statechart_parser_rules, path=path)
    test_rules = test_parser_rules(sc_rules)
    try:
      timer.start("parse test")
      test_variants = parse_f(self.src, test_rules)
      timer.stop("parse test")
    except Exception as e:
      print_debug(e)
      raise e

    for test in test_variants:
      print_debug('\n'+test.name)
      pipe = QueueImplementation()

      controller = Controller(test.cd)

      for i in test.input:
        controller.add_input(i.event, controller._duration_to_time_offset(i.at))

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
        def pretty(output):
          return '\n'.join("%d: %s" % (i, str(big_step)) for i, big_step in enumerate(output))
        self.fail('\n'+test.name + '\n'+msg + "\n\nActual:\n" + pretty(actual) + "\n\nExpected:\n" + pretty(expected))

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
          big_step_index = len(actual)
          actual.append(data)

          if len(actual) > len(expected):
            fail("More output than expected.")

          actual_big_step = actual[big_step_index]
          expected_big_step = expected[big_step_index]

          if actual_big_step != expected_big_step:
            fail("Big step %d: output differs." % big_step_index)


class FailingTest(Test):
  @unittest.expectedFailure
  def runTest(self):
    super().runTest()


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description="Run SCCD tests.",
        epilog="Set environment variable SCCDDEBUG=1 to display debug information about the inner workings of the runtime.")
    argparser.add_argument('path', metavar='PATH', type=str, nargs='*', help="Tests to run. Can be a XML file or a directory. If a directory, it will be recursively scanned for XML files.")
    argparser.add_argument('--build-dir', metavar='BUILD_DIR', type=str, default='build', help="Directory for built tests. Defaults to 'build'")
    args = argparser.parse_args()

    src_files = get_files(args.path,
        filter=lambda file: (file.startswith("test_") or file.startswith("fail_")) and file.endswith(".xml"))

    if len(src_files) == 0:
        print("No input files specified.")
        print()
        argparser.print_usage()
        exit()

    suite = unittest.TestSuite()

    for src_file in src_files:
        should_fail = os.path.basename(src_file).startswith("fail_")

        if should_fail:
            suite.addTest(FailingTest(src_file))
        else:
            suite.addTest(Test(src_file))

    unittest.TextTestRunner(verbosity=2).run(suite)
