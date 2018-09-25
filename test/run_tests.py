import sys
import os
import importlib
import unittest

from sccd.runtime.statecharts_core import *

class PyTestCase(unittest.TestCase):
    def __init__(self, file_name):
        unittest.TestCase.__init__(self)
        self.file_name = file_name
        self.name = os.path.splitext(self.file_name)[0]
        self.module = importlib.import_module(self.name.replace(os.path.sep, "."))

    def __str__(self):
        return self.file_name

    def runTest(self):
        inputs = self.module.Test.input_events
        expected = self.module.Test.expected_events

        controller = self.module.Controller(False)

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

                    self.assertTrue(matches, self.name + ", expected results slot " + str(slot_index) + " mismatch. Expected " + str(entry) + ", but got " + str(output_event) +  " instead.") # no match found in the options

            # check if there are no extra events
            next_event = output_listener.fetch(0)
            self.assertEqual(next_event, None, "More output events than expected on selected ports: " + str(next_event))
            
        controller.start()
        check_output()
        
if __name__ == '__main__':
    suite = unittest.TestSuite()

    for d in os.listdir("target_py"):
        subdir = os.path.join("target_py", d)
        if not os.path.isdir(subdir):
            continue
        for f in os.listdir(subdir):
            if f.endswith(".py") and not f.startswith("_"):
                suite.addTest(PyTestCase(os.path.join(subdir, f)))

    unittest.TextTestRunner(verbosity=2).run(suite)
