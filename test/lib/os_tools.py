import os
from typing import List, Callable, Set

# For a given list of files and or directories, get all the 
def get_files(paths: List[str], filter: Callable[[str], bool]) -> List[str]:
  already_have: Set[str] = set()
  src_files = []

  def add_file(path):
      if path not in already_have:
          already_have.add(path)
          src_files.append(path)

  for p in paths:
      if os.path.isdir(p):
          # recursively scan directories
          for r, dirs, files in os.walk(p):
              files.sort()
              for f in files:
                  if filter(f):
                      add_file(os.path.join(r,f))
      elif os.path.isfile(p):
          add_file(p)
      else:
          print("%s: not a file or a directory, skipped." % p)

  return src_files

xml_filter = lambda x: x.endswith('.xml')
