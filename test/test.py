import os
import unittest
import argparse
import threading
import queue
from sccd.runtime.infinity import INFINITY
from sccd.runtime.event import Event
from sccd.runtime.controller import Controller
from lib.builder import Builder
from lib.os_tools import *

class PyTestCase(unittest.TestCase):
    def __init__(self, src_file, builder):
        unittest.TestCase.__init__(self)
        self.src_file = src_file
        self.builder = builder

    def __str__(self):
        return self.src_file

    def runTest(self):
        # Build & load
        module = self.builder.build_and_load(self.src_file)
        inputs = module.Test.input_events
        expected = module.Test.expected_events # list of lists of Event objects
        model = module.Model()

        controller = Controller(model)

        # generate input
        if inputs:
            for i in inputs:
                controller.add_input(Event(i.name, i.port, i.parameters), int(i.time_offset))

        pipe = queue.Queue()

        def model_thread():
            try:
                # Run as-fast-as-possible, always advancing time to the next item in event queue, no sleeping.
                # The call returns when the event queue is empty and therefore the simulation is finished.
                controller.run_until(INFINITY, pipe)
            except Exception as e:
                pipe.put(e, block=True, timeout=None)
                return
            pipe.put(None, block=True, timeout=None)

        # start the controller
        thread = threading.Thread(target=model_thread)
        thread.start()

        # check output
        slot_index = 0
        while True:
            output = pipe.get(block=True, timeout=None)
            if isinstance(output, Exception):
                thread.join()
                raise output # Exception was caught in Controller thread, throw it here instead.
            elif output is None:
                self.assertEqual(slot_index, len(expected), "Less output was received than expected.")
                thread.join()
                return
            else:
                self.assertLess(slot_index, len(expected), "More output was received than expected.")
                exp_slot = expected[slot_index]
                # print("slot:", slot_index, ", events: ", output)

                self.assertEqual(len(exp_slot), len(output), "Slot %d length differs: Expected %s, but got %s instead." % (slot_index, exp_slot, output))

                # sort both expected and actual lists of events before comparing,
                # in theory the set of events at the end of a big step is unordered
                key_f = lambda e: "%s.%s"%(e.port, e.name)
                exp_slot.sort(key=key_f)
                output.sort(key=key_f)

                for (exp_event, event) in zip(exp_slot, output):
                    matches = True
                    if exp_event.name != event.name :
                        matches = False
                    if exp_event.port != event.port :
                        matches = False
                    if len(exp_event.parameters) != len(event.parameters) :
                        matches = False
                    for index in range(len(exp_event.parameters)) :
                        if exp_event.parameters[index] !=  event.parameters[index]:
                            matches = False

                self.assertTrue(matches, "Slot %d entry differs: Expected %s, but got %s instead." % (slot_index, exp_slot, output))
                slot_index += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Run SCCD tests.",
        epilog="Set environment variable SCCDDEBUG=1 to display debug information about the inner workings of state machines.")
    parser.add_argument('path', metavar='PATH', type=str, nargs='*', help="Tests to run. Can be a XML file or a directory. If a directory, it will be recursively scanned for XML files.")
    parser.add_argument('--build-dir', metavar='BUILD_DIR', type=str, default='build', help="Directory for built tests. Defaults to 'build'")
    args = parser.parse_args()

    src_files = get_files(args.path, filter=filter_xml)

    builder = Builder(args.build_dir)
    suite = unittest.TestSuite()
    for src_file in src_files:
        suite.addTest(PyTestCase(src_file, builder))

    if len(src_files) == 0:
        print("No input files specified.")
        print()
        parser.print_usage()
    else:
        unittest.TextTestRunner(verbosity=2).run(suite)
