import os

try:
  DEBUG = os.environ['SCCDDEBUG']
except KeyError:
  DEBUG = False
def print_debug(msg):
    if DEBUG:
        print(msg)
