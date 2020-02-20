import threading
from sccd.runtime.event_queue import EventQueue
from sccd.runtime.accurate_time import AccurateTime

try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty

try:
    from sccd.runtime.infinity import INFINITY
except ImportError:
    from infinity import INFINITY

class OutputListener(object):
    def __init__(self):
        self.queue = Queue() # queue of lists of event objects

    """ Called at the end of a big step with a list of events.

        Parameters
        ----------
        events: list of Event objects """
    def add_bigstep(self, events):
        self.queue.put_nowait(events)

    """ Fetch next element without blocking.
        If no element is available, None is returned. """
    def fetch_nonblocking(self):
        try:
            return self.queue.get_nowait()
        except Empty:
            return None

    """ Fetch next element from listener, blocking until an element is available.
        If the given timeout is exceeded, None is returned.

        Parameters
        ----------
        timeout: Max time to block (in millisecs). None if allowed to block forever. """
    def fetch_blocking(self, timeout=None):
        try:
            return self.queue.get(True, timeout);
        except Empty:
            return None


# Data class
class InputPortEntry(object):
    def __init__(self, virtual_name, instance):
        self.virtual_name = virtual_name
        self.instance = instance

# Data class
class OutputPortEntry(object):
    def __init__(self, port_name, virtual_name, instance):
        self.port_name = port_name
        self.virtual_name = virtual_name
        self.instance = instance

class ControllerBase(object):
    def __init__(self, object_manager):
    
        self.object_manager = object_manager

        self.private_port_counter = 0

        # keep track of input ports
        self.input_ports = {}
        self.input_queue = EventQueue()

        # keep track of output ports
        self.output_ports = {}
        self.output_listeners = {} # dictionary from port name to list of OutputListener objects
        
        self.simulated_time = None
        self.behind = False
        
        # accurate timer
        self.accurate_time = AccurateTime()
        
    def getSimulatedTime(self):
        return self.simulated_time
        
    def getWallClockTime(self):
        return self.accurate_time.get_wct()
            
    def createInputPort(self, virtual_name, instance = None):
        if instance == None:
            port_name = virtual_name
        else:
            port_name = "private_" + str(self.private_port_counter) + "_" + virtual_name
            self.private_port_counter += 1
        self.input_ports[port_name] = InputPortEntry(virtual_name, instance)
        return port_name
        
    def createOutputPort(self, virtual_name, instance = None):
        if instance == None:
            port_name = virtual_name
        else:
            port_name = "private_" + str(self.private_port_counter) + "_" + virtual_name
            self.private_port_counter += 1
        self.output_ports[port_name] = OutputPortEntry(port_name, virtual_name, instance)
        self.output_listeners[port_name] = []
        return port_name

    def broadcast(self, new_event, time_offset = 0):
        self.object_manager.broadcast(None, new_event, time_offset)
        
    def start(self):
        self.accurate_time.set_start_time()
        self.simulated_time = 0
        self.object_manager.start()
    
    def stop(self):
        pass

    def addInput(self, input_event_list, time_offset = 0, force_internal=False):
        # force_internal is for narrow_cast events, otherwise these would arrive as external events (on the current wall-clock time)
        if not isinstance(input_event_list, list):
            input_event_list = [input_event_list]

        for e in input_event_list:
            if e.getName() == "":
                raise InputException("Input event can't have an empty name.")
        
            if e.getPort() not in self.input_ports:
                raise InputException("Input port mismatch, no such port: " + e.getPort() + ".")
            
            if force_internal:
                self.input_queue.add((0 if self.simulated_time is None else self.simulated_time) + time_offset, e)
            else:
                self.input_queue.add((0 if self.simulated_time is None else self.accurate_time.get_wct()) + time_offset, e)

    def getEarliestEventTime(self):
        return min(self.object_manager.getEarliestEventTime(), self.input_queue.getEarliestTime())

    def handleInput(self):
        while not self.input_queue.isEmpty():
            event_time = self.input_queue.getEarliestTime()
            e = self.input_queue.pop()
            input_port = self.input_ports[e.getPort()]
            # e.port = input_port.virtual_name
            target_instance = input_port.instance
            if target_instance == None:
                self.broadcast(e, event_time - self.simulated_time)
            else:
                target_instance.addEvent(e, event_time - self.simulated_time)

    """
    Called at the end of every big step.

    Parameters
    ----------
    events: dictionary from port name to list of event objects
    """
    def outputBigStep(self, events):
        for port, event_list in events.items():
            for listener in self.output_listeners[port]:
                listener.add_bigstep(event_list)

    def createOutputListener(self, ports):
        listener = OutputListener()
        self.addOutputListener(ports, listener)
        return listener

    def addOutputListener(self, ports, listener):
        if len(ports) == 0:
            # add to all the ports
            for ls in self.output_listeners.values():
                ls.append(listener)
        else:
            for port in ports:
                self.output_listeners[port].append(listener)
            
    def getObjectManager(self):
        return self.object_manager
        
class GameLoopControllerBase(ControllerBase):
    def __init__(self, object_manager):
        ControllerBase.__init__(self, object_manager)
        
    def update(self):
        self.handleInput()
        earliest_event_time = self.getEarliestEventTime()
        if earliest_event_time > time():
            self.simulated_time = earliest_event_time
            self.object_manager.stepAll()

class EventLoop:
    # parameters:
    #  schedule - a callback scheduling another callback in the event loop
    #      this callback should take 2 parameters: (callback, timeout) and return an ID
    #  clear - a callback that clears a scheduled callback
    #      this callback should take an ID that was returned by 'schedule'
    def __init__(self, schedule, clear):
        self.schedule_callback = schedule
        self.clear_callback = clear
        self.scheduled_id = None
        self.last_print = 0.0

    # schedule relative to last_time
    #
    # argument 'wait_time' is the amount of virtual (simulated) time to wait
    #
    # NOTE: if the next wakeup (in simulated time) is in the past, the timeout is '0',
    # but because scheduling '0' timeouts hurts performance, we don't schedule anything
    # and return False instead
    def schedule(self, f, wait_time, behind = False):
        if self.scheduled_id is not None:
            # if the following error occurs, it is probably due to a flaw in the logic of EventLoopControllerBase
            raise RuntimeException("EventLoop class intended to maintain at most 1 scheduled callback.")

        if wait_time != INFINITY:
            self.scheduled_id = self.schedule_callback(f, wait_time, behind)

    def clear(self):
        if self.scheduled_id is not None:
            self.clear_callback(self.scheduled_id)
            self.scheduled_id = None

    def bind_controller(self, controller):
        pass

class EventLoopControllerBase(ControllerBase):
    def __init__(self, object_manager, event_loop, finished_callback = None, behind_schedule_callback = None):
        ControllerBase.__init__(self, object_manager)
        if not isinstance(event_loop, EventLoop):
            raise RuntimeException("Event loop argument must be an instance of the EventLoop class!")
        self.event_loop = event_loop
        self.finished_callback = finished_callback
        self.behind_schedule_callback = behind_schedule_callback
        self.last_print_time = 0
        self.running = False
        self.input_condition = threading.Condition()
        self.behind = False

        self.event_loop.bind_controller(self)
        self.event_queue = []
        self.main_thread = thread.get_ident()

    def addInput(self, input_event, time_offset = 0, force_internal=False):
        # import pdb; pdb.set_trace()
        if self.main_thread == thread.get_ident():
            # Running on the main thread, so just execute what we want
            self.simulated_time = self.accurate_time.get_wct()
            ControllerBase.addInput(self, input_event, time_offset, force_internal)
        else:
            # Not on the main thread, so we have to queue these events for the main thread instead
            self.event_queue.append((input_event, time_offset, force_internal))

        self.event_loop.clear()
        self.event_loop.schedule(self.run, 0, True)

    def start(self):
        ControllerBase.start(self)
        self.run()

    def stop(self):
        self.event_loop.clear()
        ControllerBase.stop(self)

    def run(self, tkinter_event=None):
        start_time = self.accurate_time.get_wct()
        try:
            self.running = True
            # Process external events first
            while 1:
                while self.event_queue:
                    self.addInput(*self.event_queue.pop(0))

                if self.accurate_time.get_wct() >= self.getEarliestEventTime():
                    self.simulated_time = self.getEarliestEventTime()
                else:
                    return

                # clear existing timeout
                self.event_loop.clear()
                self.handleInput()
                self.object_manager.stepAll()
                # schedule next timeout
                earliest_event_time = self.getEarliestEventTime()
                if earliest_event_time == INFINITY:
                    if self.finished_callback: self.finished_callback() # TODO: This is not necessarily correct (keep_running necessary?)
                    return
                now = self.accurate_time.get_wct()
                if earliest_event_time - now > 0:
                    if self.behind:
                        self.behind = False
                    self.event_loop.schedule(self.run, earliest_event_time - now, now - start_time > 10)
                else:
                    if now - earliest_event_time > 10 and now - self.last_print_time >= 1000:
                        if self.behind_schedule_callback:
                            self.behind_schedule_callback(self, now - earliest_event_time)
                        print_debug('\rrunning %ims behind schedule' % (now - earliest_event_time))
                        self.last_print_time = now
                    self.behind = True
                if not self.behind:
                    return
        finally:
            self.running = False
            if self.event_queue:
                self.event_loop.clear()
                self.event_loop.schedule(self.run, 0, True)
        
class ThreadsControllerBase(ControllerBase):
    def __init__(self, object_manager, keep_running, behind_schedule_callback = None):
        ControllerBase.__init__(self, object_manager)
        self.keep_running = keep_running
        self.behind_schedule_callback = behind_schedule_callback
        self.input_condition = threading.Condition()
        self.stop_thread = False
        self.last_print_time = 0

    # may be called from another thread than run
    def addInput(self, input_event, time_offset = 0, force_internal=False):
        with self.input_condition:
            ControllerBase.addInput(self, input_event, time_offset, force_internal)
            self.input_condition.notifyAll()
        
    def start(self):
        self.run()
    
    # may be called from another thread than run
    def stop(self):
        with self.input_condition:
            self.stop_thread = True
            self.input_condition.notifyAll()

    def run(self):
        ControllerBase.start(self)
        
        while 1:
            # simulate
            with self.input_condition:
                self.handleInput()
            self.object_manager.stepAll()
            
            # wait until next timeout
            earliest_event_time = self.getEarliestEventTime()
            if earliest_event_time == INFINITY and not self.keep_running:
                return
            now = self.accurate_time.get_wct()
            if earliest_event_time - now > 0:
                if self.behind:                
                    self.behind = False
                with self.input_condition:
                    if earliest_event_time == self.getEarliestEventTime() and not earliest_event_time == INFINITY:
                        self.input_condition.wait((earliest_event_time - now) / 1000.0)
                    else:
                        # Something happened that made the queue fill up already, but we were not yet waiting for the Condition...
                        pass
            else:
                if now - earliest_event_time > 10 and now - self.last_print_time >= 1000:
                    if self.behind_schedule_callback:
                        self.behind_schedule_callback(self, now - earliest_event_time)
                    print_debug('\rrunning %ims behind schedule' % (now - earliest_event_time))
                    self.last_print_time = now
                    self.behind = True
            with self.input_condition:
                earliest_event_time = self.getEarliestEventTime()
                if earliest_event_time == INFINITY:
                    if self.keep_running:
                        self.input_condition.wait()
                        earliest_event_time = self.getEarliestEventTime()
                    else:
                        self.stop_thread = True
                if self.stop_thread:
                    break
                self.simulated_time = earliest_event_time
