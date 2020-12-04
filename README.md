# Statechart interpreter (and compiler!) with semantic variation

## Dependencies

Tip: Users of the Nix package manager can get a usable development environment through the supplied `shell.nix` file instead of manually installing all dependencies.

### Mandatory

* CPython >= 3.6 or PyPy >= 7.3.0 (Compatible with Python 3.6)
* The following packages from PyPi:
  * [lark-parser](https://github.com/lark-parser/lark) for parsing action language code and various fragments of the statechart language (such as target state references in an XPath-like syntax)
  * [lxml](https://lxml.de/), wraps the C-library libxml2, used for parsing the statechart XML input format
  * [termcolor](https://pypi.org/project/termcolor/) for colored terminal output
  * [dataclasses](https://pypi.org/project/dataclasses/) standard library backport, not needed for Python >= 3.7.


### Optional

* [Rust compiler](https://www.rust-lang.org/) to test compilation to Rust.
* [state-machine-cat](https://github.com/sverweij/state-machine-cat) to render statecharts as SVG images. Runs on NodeJS, installable from NPM.
* [Graphviz dot](https://graphviz.org/) to render the priorities between a statechart's transitions as a graph.

## Installation

There's a `setup.py` script in the `src` directory.

Alternatively, you can just set your `PYTHONPATH` environment variable to the absolute path of the `src` directory. This is recommended for development.

## Running the tests

Assuming you followed the installation instructions above, run:

```
python -m sccd.test.cmd.run test/test_files
```

It will recursively visit the directory tree of `test_files` and look for XML files starting with with `test_` (tests that should succeed) or `fail_` (for tests that should fail), and execute them. The tree also contains XML files starting with `statechart_`: these are individual statechart models that are not directly executable, but are used by test files. The tree also contains SVG files: these contain automatically rendered images of statechart models.

### Running the tests with Rust

The test framework can also generate Rust code for each test, and then invokes the Rust compiler (must be in your PATH as `rustc`) to compile to native code for your machine. The compiled program is then run (the main-function of the generated code executes the test). Add the `--rust` flag to try it:

```
python -m sccd.test.cmd.run --rust test/test_files
```

Rust code generation is a work in progress. Tests that contain unsupported features will be skipped.

## Runtime environment variables

The following environment variables can be set to change the behavior of the runtime. These options can be set while running the tests, or while running one of the examples.

* `SCCDDEBUG`: When set, additional debug information is printed, such as a trace of the individual transitions taken.
* `SCCDTIMINGS`: When set, at exit, the runtime will print information about how much time in total was spent during various parts of its execution, such as loading the model, generating transition candidates, executing transitions, executing actions, and more.

## Included tools

The following Python modules are runnable from terminal:

* `sccd.test.cmd.run`, already mentioned, runs tests.
* `sccd.statechart.cmd.render` will render test files and statecharts as SVG images. Depends on `state-machine-cat` command. [Example of a rendered file](examples/digitalwatch/model_digitalwatch.svg)
* `sccd.statechart.cmd.render_priorities` will render the statechart's transition priorities, as determined by the chosen semantics, as a graph. Depends on `dot` command. [Example of a rendered file](examples/digitalwatch/model_digitalwatch_priorities.svg)
* `sccd.statechart.cmd.check_model` will check if a model is valid.
* `sccd.action_lang.cmd.prompt` is an interactive prompt for the action language that is part of the statechart language.