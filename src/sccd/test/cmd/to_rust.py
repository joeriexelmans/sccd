import argparse
import sys
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate Rust crate from statechart / class diagram / test model. A statechart or class diagram model becomes a library. A test models becomes a binary (main function runs the test).")
    parser.add_argument('--output', metavar='DIRNAME', type=str, default="codegen", help="Name of directory (Rust crate) to create.")
    parser.add_argument('path', metavar='PATH', type=str, help="A SCCD statechart, class diagram or test XML file.")
    args = parser.parse_args()

    from sccd.test.codegen.write_crate import write_crate
    write_crate(args.path, args.output)
    sys.stderr.write("Wrote rust crate '%s'.\n" % args.output)
