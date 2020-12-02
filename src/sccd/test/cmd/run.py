import argparse
import unittest
import functools

from sccd.util.os_tools import *
from sccd.util.debug import *
from sccd.statechart.parser.xml import *
from sccd.test.parser.xml import *
from sccd.util import timer

# A TestCase loading and executing a statechart test file.
class Test(unittest.TestCase):
  def __init__(self, src: str, enable_rust: bool):
    super().__init__()
    self.src = src
    self.enable_rust = enable_rust

  def __str__(self):
    return self.src

  def runTest(self):
    # assume external statechart files in same directory as test
    
    path = os.path.dirname(self.src)
    sc_rules = functools.partial(statechart_parser_rules, path=path)
    test_rules = test_parser_rules(sc_rules)
    try:
      with timer.Context("parse test"):
        test_variants = parse_f(self.src, {"test" :test_rules})


      if self.enable_rust:
        from sccd.test.dynamic.test_rust import run_variants
        run_variants(test_variants, self)
      else:
        from sccd.test.dynamic.test_interpreter import run_variant
        for v in test_variants:
          run_variant(v, self)

    except Exception as e:
      print_debug(e)
      raise e

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
    argparser.add_argument('--rust', action='store_true', help="Instead of testing the interpreter, generate Rust code from test and run it. Depends on the 'rustc' command in your environment's PATH. Does not depend on Cargo.")
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
            suite.addTest(FailingTest(src_file, args.rust))
        else:
            suite.addTest(Test(src_file, args.rust))

    unittest.TextTestRunner(verbosity=2).run(suite)
