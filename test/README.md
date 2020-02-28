## test.py

The Python program `test.py` replaces the old `run_tests.py`. It takes test input files (in SCCD XML format) as parameter. It compiles tests and runs them.

For example, to run the "semantics" tests:
```
python3 test.py test_files/semantics
```
This will create a 'build' directory with compiled statechart models. It is always safe to remove this directory, it merely serves as a 'cache' for build artifacts.

## render.py

The Python program `render.py` renders SVG graphs for test files. Rendered SVG files are already checked in to this repository. If you wish to re-render them, you need the NPM (NodeJS) package [state-machine-cat](https://github.com/sverweij/state-machine-cat/). Install NodeJS and NPM, and then install the NPM package 'state-machine-cat':
```
npm i -g state-machine-cat
```
Now, e.g. render the "semantics" tests:
```
python3 render.py test_files/semantics
```
By default, the SVG files are stored next to the test XML files.
