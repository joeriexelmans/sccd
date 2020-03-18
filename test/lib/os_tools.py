import os
from typing import List, Callable, Set

filter_any = lambda x: True
filter_xml = lambda x: x.endswith('.xml')

# For a given list of files and or directories,
# recursively find all the files that adhere to an optional filename filter,
# merge the results while eliminating duplicates.
def get_files(paths: List[str], filter: Callable[[str], bool] = filter_any) -> List[str]:
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

# Drop file extension
def dropext(file):
    return os.path.splitext(file)[0]

# Ensure path of directories exists
def make_dirs(file):
    os.makedirs(os.path.dirname(file), exist_ok=True)
