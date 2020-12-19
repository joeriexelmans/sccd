import threading
import subprocess
import tempfile
import os
from unittest import SkipTest
from typing import *
from sccd.test.static.syntax import TestVariant
from sccd.statechart.codegen.rust import UnsupportedFeature
from sccd.test.codegen.write_crate import write_crate
from sccd.util.indenting_writer import IndentingWriter
from sccd.util.debug import *

import os
import sccd
RUST_DIR = os.path.dirname(sccd.__file__) + "/../../rust"

# Generate Rust code from the test case. This Rust code is piped to a Rust compiler (rustc) process, which reads from stdin. The Rust compiler outputs a binary in a temp dir. We then run the created binary as a subprocess.
# If the result code of either the Rust compiler or the created binary is not 0 ("success"), the 'unittest' fails.
def run_rust_test(path: str, unittest):
    if DEBUG:
        stdout = None
        stderr = None
    else:
        stdout = subprocess.DEVNULL
        stderr = subprocess.STDOUT

    from hashlib import sha1

    output = tempfile.gettempdir() + "/sccd_test_crate"

    print_debug("Writing crate to " + output)

    try:
        write_crate(path, output)
    except UnsupportedFeature as e:
        raise SkipTest("unsupported feature: " + str(e))

    print_debug("Done. Running crate...")

    with subprocess.Popen(["cargo", "run"],
        cwd=output,
        stdout=stdout,
        stderr=subprocess.PIPE) as cargo:

        cargostderr = cargo.stderr.read().decode('UTF-8')
        status = cargo.wait()

        if DEBUG:
            print(cargostderr)

        if status != 0:
            unittest.fail("Test status %d. Stderr:\n%s" % (status, cargostderr))
