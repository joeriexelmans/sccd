import argparse
import unittest
from lib.os_tools import *
from lib.test import *
from sccd.util.debug import *

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
