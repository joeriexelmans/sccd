import threading
import subprocess
import tempfile
import os
from typing import *
from sccd.test.static.syntax import TestVariant
from sccd.test.codegen.rust import compile_test
from sccd.util.indenting_writer import IndentingWriter
from sccd.util.debug import *

# Generate Rust code from the test case. This Rust code is piped to a Rust compiler (rustc) process, which reads from stdin. The Rust compiler outputs a binary in a temp dir. We then run the created binary as a subprocess.
# If the result code of either the Rust compiler or the created binary is not 0 ("success"), the 'unittest' fails.
def run_variants(variants: List[TestVariant], unittest):
    if DEBUG:
        stdout = None
        # stderr = subprocess.STDOUT
        stderr = None
    else:
        stdout = subprocess.DEVNULL
        stderr = subprocess.STDOUT

    output_file = os.path.join(tempfile.gettempdir(), "sccd_rust_out")
    print_debug("Writing binary to " + output_file)

    with subprocess.Popen(["rustc", "-o", output_file, "-"],
        stdin=subprocess.PIPE,
        stdout=stdout,
        stderr=stderr) as pipe:

        class PipeWriter:
            def __init__(self, pipe):
                self.pipe = pipe
            def write(self, s):
                self.pipe.stdin.write(s.encode(encoding='UTF-8'))

        w = IndentingWriter(out=PipeWriter(pipe))

        compile_test(variants, w)

        pipe.stdin.close()

        print_debug("Done generating Rust code")

        pipe.wait()

    print_debug("Done generating binary")

    with subprocess.Popen([output_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE) as binary:

        status = binary.wait()

        if status != 0:
            unittest.fail("Status code %d:\n%s%s" % (status, binary.stdout.read().decode('UTF-8'), binary.stderr.read().decode('UTF-8')))

    print_debug("Done running binary")