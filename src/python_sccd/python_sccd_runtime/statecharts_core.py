import abc
import re
import threading
import traceback
import math
from infinity import INFINITY
from Queue import Queue, Empty

from sccd.runtime.event_queue import EventQueue
from sccd.runtime.accurate_time import time

global simulated_time
simulated_time = 0.0
def get_simulated_time():
    global simulated_time
    return simulated_time

class RuntimeException(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

class AssociationException(RuntimeException):
    pass

class AssociationReferenceException(RuntimeException):
    pass

class ParameterException(RuntimeException):
    pass

class InputException(RuntimeException):
    pass

class Association(object):
    # wrapper object for one association relation
    def __init__(self, to_class, min_card, max_card):
        self.to_class = to_class
        self.min_card = min_card
        self.max_card = max_card
        self.instances = {} # maps index (as string) to instance
        self.instances_to_ids = {}
        self.size = 0
        self.next_id = 0
        

    def allowedToAdd(self):
        return self.max_card == -1 or self.size < self.max_card
        
    def allowedToRemove(self):
        return self.min_card == -1 or self.size > self.min_card
        
    def addInstance(self, instance):
        if self.allowedToAdd() :
            new_id = self.next_id
            self.next_id += 1
            self.instances[new_id] = instance
            self.instances_to_ids[instance] = new_id
            self.size += 1
            return new_id
        else :
            raise AssociationException("Not allowed to add the instance to the association.")
        
    def removeInstance(self, instance):
        if self.allowedToRemove() :
            del self.instances[self.instances_to_ids[instance]]
            del self.instances_to_ids[instance]
            self.size -= 1
        else :
            raise AssociationException("Not allowed to remove the instance from the association.")
        
    def getInstance(self, index):
        try :
            return self.instances[index]
        except IndexError :
            raise AssociationException("Invalid index for fetching instance(s) from association.")

# TODO: Clean this mess up. Look at all object management operations and see how they can be improved.
class ObjectManagerBase(object):
    __metaclass__  = abc.ABCMeta
    
    def __init__(self, controller):
        self.controller = controller
        self.events = EventQueue()
        self.instances = set() # a set of RuntimeClassBase instances
        
    def addEvent(self, event, time_offset = 0.0):
        self.events.add((simulated_time + time_offset, event))
        
    # broadcast an event to all instances
    def broadcast(self, new_event, time_offset = 0.0):
        for i in self.instances:
            i.addEvent(new_event, time_offset)
        
    def getEarliestEventTime(self):
        earliest_time = self.events.getEarliestTime()
        if self.instances:
            for i in self.instances:
                if i.earliest_event_time < earliest_time:
                    earliest_time = i.earliest_event_time
        return earliest_time
    
    def stepAll(self):
        self.step()
        for i in self.instances:
            if i.active:
                i.step()

    def step(self):
        while self.events.getEarliestTime() <= time():
            self.handleEvent(self.events.pop())
               
    def start(self):
        for i in self.instances:
            i.start()          
               
    def handleEvent(self, e):   
        if e.getName() == "narrow_cast" :
            self.handleNarrowCastEvent(e.getParameters())            
        elif e.getName() == "broad_cast" :
            self.handleBroadCastEvent(e.getParameters())            
        elif e.getName() == "create_instance" :
            self.handleCreateEvent(e.getParameters())            
        elif e.getName() == "associate_instance" :
            self.handleAssociateEvent(e.getParameters())            
        elif e.getName() == "start_instance" :
            self.handleStartInstanceEvent(e.getParameters())            
        elif e.getName() == "delete_instance" :
            self.handleDeleteInstanceEvent(e.getParameters())
            
    def processAssociationReference(self, input_string):
        if len(input_string) == 0 :
            raise AssociationReferenceException("Empty association reference.")
        regex_pattern = re.compile("^([a-zA-Z_]\w*)(?:\[(\d+)\])?$")
        path_string =  input_string.split("/")
        result = []
        for piece in path_string :
            match = regex_pattern.match(piece)
            if match :
                name = match.group(1)
                index = match.group(2)
                if index is None :
                    index = -1
                result.append((name,int(index)))
            else :
                raise AssociationReferenceException("Invalid entry in association reference. Input string: " + input_string)
        return result
    
    def handleStartInstanceEvent(self, parameters):
        if len(parameters) != 2 :
            raise ParameterException ("The start instance event needs 2 parameters.")  
        else :
            source = parameters[0]
            traversal_list = self.processAssociationReference(parameters[1])
            for i in self.getInstances(source, traversal_list) :
                i["instance"].start()
            source.addEvent(Event("instance_started", parameters = [parameters[1]]))
        
    def handleBroadCastEvent(self, parameters):
        if len(parameters) != 1 :
            raise ParameterException ("The broadcast event needs 1 parameter.")
        self.broadcast(parameters[0])

    def handleCreateEvent(self, parameters):
        if len(parameters) < 2 :
            raise ParameterException ("The create event needs at least 2 parameters.")

        source = parameters[0]
        association_name = parameters[1]
        
        association = source.associations[association_name]
        #association = self.instances_map[source].getAssociation(association_name)
        if association.allowedToAdd() :
            ''' allow subclasses to be instantiated '''
            class_name = association.to_class if len(parameters) == 2 else parameters[2]
            new_instance = self.createInstance(class_name, parameters[3:])
            if not new_instance:
                raise ParameterException("Creating instance: no such class: " + class_name)
            #index = association.addInstance(new_instance)
            try:
                index = association.addInstance(new_instance)
            except AssociationException as exception:
                raise RuntimeException("Error adding instance to association '" + association_name + "': " + str(exception))
            p = new_instance.associations.get("parent")
            if p:
                p.addInstance(source)
            source.addEvent(Event("instance_created", None, [association_name+"["+str(index)+"]"]))
        else :
            source.addEvent(Event("instance_creation_error", None, [association_name]))

    def handleDeleteInstanceEvent(self, parameters):
        if len(parameters) < 2 :
            raise ParameterException ("The delete event needs at least 2 parameters.")
        else :
            source = parameters[0]
            association_name = parameters[1]
            traversal_list = self.processAssociationReference(association_name)
            instances = self.getInstances(source, traversal_list)
            #association = self.instances_map[source].getAssociation(traversal_list[0][0])
            association = source.associations[traversal_list[0][0]]
            for i in instances:
                try:
                    association.removeInstance(i["instance"])
                    self.instances.discard(i["instance"])
                except AssociationException as exception:
                    raise RuntimeException("Error removing instance from association '" + association_name + "': " + str(exception))
                i["instance"].stop()
                #if hasattr(i.instance, 'user_defined_destructor'):
                i["instance"].user_defined_destructor()
            source.addEvent(Event("instance_deleted", parameters = [parameters[1]]))
                
    def handleAssociateEvent(self, parameters):
        if len(parameters) != 3 :
            raise ParameterException ("The associate_instance event needs 3 parameters.")
        else :
            source = parameters[0]
            to_copy_list = self.getInstances(source,self.processAssociationReference(parameters[1]))
            if len(to_copy_list) != 1 :
                raise AssociationReferenceException ("Invalid source association reference.")
            wrapped_to_copy_instance = to_copy_list[0]["instance"]
            dest_list = self.processAssociationReference(parameters[2])
            if len(dest_list) == 0 :
                raise AssociationReferenceException ("Invalid destination association reference.")
            last = dest_list.pop()
            if last[1] != -1 :
                raise AssociationReferenceException ("Last association name in association reference should not be accompanied by an index.")
                
            for i in self.getInstances(source, dest_list) :
                i["instance"].associations[last[0]].addInstance(wrapped_to_copy_instance)
        
    def handleNarrowCastEvent(self, parameters):
        if len(parameters) != 3 :
            raise ParameterException ("The associate_instance event needs 3 parameters.")
        source = parameters[0]
        traversal_list = self.processAssociationReference(parameters[1])
        cast_event = parameters[2]
        for i in self.getInstances(source, traversal_list) :
            i["instance"].addEvent(cast_event)
        
    def getInstances(self, source, traversal_list):
        currents = [{
            "instance" : source,
            "ref" : None,
            "assoc_name" : None,
            "assoc_index" : None
        }]
        #currents = [source]
        for (name, index) in traversal_list :
            nexts = []
            for current in currents :
                association = current["instance"].associations[name]
                if (index >= 0 ) :
                    nexts.append({
                        "instance" : association.instances[index],
                        "ref" : current["instance"],
                        "assoc_name" : name,
                        "assoc_index" : index
                    })
                elif (index == -1) :
                    for i in association.instances:
                        nexts.append({
                            "instance" : association.instances[i],
                            "ref" : current["instance"],
                            "assoc_name" : name,
                            "assoc_index" : index
                        })
                    #nexts.extend( association.instances.values() )
                else :
                    raise AssociationReferenceException("Incorrect index in association reference.")
            currents = nexts
        return currents
            
    @abc.abstractmethod
    def instantiate(self, class_name, construct_params):
        pass
        
    def createInstance(self, to_class, construct_params = []):
        instance = self.instantiate(to_class, construct_params)
        self.instances.add(instance)
        return instance
    
class Event(object):
    def __init__(self, event_name, port = "", parameters = []):
        self.name = event_name
        self.parameters = parameters
        self.port = port

    def getName(self):
        return self.name

    def getPort(self):
        return self.port

    def getParameters(self):
        return self.parameters
    
    def __repr__(self):
        representation = "(event name : " + str(self.name) + "; port : " + str(self.port)
        if self.parameters :
            representation += "; parameters : " + str(self.parameters)
        representation += ")"
        return representation
    
class OutputListener(object):
    def __init__(self, port_names):
        self.port_names = port_names
        self.queue = Queue()

    def add(self, event):
        if len(self.port_names) == 0 or event.getPort() in self.port_names :
            self.queue.put_nowait(event)
            
    """ Tries for timeout seconds to fetch an event, returns None if failed.
        0 as timeout means no waiting (blocking), returns None if queue is empty.
        -1 as timeout means blocking until an event can be fetched. """
    def fetch(self, timeout = 0):
        if timeout < 0:
            timeout = INFINITY
        while timeout >= 0:
            try:
                # wait in chunks of 100ms because we
                # can't receive (keyboard)interrupts while waiting
                return self.queue.get(True, 0.1 if timeout > 0.1 else timeout)
            except Empty:
                timeout -= 0.1
        return None

class InputPortEntry(object):
    def __init__(self, virtual_name, instance):
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
        self.output_ports = []
        self.output_listeners = []
        
        self.started = False
            
    def addInputPort(self, virtual_name, instance = None):
        if instance == None :
            port_name = virtual_name
        else:
            port_name = "private_" + str(self.private_port_counter) + "_" + virtual_name
            self.private_port_counter += 1
        self.input_ports[port_name] = InputPortEntry(virtual_name, instance)
        return port_name
        
    def addOutputPort(self, port_name):
        self.output_ports.append(port_name)

    def broadcast(self, new_event, time_offset = 0.0):
        self.object_manager.broadcast(new_event, time_offset)
        
    def start(self):
        self.started = True
        self.object_manager.start()
    
    def stop(self):
        pass

    def addInput(self, input_event_list, time_offset = 0.0):
        if not isinstance(input_event_list, list):
            input_event_list = [input_event_list]

        for e in input_event_list:
            if e.getName() == ""  :
                raise InputException("Input event can't have an empty name.")
        
            if e.getPort() not in self.input_ports :
                raise InputException("Input port mismatch, no such port: " + e.getPort() + ".")
            
            self.input_queue.add((time() + time_offset, e))

    def getEarliestEventTime(self):
        return min(self.object_manager.getEarliestEventTime(), self.input_queue.getEarliestTime())

    def handleInput(self):
        while not self.input_queue.isEmpty():
            event_time = self.input_queue.getEarliestTime()
            e = self.input_queue.pop()
            input_port = self.input_ports[e.getPort()]
            e.port = input_port.virtual_name
            target_instance = input_port.instance
            if target_instance == None:
                self.broadcast(e, event_time - simulated_time)
            else:
                target_instance.addEvent(e, event_time - simulated_time)

    def outputEvent(self, event):
        for listener in self.output_listeners :
            listener.add(event)

    def addOutputListener(self, ports):
        listener = OutputListener(ports)
        self.output_listeners.append(listener)
        return listener

    def addMyOwnOutputListener(self, listener):
        self.output_listeners.append(listener)
            
    def getObjectManager(self):
        return self.object_manager
        
class GameLoopControllerBase(ControllerBase):
    def __init__(self, object_manager):
        ControllerBase.__init__(self, object_manager)
        
    def update(self):
        self.handleInput()
        earliest_event_time = self.getEarliestEventTime()
        if earliest_event_time > time():
            global simulated_time
            simulated_time = earliest_event_time
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
        if self.scheduled_id:
            # if the following error occurs, it is probably due to a flaw in the logic of EventLoopControllerBase
            raise RuntimeException("EventLoop class intended to maintain at most 1 scheduled callback.")

        if wait_time != INFINITY:
            self.scheduled_id = self.schedule_callback(f, wait_time, behind)

    def clear(self):
        if self.scheduled_id:
            self.clear_callback(self.scheduled_id)
            self.scheduled_id = None

class EventLoopControllerBase(ControllerBase):
    def __init__(self, object_manager, event_loop, finished_callback = None):
        ControllerBase.__init__(self, object_manager)
        self.event_loop = event_loop
        self.finished_callback = finished_callback
        self.last_print_time = 0.0
        self.behind = False

    def addInput(self, input_event, time_offset = 0.0):
        ControllerBase.addInput(self, input_event, time_offset)
        self.event_loop.clear()
        global simulated_time
        simulated_time = self.getEarliestEventTime()
        self.run()

    def start(self):
        ControllerBase.start(self)
        self.run()

    def stop(self):
        self.event_loop.clear()
        ControllerBase.stop(self)

    def run(self):
        global simulated_time
        start_time = time()
        while 1:
            # clear existing timeout
            self.event_loop.clear()
            # simulate
            self.handleInput()
            self.object_manager.stepAll()
            # schedule next timeout
            earliest_event_time = self.getEarliestEventTime()
            if earliest_event_time == INFINITY:
                if self.finished_callback: self.finished_callback() # TODO: This is not necessarily correct (keep_running necessary?)
                return
            now = time()
            if now - start_time > 0.01 or earliest_event_time - now > 0.0:
                self.event_loop.schedule(self.run, earliest_event_time - now, now - start_time > 0.01)
                if now - earliest_event_time > 0.1 and now - self.last_print_time >= 1:
                    print '\rrunning %ims behind schedule' % ((now - earliest_event_time) * 1000),
                    self.last_print_time = now
                    self.behind = True
                elif now - earliest_event_time < 0.1 and self.behind:
                    print '\r' + ' ' * 80,
                    self.behind = False
                simulated_time = earliest_event_time
                return
            else:
                simulated_time = earliest_event_time
        
class ThreadsControllerBase(ControllerBase):
    def __init__(self, object_manager, keep_running):
        ControllerBase.__init__(self, object_manager)
        self.keep_running = keep_running
        self.input_condition = threading.Condition()
        self.stop_thread = False

    def addInput(self, input_event, time_offset = 0.0):
        with self.input_condition:
            ControllerBase.addInput(self, input_event, time_offset)
            self.input_condition.notifyAll()
        
    def start(self):
        self.run()
        
    def stop(self):
        with self.input_condition:
            self.stop_thread = True
            self.input_condition.notifyAll()
        
    def join(self):
        self.thread.join()

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
            with self.input_condition:
                self.input_condition.wait(earliest_event_time - time())
            earliest_event_time = self.getEarliestEventTime()
            if earliest_event_time == INFINITY:
                if self.keep_running:
                    with self.input_condition:
                        self.input_condition.wait()
                else:
                    self.stop_thread = True
            if self.stop_thread:
                break
            earliest_event_time = self.getEarliestEventTime()
            global simulated_time
            simulated_time = earliest_event_time

class StatechartSemantics:
    # Big Step Maximality
    TakeOne = 0
    TakeMany = 1
    # Concurrency - not implemented yet
    Single = 0
    Many = 1
    # Preemption - not implemented yet
    NonPreemptive = 0
    Preemptive = 1
    # Internal Event Lifeline
    Queue = 0
    NextSmallStep = 1
    NextComboStep = 2
    # Input Event Lifeline
    Whole = 0
    FirstSmallStep = 1
    FirstComboStep = 2
    # Priority
    SourceParent = 0
    SourceChild = 1
    # TODO: add Memory Protocol options
    
    def __init__(self):
        # default semantics:
        self.big_step_maximality = self.TakeMany
        self.internal_event_lifeline = self.Queue
        self.input_event_lifeline = self.FirstComboStep
        self.priority = self.SourceParent
        self.concurrency = self.Single

class State:
    def __init__(self, state_id, obj):
        self.state_id = state_id
        self.obj = obj
        
        self.ancestors = []
        self.descendants = []
        self.children = []
        self.parent = None
        self.enter = None
        self.exit = None
        self.default_state = None
        self.transitions = []
        self.history = []
        
    def getEffectiveTargetStates(self):
        targets = [self]
        if self.default_state:
            targets.extend(self.default_state.getEffectiveTargetStates())
        return targets
        
    def fixTree(self):
        for c in self.children:
            if isinstance(c, HistoryState):
                self.history.append(c)
            c.parent = self
            c.ancestors.append(self)
            c.ancestors.extend(self.ancestors)
            c.fixTree()
        self.descendants.extend(self.children)
        for c in self.children:
            self.descendants.extend(c.descendants)
            
    def addChild(self, child):
        self.children.append(child)
    
    def addTransition(self, transition):
        self.transitions.append(transition)
        
    def setEnter(self, enter):
        self.enter = enter
        
    def setExit(self, exit):
        self.exit = exit
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.state_id == other.state_id
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return self.state_id
        
    def __repr__(self):
        return "State(%i)" % self.state_id
        
class HistoryState(State):
    def __init__(self, state_id, obj):
        State.__init__(self, state_id, obj)
        
class ShallowHistoryState(HistoryState):
    def __init__(self, state_id, obj):
        HistoryState.__init__(self, state_id, obj)
        
    def getEffectiveTargetStates(self):
        if self.state_id in self.obj.history_values:
            targets = []
            for hv in self.obj.history_values[self.state_id]:
                targets.extend(hv.getEffectiveTargetStates())
            return targets
        else:
            # TODO: is it correct that in this case, the parent itself is also entered?
            return self.parent.getEffectiveTargetStates()
        
class DeepHistoryState(HistoryState):
    def __init__(self, state_id, obj):
        HistoryState.__init__(self, state_id, obj)
        
    def getEffectiveTargetStates(self):
        if self.state_id in self.obj.history_values:
            return self.obj.history_values[self.state_id]
        else:
            # TODO: is it correct that in this case, the parent itself is also entered?
            return self.parent.getEffectiveTargetStates()
        
class ParallelState(State):
    def __init__(self, state_id, obj):
        State.__init__(self, state_id, obj)
        
    def getEffectiveTargetStates(self):
        targets = [self]
        for c in self.children:
            if not isinstance(c, HistoryState):
                targets.extend(c.getEffectiveTargetStates())
        return targets
    
class Transition:
    def __init__(self, obj, source, targets):
        self.guard = None
        self.action = None
        self.trigger = None
        self.source = source
        self.targets = targets
        self.obj = obj
        self.enabled_event = None # the event that enabled this transition
    
    def isEnabled(self, events):
        if self.trigger is None:
            self.enabled_event = None
            return (self.guard is None) or self.guard([])
        else:
            for event in events:
                if ((self.trigger is None) or (self.trigger.name == event.name and self.trigger.port == event.port)) and ((self.guard is None) or self.guard(event.parameters)):
                    self.enabled_event = event
                    return True
    
    def fire(self):
        # exit states...
        targets = self.__getEffectiveTargetStates()
        exit_set = self.__exitSet(targets)
        for s in exit_set:
            # remember which state(s) we were in if a history state is present
            for h in s.history:
                f = lambda s0: s0.ancestors and s0.parent == s
                if isinstance(h, DeepHistoryState):
                    f = lambda s0: not s0.descendants and s0 in s.descendants
                self.obj.history_values[h.state_id] = filter(f, self.obj.configuration)
        for s in exit_set:
            # execute exit action(s)
            if s.exit:
                s.exit()
            self.obj.configuration.remove(s)
        
        # combo state changed area
        self.obj.combo_step.changed.add(self.lca)
        self.obj.combo_step.changed.update(self.lca.descendants)
        
        # execute transition action(s)
        if self.action:
            self.action(self.enabled_event.parameters if self.enabled_event else [])
            
        # enter states...
        enter_set = self.__enterSet(targets)
        for s in enter_set:
            self.obj.configuration.append(s)
            # execute enter action(s)
            if s.enter:
                s.enter()
                
        self.obj.configuration.sort(key=lambda x: x.state_id)
        self.enabled_event = None
    
    def __getEffectiveTargetStates(self):
        targets = []
        for target in self.targets:
            for e_t in target.getEffectiveTargetStates():
                if not e_t in targets:
                    targets.append(e_t)
        return targets
    
    def __exitSet(self, targets):
        target = targets[0]
        self.lca = self.source.parent
        if self.source.parent != target.parent: # external
            for a in self.source.ancestors:
                if a in target.ancestors:
                    self.lca = a
                    break
        return [s for s in reversed(self.lca.descendants) if (s in self.obj.configuration)]
    
    def __enterSet(self, targets):
        target = targets[0]
        for a in reversed(target.ancestors):
            if a in self.source.ancestors:
                continue
            else:
                yield a
        for target in targets:
            yield target
    
    def conflicts(self, transition):
        return self.__exitSet() & transition.__exitSet()
        
    def setGuard(self, guard):
        self.guard = guard
        
    def setAction(self, action):
        self.action = action
        
    def __repr__(self):
        return "Transition(%i, %s)" % (self.source.state_id, [target.state_id for target in self.targets])

class RuntimeClassBase(object):
    __metaclass__  = abc.ABCMeta
    
    def __init__(self, controller):
        self.active = False
        self.__set_stable(True)
        self.events = EventQueue()

        self.controller = controller
        self.inports = {}
        self.timers = {}
        self.states = {}

        self.semantics = StatechartSemantics()

    def start(self):
        self.configuration = []
        
        self.current_state = {}
        self.history_values = {}
        self.timers = {}

        self.big_step = BigStepState()
        self.combo_step = ComboStepState()
        self.small_step = SmallStepState()

        self.active = True
        self.__set_stable(False)

        self.initializeStatechart()
        self.processBigStepOutput()
    
    def updateConfiguration(self, states):
        self.configuration.extend(states)
    
    def stop(self):
        self.active = False
        self.__set_stable(True)
    
    def addTimer(self, index, timeout):
        self.timers[index] = self.events.add((simulated_time + timeout, Event("_%iafter" % index)))
    
    def removeTimer(self, index):
        self.events.remove(self.timers[index])
        del self.timers[index]
        
    def addEvent(self, event_list, time_offset = 0.0):
        event_time = simulated_time + time_offset
        if event_time < self.earliest_event_time:
            self.earliest_event_time = event_time
        if not isinstance(event_list, list):
            event_list = [event_list]
        for e in event_list:
            self.events.add((event_time, e))
        
    def getEarliestEventTime(self):
        return self.earliest_event_time

    def processBigStepOutput(self):
        for e in self.big_step.output_events_port:
            self.controller.outputEvent(e)
        for e in self.big_step.output_events_om:
            self.controller.object_manager.addEvent(e)
            
    def __set_stable(self, is_stable):
        self.is_stable = is_stable
        # self.earliest_event_time keeps track of the earliest time this instance will execute a transition
        if not is_stable:
            self.earliest_event_time = 0.0
        elif not self.active:
            self.earliest_event_time = INFINITY
        else:
            self.earliest_event_time = self.events.getEarliestTime()

    def step(self):        
        is_stable = False
        while not is_stable:
            due = []
            if self.events.getEarliestTime() <= simulated_time:
                due = [self.events.pop()]
            is_stable = not self.bigStep(due)
            self.processBigStepOutput()
        self.__set_stable(True)

    def inState(self, state_strings):
        state_ids = [self.states[state_string].state_id for state_string in state_strings]
        for state_id in state_ids:
            found = False
            for s in self.configuration:
                if s.state_id == state_id:
                    found = True
                    break
            if not found:
                return False
        return True

    def bigStep(self, input_events):
        self.big_step.next(input_events)
        self.small_step.reset()
        self.combo_step.reset()
        while self.comboStep():
            self.big_step.has_stepped = True
            if self.semantics.big_step_maximality == StatechartSemantics.TakeOne:
                break # Take One -> only one combo step allowed
        return self.big_step.has_stepped

    def comboStep(self):
        self.combo_step.next()
        while self.smallStep():
            self.combo_step.has_stepped = True
        return self.combo_step.has_stepped
	
    # generate transition candidates for current small step
    def generateCandidates(self):
        enabledEvents = self.getEnabledEvents()
        enabledTransitions = []
        for s in self.configuration:
            if not (s in self.combo_step.changed):
                for t in s.transitions:
                    if t.isEnabled(enabledEvents):
                        enabledTransitions.append(t)
        return enabledTransitions

    def smallStep(self):        
        def __younger_than(x, y):
            if x.source in y.source.ancestors:
                return 1
            elif y.source in x.source.ancestors:
                return -1
            else:
                raise Exception('These items have no relation with each other.')
                
        if self.small_step.has_stepped:
            self.small_step.next()
        candidates = self.generateCandidates()
        if candidates:
            to_skip = set()
            conflicting = []
            for c1 in candidates:
                if c1 not in to_skip:
                    conflict = [c1]
                    for c2 in candidates[candidates.index(c1):]:
                        if c2.source in c1.source.ancestors or c1.source in c2.source.ancestors:
                            conflict.append(c2)
                            to_skip.add(c2)
                    conflicting.append(sorted(conflict, cmp=__younger_than))
            if self.semantics.concurrency == StatechartSemantics.Single:
                candidate = conflicting[0]
                if self.semantics.priority == StatechartSemantics.SourceParent:
                    candidate[-1].fire()
                else:
                    candidate[0].fire()
            elif self.semantics.concurrency == StatechartSemantics.Many:
                pass # TODO: implement
            self.small_step.has_stepped = True
        return self.small_step.has_stepped

    def getEnabledEvents(self):
        result = self.small_step.current_events + self.combo_step.current_events
        if self.semantics.input_event_lifeline == StatechartSemantics.Whole or (
            not self.big_step.has_stepped and
                (self.semantics.input_event_lifeline == StatechartSemantics.FirstComboStep or (
                not self.combo_step.has_stepped and
                    self.semantics.input_event_lifeline == StatechartSemantics.FirstSmallStep))):
            result += self.big_step.input_events
        return result

    def raiseInternalEvent(self, event):
        if self.semantics.internal_event_lifeline == StatechartSemantics.NextSmallStep:
            self.small_step.addNextEvent(event)
        elif self.semantics.internal_event_lifeline == StatechartSemantics.NextComboStep:
            self.combo_step.addNextEvent(event)
        elif self.semantics.internal_event_lifeline == StatechartSemantics.Queue:
            self.events.add((time(), event))

    @abc.abstractmethod
    def initializeStatechart(self):
        pass
        

class BigStepState(object):
    def __init__(self):
        self.input_events = [] # input events received from environment before beginning of big step (e.g. from object manager, from input port)
        self.output_events_port = [] # output events to be sent to output port after big step ends.
        self.output_events_om = [] # output events to be sent to object manager after big step ends.
        self.has_stepped = True

    def next(self, input_events):
        self.input_events = input_events
        self.output_events_port = []
        self.output_events_om = []
        self.has_stepped = False

    def outputEvent(self, event):
        self.output_events_port.append(event)

    def outputEventOM(self, event):
        self.output_events_om.append(event)


class ComboStepState(object):
    def __init__(self):
        self.current_events = [] # set of enabled events during combo step
        self.next_events = [] # internal events that were raised during combo step
        self.changed = set() # set of all or-states that were the arena of a triggered transition during big step.
        self.has_stepped = True

    def reset(self):
        self.current_events = []
        self.next_events = []

    def next(self):
        self.current_events = self.next_events
        self.next_events = []
        self.changed = set()
        self.has_stepped = False

    def addNextEvent(self, event):
        self.next_events.append(event)

    def setArenaChanged(self, arena):
        self.changed.add(arena)

    def isArenaChanged(self, arena):
        return (arena in self.changed)

    def isStable(self):
        return (len(self.changed) == 0)


class SmallStepState(object):
    def __init__(self):
        self.current_events = [] # set of enabled events during small step
        self.next_events = [] # events to become 'current' in the next small step
        self.candidates = [] # document-ordered(!) list of transitions that can potentially be executed concurrently, or preempt each other, depending on concurrency semantics. If no concurrency is used and there are multiple candidates, the first one is chosen. Source states of candidates are *always* orthogonal to each other.
        self.has_stepped = True

    def reset(self):
        self.current_events = []
        self.next_events = []

    def next(self):
        self.current_events = self.next_events # raised events from previous small step
        self.next_events = []
        self.candidates = []
        self.has_stepped = False

    def addNextEvent(self, event):
        self.next_events.append(event)

    def addCandidate(self, t, p):
        self.candidates.append((t, p))

    def hasCandidates(self):
        return len(self.candidates) > 0

