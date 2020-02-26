import os
import importlib
import unittest
import argparse
import threading

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
        print()
        # Get src_file and target_file modification times
        src_file_mtime = os.path.getmtime(self.src_file)
        target_file_mtime = 0
        try:
            target_file_mtime = os.path.getmtime(self.target_file)
        except FileNotFoundError:
            pass

        if src_file_mtime > target_file_mtime:
            os.makedirs(os.path.dirname(self.target_file), exist_ok=True)
            try:
                generate(self.src_file, self.target_file, "python", Platforms.Threads)
            except TargetLanguageException :
                self.skipTest("meant for different target language.")
                return

        module = importlib.import_module(os.path.join(BUILD_DIR, self.name).replace(os.path.sep, "."))
        inputs = module.Test.input_events
        expected = module.Test.expected_events # list of lists of Event objects

        model = module.Model()
        controller = Controller(model)

        output_ports = set()
        expected_result = [] # what happens here is basically a deep-copy of the list-of-lists, why?
        for s in expected:
            slot = []
            for event in s:
                slot.append(event)
                output_ports.add(event.port)
            if slot:
                expected_result.append(slot)

        output_listener = controller.createOutputListener(list(output_ports))

        # generate input
        if inputs:
            for i in inputs:
                controller.addInput(Event(i.name, i.port, i.parameters), int(i.time_offset* 1000))

        def run_model():
            try:
                # run as-fast-as-possible, always advancing time to the next item in event queue, no sleeping
                # the call returns when the event queue is empty
                controller.run_until(INFINITY)
            except Exception as e:
                output_listener.signal_exception(e)
                return
            output_listener.signal_done()

        # start the controller
        thread = threading.Thread(target=run_model)
        thread.start()

        # check output
        slot_index = 0
        while True:
            what, arg = output_listener.fetch_blocking()
            if what == "exception":
                thread.join()
                raise arg
            elif what == "done":
                thread.join()
                return
            elif what == "output":
                output_events = arg
                slot = expected_result[slot_index]
                print("slot:", slot_index, ", events: ", output_events)

                # sort both expected and actual lists of events before comparing,
                # in theory the set of events at the end of a big step is unordered
                key_f = lambda e: "%s.%s"%(e.port, e.name)
                slot.sort(key=key_f)
                output_events.sort(key=key_f)

                self.assertEqual(len(slot), len(output_events), "Slot %d: Expected output events: %s, instead got: %s" % (slot_index, str(slot), str(output_events)))
                for (expected, actual) in zip(slot, output_events):
                    matches = True
                    if expected.name != actual.name :
                        matches = False
                    if expected.port != actual.port :
                        matches = False
                    if len(expected.parameters) != len(actual.parameters) :
                        matches = False
                    for index in range(len(expected.parameters)) :
                        if expected.parameters[index] !=  actual.parameters[index]:
                            matches = False

                self.assertTrue(matches, self.src_file + ", expected results slot " + str(slot_index) + " mismatch. Expected " + str(expected) + ", but got " + str(actual) +  " instead.") # no match found in the options
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