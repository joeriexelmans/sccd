import sys
import os
import importlib
import unittest
import argparse

from sccd.runtime.statecharts_core import *
from sccd.compiler.sccdc import generate
from sccd.compiler.generic_generator import Platforms
from sccd.compiler.compiler_exceptions import CompilerException

BUILD_DIR = "build"

class PyTestCase(unittest.TestCase):
    def __init__(self, src_file):
        unittest.TestCase.__init__(self)
        self.src_file = src_file
        self.name = os.path.splitext(self.src_file)[0]
        self.target_file = os.path.join(BUILD_DIR, self.name+".py")
        # print("module=", os.path.join(BUILD_DIR, name).replace(os.path.sep, "."))

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
            os.makedirs(os.path.dirname(self.target_file), exist_ok=True)
            print("Compiling %s" % src_file)
            try:
                generate(self.src_file, self.target_file, "python", Platforms.Threads)
            except CompilerException:
                self.skipTest("Compilation failed.")
                return

        module = importlib.import_module(os.path.join(BUILD_DIR, self.name).replace(os.path.sep, "."))
        inputs = module.Test.input_events
        expected = module.Test.expected_events

        controller = module.Controller(False)

        if inputs:
            for i in inputs:
                controller.addInput(Event(i.name, i.port, i.parameters), int(i.time_offset * 1000))

        if not expected:
            controller.start()
            return

        output_ports = set()
        expected_result = []
        for s in expected:
            slot = []
            for event in s:
                slot.append(event)
                output_ports.add(event.port)
            if slot:
                expected_result.append(slot)

        output_listener = controller.addOutputListener(list(output_ports))

        def check_output():
            # check output
            for (slot_index, slot) in enumerate(expected_result, start=1) : 
                for entry in slot:
                    output_event = output_listener.fetch(0)
                    self.assertNotEqual(output_event, None, "Not enough output events on selected ports while checking for event %s" % entry)
                    matches = True
                    if output_event.name != entry.name :
                        matches = False
                    if output_event.port != entry.port :
                        matches = False
                    compare_parameters = output_event.getParameters()
                    if len(entry.parameters) != len(compare_parameters) :
                        matches = False
                    for index in range(len(entry.parameters)) :
                        if entry.parameters[index] !=  compare_parameters[index]:
                            matches = False

                    self.assertTrue(matches, self.src_file + ", expected results slot " + str(slot_index) + " mismatch. Expected " + str(entry) + ", but got " + str(output_event) +  " instead.") # no match found in the options

            # check if there are no extra events
            next_event = output_listener.fetch(0)
            self.assertEqual(next_event, None, "More output events than expected on selected ports: " + str(next_event))
            
        controller.start()
        check_output()
        
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

    def add_file_or_dir(path):
        if os.path.isdir(path):
            # recursively scan directories
            for r, dirs, files in os.walk(path):
                for f in files:
                    if f.endswith('.xml'):
                        add_file(os.path.join(r,f))
        elif os.path.isfile(path):
            add_file(path)


    for f in args.test:
        add_file_or_dir(f)

    if len(src_files) == 0:
        print("Note: no test files specified.")
        print()
        parser.print_usage()

    # src_files should now contain a list of XML files that need to be compiled an ran

    for src_file in src_files:
        suite.addTest(PyTestCase(src_file))

    unittest.TextTestRunner(verbosity=2).run(suite)
