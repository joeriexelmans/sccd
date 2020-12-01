import argparse
import sys
import os

# Output can be piped to Rust compiler as follows:
#
# For statecharts (build library):
#  python -m sccd.statechart.cmd.gen_rust <path/to/statechart.xml> | rustc --crate-type=lib -
#
# For tests (build executable):
#  python -m sccd.statechart.cmd.gen_rust <path/to/test.xml> | rustc -

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate Rust code. Rust code is written to stdout.")
    parser.add_argument('path', metavar='PATH', type=str, help="A SCCD statechart or test XML file. A statechart can be compiled to a Rust library. A test can be compiled to a Rust executable (the main-function runs the test).")
    args = parser.parse_args()
    src = args.path
    path = os.path.dirname(src)

    from sccd.statechart.parser.xml import *
    from sccd.test.parser.xml import *
    from sccd.statechart.codegen.rust import compile_statechart
    from sccd.test.codegen.rust import compile_test
    from sccd.util.indenting_writer import *
    from functools import partial

    globals = Globals()

    sc_parser_rules = partial(statechart_parser_rules, path=path, load_external=True)

    rules = {
        "statechart": sc_parser_rules(globals),
        "test": test_parser_rules(sc_parser_rules),
    }

    statechart_or_test = parse_f(src, rules)

    w = IndentingWriter()

    if isinstance(statechart_or_test, Statechart):
        sys.stderr.write("Loaded statechart.\n")
        compile_statechart(statechart_or_test, globals, w)

    elif isinstance(statechart_or_test, list) and reduce(lambda x,y: x and y, (isinstance(test, TestVariant) for test in statechart_or_test)):
        sys.stderr.write("Loaded test.\n")
        compile_test(statechart_or_test, w)
