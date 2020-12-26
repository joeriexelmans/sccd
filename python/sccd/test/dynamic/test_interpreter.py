import queue
import threading
from sccd.test.static.syntax import TestVariant
from sccd.controller.controller import *
from sccd.util.debug import *

import sys
if sys.version_info.minor >= 7:
  QueueImplementation = queue.SimpleQueue
else:
  QueueImplementation = queue.Queue

def run_variant(test: TestVariant, unittest):
  print_debug('\n'+test.name)
  pipe = QueueImplementation()

  current_big_step = []
  def on_output(event: OutputEvent):
    nonlocal current_big_step
    if event.port == "trace":
      if event.name == "big_step_completed":
        if len(current_big_step) > 0:
          pipe.put(current_big_step)
        current_big_step = []
    else:
      current_big_step.append(event)


  controller = Controller(test.cd, on_output)

  for bag in test.input:
    controller.schedule(
      bag.timestamp.eval(None),
      bag.events,
      controller.all_instances()) # broadcast input events to all instances

  def controller_thread():
    try:
      # Run as-fast-as-possible, always advancing time to the next item in event queue, no sleeping.
      # The call returns when the event queue is empty and therefore the simulation is finished.
      controller.run_until(None)
    except Exception as e:
      print_debug(e)
      pipe.put(e, block=True, timeout=None)
      return
    # Signal end of output
    pipe.put(None, block=True, timeout=None)

  # start the controller
  thread = threading.Thread(target=controller_thread)
  thread.daemon = True # make controller thread exit when main thread exits
  thread.start()

  # check output
  expected = test.output
  actual = []

  def fail(msg):
    thread.join()
    def pretty(output):
      return '\n'.join("%d: %s" % (i, str(big_step)) for i, big_step in enumerate(output))
    unittest.fail('\n'+test.name + '\n'+msg + "\n\nActual:\n" + pretty(actual) + "\n\nExpected:\n" + pretty(expected))

  while True:
    data = pipe.get(block=True, timeout=None)

    if isinstance(data, Exception):
      raise data # Exception was caught in Controller thread, throw it here instead.

    elif data is None:
      # End of output
      break

    else:
      actual.append(data)

  if actual != expected:
    fail("Output differs from expected.")
