import os

try:
  DEBUG = bool(os.environ['SCCDDEBUG']=="1")
except KeyError:
  DEBUG = False
def print_debug(msg):
    if DEBUG:
        print(msg)
