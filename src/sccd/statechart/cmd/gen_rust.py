import argparse
import sys
import os

# Output can be piped to Rust compiler as follows:
#
# For statecharts, class diagrams (build library):
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
    from sccd.util.indenting_writer import *
    from functools import partial

    globals = Globals()

    sc_parser_rules = partial(statechart_parser_rules, path=path, load_external=True)

    rules = {
        "statechart": sc_parser_rules(globals),
        "single_instance_cd": cd_parser_rules(sc_parser_rules),
        "test": test_parser_rules(sc_parser_rules),
    }

    parsed = parse_f(src, rules)

    sys.stderr.write("Parsing finished.\n")

    w = IndentingWriter()

    if isinstance(parsed, Statechart):
        
        from sccd.statechart.codegen.rust import StatechartRustGenerator

        gen = StatechartRustGenerator(w, globals)
        gen.accept(parsed)

    elif isinstance(parsed, AbstractCD):
        from sccd.cd.codegen.rust import ClassDiagramRustGenerator

        gen = ClassDiagramRustGenerator(w, globals)
        gen.accept(parsed)

    elif isinstance(parsed, list) and reduce(lambda x,y: x and y, (isinstance(test, TestVariant) for test in parsed)):
        sys.stderr.write("Loaded test.\n")

        from sccd.test.codegen.rust import compile_test
        compile_test(parsed, w)
