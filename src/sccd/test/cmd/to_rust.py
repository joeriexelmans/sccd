import argparse
import sys
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate Rust code. Rust code is written to stdout.")
    parser.add_argument('--output', metavar='DIRNAME', type=str, default="codegen", help="Name of directory (Rust crate) to create.")
    parser.add_argument('path', metavar='PATH', type=str, help="A SCCD statechart or test XML file. A statechart can be compiled to a Rust library. A test can be compiled to a Rust executable (the main-function runs the test).")
    args = parser.parse_args()

    from sccd.test.codegen.write_crate import write_crate
    write_crate(args.path, args.output)
    sys.stderr.write("Wrote rust crate '%s'.\n" % args.output)
