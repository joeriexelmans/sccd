import argparse
import sys
import termcolor
from sccd.statechart.parser.xml import *

from sccd.statechart.codegen.rust import compile_to_rust


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate Rust code.")
    parser.add_argument('path', metavar='PATH', type=str, help="Model to check.")
    args = parser.parse_args()

    src = args.path

    path = os.path.dirname(src)
    rules = [("statechart", statechart_parser_rules(Globals(), path, load_external=True))]

    statechart = parse_f(src, rules)

    assert isinstance(statechart, Statechart)

    sys.stderr.write("Loaded model.\n")

    compile_to_rust(statechart.tree)