from sccd.test.static.syntax import *
from sccd.statechart.codegen.rust import compile_statechart
from sccd.util.indenting_writer import *

def compile_test(variants: List[TestVariant], w: IndentingWriter):
    if len(variants) > 0:
        cd = variants[0].cd
        compile_statechart(cd.get_default_class(), cd.globals, w)


    w.writeln("fn main() {")
    w.indent()

    for v in variants:
        w.writeln("// Test variant")
        w.writeln("let mut sc: Statechart = Default::default();")
        for i in v.input:
            if len(i.events) > 1:
                raise Exception("Multiple simultaneous input events not supported")
            elif len(i.events) == 0:
                raise Exception("Test declares empty bag of input events - not supported")
            e = i.events[0]

            w.writeln("println!(\"time is now %s\");" % i.timestamp.render())
            w.writeln("sc.fair_step(Some(Event::%s));" % e.name)
        pass

    w.dedent()
    w.writeln("}")