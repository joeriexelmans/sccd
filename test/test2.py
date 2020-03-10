import argparse
from lib.os_tools import *
from sccd.runtime.test import *
from sccd.runtime.xml_loader2 import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Run SCCD tests.",
        epilog="Set environment variable SCCDDEBUG=1 to display debug information about the inner workings of state machines.")
    parser.add_argument('path', metavar='PATH', type=str, nargs='*', help="Tests to run. Can be a XML file or a directory. If a directory, it will be recursively scanned for XML files.")
    parser.add_argument('--build-dir', metavar='BUILD_DIR', type=str, default='build', help="Directory for built tests. Defaults to 'build'")
    args = parser.parse_args()

    src_files = get_files(args.path, filter=lambda file: file.endswith(".test.xml"))

    suite = unittest.TestSuite()
    for src_file in src_files:
        tests = load_test(src_file)
        for test in tests:
            suite.addTest(test)

    if len(src_files) == 0:
        print("No input files specified.")
        print()
        parser.print_usage()
    else:
        unittest.TextTestRunner(verbosity=2).run(suite)
