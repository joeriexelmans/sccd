from sccd.statechart.codegen.rust import *

class ClassDiagramRustGenerator(StatechartRustGenerator):

    def visit_SingleInstanceCD(self, cd):
        cd.statechart.accept(self)