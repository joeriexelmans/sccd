import os
import importlib
import unittest
import argparse
import threading
import queue

from sccd.compiler.sccdc import generate
from sccd.compiler.generic_generator import Platforms
from sccd.runtime.infinity import INFINITY
from sccd.runtime.event import Event
from sccd.compiler.compiler_exceptions import *
from sccd.runtime.controller import Controller

BUILD_DIR = "build"

class PyTestCase(unittest.TestCase):
    def __init__(self, src_file):
        unittest.TestCase.__init__(self)
        self.src_file = src_file
        self.name = os.path.splitext(self.src_file)[0]
        self.target_file = os.path.join(BUILD_DIR, self.name+".py")

    def __str__(self):
        return self.name

    def runTest(self):
        # Get src_file and target_file modification times
        src_file_mtime = os.path.getmtime(self.src_file)
        target_file_mtime = 0
        try:
            target_file_mtime = os.path.getmtime(self.target_file)
        except FileNotFoundError:
            pass

        if src_file_mtime > target_file_mtime:
            # (Re-)Compile test
            os.makedirs(os.path.dirname(self.target_file), exist_ok=True)
            try:
                generate(self.src_file, self.target_file, "python", Platforms.Threads)
            except TargetLanguageException :
                self.skipTest("meant for different target language.")
                return

        # Load compiled test
        module = importlib.import_module(os.path.join(BUILD_DIR, self.name).replace(os.path.sep, "."))
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
    suite = unittest.TestSuite()

    parser = argparse.ArgumentParser(description="Run SCCD tests.")
    parser.add_argument('test', metavar='test_path', type=str, nargs='*', help="Test to run. Can be a XML file or a directory. If a directory, it will be recursively scanned for XML files.")
    args = parser.parse_args()

    already_have = set()
    src_files = []

    def add_file(path):
        if path not in already_have:
            already_have.add(path)
            src_files.append(path)

    for p in args.test:
        if os.path.isdir(p):
            # recursively scan directories
            for r, dirs, files in os.walk(p):
                files.sort()
                for f in files:
                    if f.endswith('.xml'):
                        add_file(os.path.join(r,f))
        elif os.path.isfile(p):
            add_file(p)
        else:
            print("%s: not a file or a directory, skipped." % p)

    # src_files should now contain a list of XML files that need to be compiled an ran

    for src_file in src_files:
        suite.addTest(PyTestCase(src_file))

    unittest.TextTestRunner(verbosity=2).run(suite)

    if len(src_files) == 0:
        print("Note: no test files specified.")
        print()
        parser.print_usage()