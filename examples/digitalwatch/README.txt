Directory layout
----------------

common/
    digitalwatch.xml
        The statechart model

python/
    run.py
        Python script that runs the demo with the statechart interpreter. Run it from the 'python' directory.

webassembly/
    index.html
        Web page that runs the demo with WebAssembly code, generated from Rust code, in turn generated from the statechart model.

        In order to run this demo, start a static HTTP server in the 'digitalwatch' directory:
          python -m http.server

        Then navigate your browser to http://localhost:8000/webassembly/

    codegen/
        Generated code: This is a Rust crate produced by SCCD compiler (module "sccd.test.cmd.to_rust") from 'common/digitalwatch.xml'. Building it with 'cargo' produces a library.

    wasm/
        Rust crate containing Rust glue code to interact with the generated code in 'codegen' from JavaScript. It should be built with the 'wasm-pack' command, producing JavaScript glue code, and a .wasm-file.

        pkg/
            Generated code: This directory contains the JavaScript glue code and .wasm-file built from this crate.
