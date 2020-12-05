from sccd.test.static.syntax import *
from sccd.statechart.codegen.rust import *
from sccd.util.indenting_writer import *

import os
import sccd.cd.codegen
rustlib = os.path.dirname(sccd.cd.codegen.__file__) + "/sccdlib.rs"

def compile_test(variants: List[TestVariant], w: IndentingWriter):

    with open(rustlib, 'r') as file:
        data = file.read()
        w.writeln(data)

    if len(variants) > 0:
        cd = variants[0].cd
        compile_statechart(cd.get_default_class(), cd.globals, w)


    w.writeln("fn main() {")
    w.indent()
    if DEBUG:
        w.writeln("debug_print_sizes();")

    for n, v in enumerate(variants):
        w.writeln("// Test variant %d" % n)
        w.writeln("let mut raised = Vec::<OutEvent>::new();")
        w.writeln("let mut output = |out: OutEvent| {")
        w.writeln("  println!(\"^{}:{}\", out.port, out.event);")
        w.writeln("  raised.push(out);")
        w.writeln("};")
        w.writeln("let mut controller = Controller::<Event,_>::new(&mut output);")
        w.writeln("let mut sc: Statechart = Default::default();")
        w.writeln("sc.init(&mut controller);")
        for i in v.input:
            if len(i.events) > 1:
                raise Exception("Multiple simultaneous input events not supported")
            elif len(i.events) == 0:
                raise Exception("Test declares empty bag of input events - not supported")
            w.writeln("controller.set_timeout(%d, Event::%s);" % (i.timestamp.opt, ident_event(i.events[0].name)))

        w.writeln("controller.run_until(&mut sc, Until::Eternity);")
        ctr = 0
        for o in v.output:
            for e in o:
                w.writeln("  assert!(raised[%d].event == \"%s\", format!(\"\nExpected: %s\nGot: {:#?}\", raised));" % (ctr, e.name, v.output))
                ctr += 1
        w.writeln("println!(\"Test variant %d passed\");" % n)

    w.dedent()
    w.writeln("}")
