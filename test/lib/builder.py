import os
import importlib
from sccd.compiler.sccdc import generate, Platforms

def dropext(file):
  return os.path.splitext(file)[0]

def make_dirs(file):
  os.makedirs(os.path.dirname(file), exist_ok=True)

class Builder:
  def __init__(self, build_dir: str):
    self.build_dir = build_dir

  def target_file(self, src_file: str, ext='.py') -> str:
    return os.path.join(self.build_dir, dropext(src_file)+ext)

  def module_name(self, src_file: str) -> str:
    return os.path.join(self.build_dir, dropext(src_file)).replace(os.path.sep, ".")

  def build(self, src_file: str):
    target_file = self.target_file(src_file)

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
    return importlib.import_module(self.module_name(src_file))
