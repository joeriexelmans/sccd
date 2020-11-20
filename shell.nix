# This file is for users of the Nix package manager (https://nixos.org)

{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python38
    pkgs.python38Packages.tkinter
    pkgs.python38Packages.lark-parser
    pkgs.python38Packages.lxml
    pkgs.python38Packages.termcolor
  ];

  PYTHONPATH = ./. + "/src";
}