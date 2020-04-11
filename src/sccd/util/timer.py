import os

try:
  TIMINGS = bool(os.environ['SCCDTIMINGS']=="1")
except KeyError:
  TIMINGS = False

if TIMINGS:
  import time
  import atexit
  import collections

  timings = {}
  counts = collections.Counter()

  class Context:
    __slots__ = ["what", "started"]
    def __init__(self, what):
      self.what = what
    def __enter__(self):
      self.started = time.perf_counter()
    def __exit__(self, type, value, traceback):
      duration = time.perf_counter() - self.started
      old_val = timings.setdefault(self.what, 0)
      timings[self.what] = old_val + duration
      counts[self.what] += 1

  def _print_stats():
      print("\ntimings:")
      for key,val in timings.items():
        print("  %s: %.2f ms / %d = %.3f ms" % (key,val*1000,counts[key],val*1000/counts[key]))

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
