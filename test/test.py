import argparse
import unittest
from lib.os_tools import *
from lib.test_parser import *
from sccd.util.debug import *

class PseudoSucceededTest(unittest.TestCase):
  def __init__(self, name: str, msg):
    super().__init__()
    self.name = name
    self.msg = msg

  def __str__(self):
    return self.name

  def runTest(self):
    print_debug(self.msg)

class PseudoFailedTest(unittest.TestCase):
  def __init__(self, name: str, e: Exception):
    super().__init__()
    self.name = name
    self.e = e

  def __str__(self):
    return self.name

  def runTest(self):
    raise self.e


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
        parser = TestParser()
        should_fail = os.path.basename(src_file).startswith("fail_")

        try:
            parser.tests.push([])
            statechart = parser.parse(src_file)
            tests = parser.tests.pop()

            if should_fail:
                suite.addTest(PseudoFailedTest(name=src_file, e=Exception("Unexpectedly succeeded at loading.")))
            else:
                for test in tests:
                    suite.addTest(test)

        except Exception as e:
            if should_fail:
                suite.addTest(PseudoSucceededTest(name=src_file, msg=str(e)))
            else:
                suite.addTest(PseudoFailedTest(name=src_file, e=e))


    unittest.TextTestRunner(verbosity=2).run(suite)
