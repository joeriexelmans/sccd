import sys

class IndentingWriter:
    def __init__(self, spaces=2, out=sys.stdout, initial=0):
        self.spaces = spaces
        self.out = out
        self.state = initial

    def indent(self):
        self.state += self.spaces

    def dedent(self):
        self.state -= self.spaces

    def writeln(self, s=""):
        if s == "":
            self.out.write('\n')
        else:
            self.out.write(' '*self.state + s + '\n')

    # "write no indent"
    def wno(self, s):
        self.out.write(s)

    def wnoln(self, s=""):
        self.out.write(s + '\n')

    def write(self, s=""):
        self.out.write(' '*self.state + s)
