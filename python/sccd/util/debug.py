import os

try:
  DEBUG = bool(os.environ['SCCDDEBUG']=="1")
except KeyError:
  DEBUG = False
  
if DEBUG:
  def print_debug(msg):
    print(msg)
else:
  def print_debug(msg):
    pass