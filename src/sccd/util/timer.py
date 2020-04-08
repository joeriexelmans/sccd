import os

try:
  TIMINGS = bool(os.environ['SCCDTIMINGS']=="1")
except KeyError:
  TIMINGS = False

if TIMINGS:
  import time
  import atexit
  import collections

  timers = {}
  timings = {}
  counts = collections.Counter()
    
  def start(what):
    timers[what] = time.perf_counter()

  def stop(what):
    end = time.perf_counter()
    begin = timers[what]
    duration = end - begin
    old_val = timings.setdefault(what, 0)
    timings[what] = old_val + duration
    counts[what] += 1

  def _print_stats():
      print("\ntimings:")
      for key,val in timings.items():
        print("  %s: %.2f ms / %d = %.2f ms" % (key,val*1000,counts[key],val*1000/counts[key]))

  atexit.register(_print_stats)

else:
  def start(what):
    pass

  def stop(what):
    pass