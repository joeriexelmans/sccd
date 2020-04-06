import os

try:
  TIMINGS = bool(os.environ['SCCDTIMINGS']=="1")
except KeyError:
  TIMINGS = False

if TIMINGS:
  import time
  import atexit

  timings = {}

  timers = {}

  def start(what):
    timers[what] = time.time()

  def stop(what):
    end = time.time()
    begin = timers[what]
    del timers[what]
    duration = end - begin
    old_val = timings.setdefault(what, 0)
    timings[what] = old_val + duration

  def _print_stats():
      print("timings:")
      for key,val in timings.items():
        print("  %s: %f ms" % (key,val*1000))

  atexit.register(_print_stats)
else:
  def start(what):
    pass

  def stop(what):
    pass