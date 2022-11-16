# This file is for users of the Nix package manager (https://nixos.org)

{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python3
    pkgs.python3Packages.tkinter
    pkgs.python3Packages.lark
    pkgs.python3Packages.lxml
    pkgs.python3Packages.termcolor

    #pkgs.rustc
    pkgs.rustup
    #pkgs.cargo
    pkgs.wasm-pack

    pkgs.perf-tools

  ];

  shellHook =
    ''
      export PYTHONPATH=$PYTHONPATH:$pwd/python
    '';

   PYTHONPATH = ./python;
}
