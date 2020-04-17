import os

try:
  TIMINGS = bool(os.environ['SCCDTIMINGS']=="1")
except KeyError:
  TIMINGS = False

if TIMINGS:
  from typing import Dict, Tuple
  import time
  import atexit
  import collections

  timings: Dict[str, Tuple[float, int]] = {}

  class Context:
    __slots__ = ["what", "started"]
    def __init__(self, what):
      self.what = what
    def __enter__(self):
      self.started = time.perf_counter()
    def __exit__(self, type, value, traceback):
      duration = time.perf_counter() - self.started
      old_val, old_count = timings.setdefault(self.what, (0, 0))
      timings[self.what] = (old_val + duration, old_count + 1)

  def _print_stats():
      print("\ntimings:")
      for key, (val,count) in sorted(timings.items()):
        print("  %s: %.2f ms / %d = %.3f ms" % (key,val*1000,count,val*1000/count))

  atexit.register(_print_stats)

else:
  class Context:
    __slots__ = []
    def __init__(self, what):
      pass
    def __enter__(self):
      pass
    def __exit__(self, type, value, traceback):
      pass
