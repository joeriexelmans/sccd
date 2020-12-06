from sccd.test.static.syntax import *
from sccd.statechart.codegen.rust import *
from sccd.util.indenting_writer import *

import os
import sccd.statechart.codegen
rustlib = os.path.dirname(sccd.statechart.codegen.__file__) + "/libstatechart.rs"

def compile_test(variants: List[TestVariant], w: IndentingWriter):

    # Note: The reason for these is that we cannot convert the casing of our state's names:
    # SCCD allows any combination of upper and lower case symbols, and
    # converting to, say, camelcase, as Rust likes it for type names,
    # could cause naming collisions.
    # Rust may output a ton of warnings for this. We disable these types of warnings,
    # so that other, more interesting types of warnings don't go unnoticed.
    w.writeln("#![allow(non_camel_case_types)]")
    w.writeln("#![allow(non_snake_case)]")
    w.writeln("#![allow(unused_labels)]")
    w.writeln("#![allow(unused_variables)]")
    w.writeln("#![allow(dead_code)]")


    with open(rustlib, 'r') as file:
        data = file.read()
        w.writeln(data)

    if len(variants) > 0:
        cd = variants[0].cd
        gen = StatechartRustGenerator(w, cd.globals)
        cd.get_default_class().accept(gen)
        # compile_statechart(cd.get_default_class(), cd.globals, w)


    w.writeln("fn main() {")
    w.indent()
    if DEBUG:
        w.writeln("debug_print_sizes();")

    for n, v in enumerate(variants):
        w.writeln("// Test variant %d" % n)
        w.writeln("let mut raised = Vec::<OutEvent>::new();")
        w.writeln("let mut output = |out: OutEvent| {")
        w.writeln("  eprintln!(\"^{}:{}\", out.port, out.event);")
        w.writeln("  raised.push(out);")
        w.writeln("};")
        w.writeln("let mut controller = Controller::<InEvent,_>::new(&mut output);")
        w.writeln("let mut sc: Statechart = Default::default();")
        w.writeln("sc.init(&mut controller);")
        for i in v.input:
            if len(i.events) > 1:
                raise UnsupportedFeature("Multiple simultaneous input events not supported")
            elif len(i.events) == 0:
                raise UnsupportedFeature("Test declares empty bag of input events")
            w.writeln("controller.set_timeout(%d, InEvent::%s);" % (i.timestamp.opt, ident_event_type(i.events[0].name)))

        w.writeln("controller.run_until(&mut sc, Until::Eternity);")
        w.writeln("assert_eq!(raised, [%s]);" % ", ".join('OutEvent{port:"%s", event:"%s"}' % (e.port, e.name) for o in v.output for e in o))
        w.writeln("eprintln!(\"Test variant %d passed\");" % n)

    w.dedent()
    w.writeln("}")
