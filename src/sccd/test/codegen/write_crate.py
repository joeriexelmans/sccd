from sccd.cd.parser.xml import *
from sccd.test.parser.xml import *
from sccd.util.indenting_writer import *
from functools import partial
from sccd.util.wasm import *

import sccd
RUST_DIR = os.path.dirname(sccd.__file__) + "/../../rust"

# Quick and dirty high-level function, taking a statechart / class diagram / test model in XML format and generating from it a Rust crate, which is written to the filesystem as a directory.
def write_crate(src, target):
    path = os.path.dirname(src)
    basename = os.path.splitext(os.path.basename(src))[0]

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

    with open(target+"/%s.rs" % basename, 'w') as file:
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

        if WASM:
            w.writeln("use wasm_bindgen::prelude::*;")
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
        w.writeln("name = \"%s\"" % basename)
        w.writeln("version = \"0.1.0\"")
        w.writeln("edition = \"2018\"")
        w.writeln()
        w.writeln("[dependencies]")
        w.writeln("sccd = { path = \"%s\" }" % RUST_DIR)
        if WASM:
            w.writeln("wasm-bindgen = \"*\"")
        w.writeln()
        if isinstance(parsed, Test):
            # Tests are compiled to binaries
            w.writeln("[[bin]]")
        else:
            # Everything else becomes a library
            w.writeln("[lib]")
        w.writeln("name = \"%s\"" % basename)
        w.writeln("path = \"%s.rs\"" % basename)
        w.writeln()

    with open(target+"/.gitignore", 'w') as file:
        w = IndentingWriter(out=file)
        w.writeln("/target/")
