from sccd.cd.parser.xml import *
from sccd.test.parser.xml import *
from sccd.util.indenting_writer import *
from functools import partial

import sccd
RUST_DIR = os.path.dirname(sccd.__file__) + "/../../rust"

# High-level function, that takes a ...
#  - statechart-xml
#  - class-diagram-xml
#  - test-xml
# ... file and generates from it a Rust crate, which is written to filesystem as a directory.
def write_crate(src, target):
    path = os.path.dirname(src)


    globals = Globals()

    sc_parser_rules = partial(statechart_parser_rules, path=path, load_external=True)

    rules = {
        "statechart": sc_parser_rules(globals),
        "single_instance_cd": cd_parser_rules(sc_parser_rules),
        "test": test_parser_rules(sc_parser_rules),
    }

    parsed = parse_f(src, rules)

    if not os.path.isdir(target):
        os.mkdir(target)

    with open(target+"/statechartgen.rs", 'w') as file:
        w = IndentingWriter(out=file)

        w.writeln("#![allow(non_camel_case_types)]")
        w.writeln("#![allow(non_snake_case)]")
        w.writeln("#![allow(unused_labels)]")
        w.writeln("#![allow(unused_variables)]")
        w.writeln("#![allow(dead_code)]")
        w.writeln("#![allow(unused_parens)]")
        w.writeln("#![allow(unused_macros)]")
        w.writeln("#![allow(non_upper_case_globals)]")
        w.writeln("#![allow(unused_mut)]")
        w.writeln("#![allow(unused_imports)]")
        w.writeln()

        if isinstance(parsed, Statechart):
            from sccd.statechart.codegen.rust import StatechartRustGenerator

            gen = StatechartRustGenerator(w, globals)
            parsed.accept(gen)

        else:
            from sccd.test.codegen.rust import TestRustGenerator

            # can parse Class Diagrams and Tests:
            gen = TestRustGenerator(w)
            parsed.accept(gen)

    with open(target+"/Cargo.toml", 'w') as file:
        w = IndentingWriter(out=file)

        w.writeln("[package]")
        w.writeln("name = \"statechartgen\"")
        w.writeln("version = \"0.1.0\"")
        w.writeln("edition = \"2018\"")
        w.writeln()
        w.writeln("[dependencies]")
        w.writeln("sccd = { path = \"%s\" }" % RUST_DIR)
        w.writeln()
        if isinstance(parsed, Test):
            # Tests are compiled to binaries
            w.writeln("[[bin]]")
        else:
            # Everything else becomes a library
            w.writeln("[lib]")
        w.writeln("name = \"statechartgen\"")
        w.writeln("path = \"statechartgen.rs\"")
        w.writeln()
