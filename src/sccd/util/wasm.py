import os

try:
  WASM = bool(os.environ['SCCDWASM']=="1")
except KeyError:
  WASM = False
