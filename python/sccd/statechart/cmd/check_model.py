import argparse
import sys
import termcolor
from sccd.statechart.parser.xml import *
from sccd.statechart.static.priority import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check if input file(s) is valid statechart model.")
    parser.add_argument('path', metavar='PATH', type=str, help="Model to check.")
    args = parser.parse_args()

    src = args.path

    path = os.path.dirname(src)
    rules = [("statechart", statechart_parser_rules(Globals(), path, load_external=True))]

    statechart = parse_f(src, rules)

    assert isinstance(statechart, Statechart)

    print("Model is OK.")
