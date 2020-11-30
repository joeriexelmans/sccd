from sccd.test.static.syntax import *
from sccd.statechart.codegen.rust import compile_statechart

def compile_test(variants: List[TestVariant]):
    if len(variants) > 0:
        cd = variants[0].cd
        compile_statechart(cd.get_default_class(), cd.globals)

    for v in variants:
        pass