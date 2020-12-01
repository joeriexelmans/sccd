from sccd.test.static.syntax import *
from sccd.statechart.codegen.rust import compile_statechart
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

    for n, v in enumerate(variants):
        w.writeln("// Test variant %d" % n)
        w.writeln("let mut raised = Vec::<&str>::new();")
        w.writeln("let mut output = |port, event| {")
        w.writeln("  println!(\"^{}:{}\", port, event);")
        w.writeln("  raised.push(event); return;")
        w.writeln("};")
        w.writeln("let mut sc: Statechart = Default::default();")
        w.writeln("sc.init(&mut output);")
        w.writeln("let mut controller = Controller::<Event, _>::new(output);")
        for i in v.input:
            if len(i.events) > 1:
                raise Exception("Multiple simultaneous input events not supported")
            elif len(i.events) == 0:
                raise Exception("Test declares empty bag of input events - not supported")

            w.writeln("controller.add_input(Entry::<Event, _>{")
            w.writeln("  timestamp: %d," % i.timestamp.opt)
            w.writeln("  event: Event::%s," % i.events[0].name)
            w.writeln("  target: Target::Narrowcast(&mut sc),")
            w.writeln("});")

        w.writeln("controller.run_until(Until::Eternity);")
        ctr = 0
        for o in v.output:
            for e in o:
                w.writeln("assert!(raised[%d] == \"%s\");" % (ctr, e.name))
                ctr += 1
        w.writeln("println!(\"Test variant %d passed\");" % n)

    w.dedent()
    w.writeln("}")
