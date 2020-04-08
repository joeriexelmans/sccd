# Statechart interpreter with semantic variation

## Dependencies

### Mandatory

* CPython >= 3.6 or PyPy >= 7.3.0 (Compatible with Python 3.6)
* The following packages from PyPi:
  * [lark-parser](https://github.com/lark-parser/lark) for parsing action code and various fragments of the statechart language
  * [lxml](https://lxml.de/) for parsing the statechart XML input format
  * [termcolor](https://pypi.org/project/termcolor/) for colored terminal output
  * [dataclasses](https://pypi.org/project/dataclasses/) (not needed for Python >= 3.7)

### Optional

* [state-machine-cat](https://github.com/sverweij/state-machine-cat) to render statecharts as SVG images. Runs on NodeJS, installable from NPM.

## Installation

There's a `setup.py` script in the `src` directory.

Alternatively, you can just set your `PYTHONPATH` environment variable to the absolute path of the `src` directory. This is recommended for development.

## Running the tests

Assuming you followed the installation instructions above, run:

```
python3 -m sccd.test.run test/test_files
```

## Runtime environment variables

The following environment variables can be set to change the behavior of the runtime. These options can be set while running the tests, or while running one of the examples.

* `SCCDDEBUG`: When set, additional debug information is printed, such as the individual transitions taken.
* `SCCDTIMINGS`: When set, at exit, the runtime will print information about how much time in total was spent during various parts of its execution, such as loading the model (if model was loaded from a file), generating transition candidates, executing transitions, executing actions, and more.

## Included tools

The following Python modules are runnable from terminal:

* `sccd.test.run`, already mentioned, runs tests.
* `sccd.render` will render test files and statecharts as SVG images. Depends on `state-machine-cat` command.
* `sccd.statechart.cmd.check_model` will check if a model is valid.
* `sccd.action_lang.cmd.prompt` is an interactive prompt for the action language that is part of the statechart language.
