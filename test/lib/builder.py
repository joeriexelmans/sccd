import os
import importlib
from sccd.compiler.sccdc import generate, Platforms
from lib.os_tools import *

class Builder:
  def __init__(self, build_dir: str):
    self.build_dir = build_dir

  def build(self, src_file: str):
    target_file = os.path.join(self.build_dir, dropext(src_file)+'.py')

    # Get src_file and target_file modification times
    src_file_mtime = os.path.getmtime(src_file)
    target_file_mtime = 0.0
    try:
        target_file_mtime = os.path.getmtime(target_file)
    except FileNotFoundError:
        pass

    if src_file_mtime > target_file_mtime:
        # (Re-)Compile test
        make_dirs(target_file)
        generate(src_file, target_file, "python", Platforms.Threads)

  def build_and_load(self, src_file: str):
    self.build(src_file)
    module_name = os.path.join(self.build_dir, dropext(src_file)).replace(os.path.sep, ".")
    return importlib.import_module(module_name)
