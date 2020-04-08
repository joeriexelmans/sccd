# Statechart compiler by Glenn De Jonghe
#
# Date:   Mon Aug 17 14:45:55 2015

# Model author: Simon Van Mierlo+Joeri Exelmans+Raphael Mannadiar
# Model name:   Bouncing_Balls
# Model description:
"""
	Tkinter frame with bouncing balls in it.
"""

from python_runtime.statecharts_core import ObjectManagerBase, Event, InstanceWrapper, RuntimeClassBase, Association
from python_runtime.libs.ui import *
from python_runtime.libs.utils import *


class Button(RuntimeClassBase):

	# Unique IDs for all statechart nodes
	Root = 0
	Root_initializing = 1
	Root_running = 2

	def commonConstructor(self, controller = None):
		"""Constructor part that is common for all constructors."""
		RuntimeClassBase.__init__(self)

		# User defined input ports
		self.inports = {}
		self.controller = controller
		self.object_manager = controller.getObjectManager()
		self.current_state = {}
		self.history_state = {}

		#Initialize statechart :

		self.current_state[self.Root] = []

	def start(self):
		super(Button, self).start()
		self.enter_Root_initializing()

	#The actual constructor
	def __init__(self, controller, parent, event_name, button_text):
		self.commonConstructor(controller)

		#constructor body (user-defined)
		self.event_name = event_name
		button = ui.append_button(parent.field_window, event_name)
		ui.bind_event(button.element, ui.EVENTS.MOUSE_CLICK, self.controller, 'mouse_click')

	# Statechart enter/exit action method(s) :

	def enter_Root_initializing(self):
		self.current_state[self.Root].append(self.Root_initializing)

	def exit_Root_initializing(self):
		self.current_state[self.Root] = []

	def enter_Root_running(self):
		self.current_state[self.Root].append(self.Root_running)

	def exit_Root_running(self):
		self.current_state[self.Root] = []

	#Statechart transitions :

	def transition_Root(self, event) :
		catched = False
		if not catched :
			if self.current_state[self.Root][0] == self.Root_initializing:
				catched = self.transition_Root_initializing(event)
			elif self.current_state[self.Root][0] == self.Root_running:
				catched = self.transition_Root_running(event)
		return catched

	def transition_Root_initializing(self, event) :
		catched = False
		enableds = []
		enableds.append(1)

		if len(enableds) > 1 :
			print "Runtime warning : indeterminism detected in a transition from node Root_initializing. Only the first in document order enabled transition is executed."

		if len(enableds) > 0 :
			enabled = enableds[0]
			if enabled == 1 :
				self.exit_Root_initializing()
				send_event = Event("button_created", parameters = [])
				self.object_manager.addEvent(Event("narrow_cast", parameters = [self, 'parent' , send_event]))
				self.enter_Root_running()
			catched = True

		return catched

	def transition_Root_running(self, event) :
		catched = False
		enableds = []
		if event.name == "mouse_click" and event.getPort() == "ui" :
			parameters = event.getParameters()
			x = parameters[0]
			y = parameters[1]
			button = parameters[2]
			if button == ui.MOUSE_BUTTONS.LEFT :
				enableds.append(1)

		if len(enableds) > 1 :
			print "Runtime warning : indeterminism detected in a transition from node Root_running. Only the first in document order enabled transition is executed."

		if len(enableds) > 0 :
			enabled = enableds[0]
			if enabled == 1 :
				parameters = event.getParameters()
				x = parameters[0]
				y = parameters[1]
				button = parameters[2]
				self.exit_Root_running()
				send_event = Event("button_pressed", parameters = [self.event_name])
				self.object_manager.addEvent(Event("narrow_cast", parameters = [self, 'parent' , send_event]))
				self.enter_Root_running()
			catched = True

		return catched

	# Execute transitions
	def transition(self, event = Event("")):
		self.state_changed = self.transition_Root(event)
	# inState method for statechart
	def inState(self, nodes):
		for actives in self.current_state.itervalues():
			nodes = [node for node in nodes if node not in actives]
			if not nodes :
				return True
		return False


class Field(RuntimeClassBase):

	# Unique IDs for all statechart nodes
	Root = 0
	Root_root = 1
	Root_root_running = 2
	Root_root_running_main_behaviour = 3
	Root_root_running_deleting_behaviour = 4
	Root_root_running_child_behaviour = 5
	Root_root_waiting = 6
	Root_root_packing = 7
	Root_root_deleting = 8
	Root_root_creating = 9
	Root_root_initializing = 10
	Root_root_deleted = 11
	Root_root_running_main_behaviour_running = 12
	Root_root_running_main_behaviour_creating = 13
	Root_root_running_deleting_behaviour_running = 14
	Root_root_running_child_behaviour_listening = 15

	def commonConstructor(self, controller = None):
		"""Constructor part that is common for all constructors."""
		RuntimeClassBase.__init__(self)

		# User defined input ports
		self.inports = {}
		self.inports["field_ui"] = controller.addInputPort("field_ui", self)

		# User defined attributes
		self.field_window = None
		self.canvas = None

		self.controller = controller
		self.object_manager = controller.getObjectManager()
		self.current_state = {}
		self.history_state = {}
		self.timers = {}

		#Initialize statechart :

		self.current_state[self.Root] = []
		self.current_state[self.Root_root] = []
		self.current_state[self.Root_root_running] = []
		self.current_state[self.Root_root_running_main_behaviour] = []
		self.current_state[self.Root_root_running_deleting_behaviour] = []
		self.current_state[self.Root_root_running_child_behaviour] = []

	def start(self):
		super(Field, self).start()
		self.enterDefault_Root_root()

	#The actual constructor
	def __init__(self, controller):
		self.commonConstructor(controller)

		#constructor body (user-defined)
		self.field_window = ui.new_window(400, 450)
		self.canvas = ui.append_canvas(self.field_window, 400, 400, {'background':'#eee'})
		ui.bind_event(self.field_window, ui.EVENTS.WINDOW_CLOSE, self.controller, 'window_close')
		ui.bind_event(self.field_window, ui.EVENTS.KEY_PRESS, self.controller, 'key_press')
		ui.bind_event(self.canvas.element, ui.EVENTS.MOUSE_RIGHT_CLICK, self.controller, 'right_click', self.inports['field_ui'])
		ui.bind_event(self.canvas.element, ui.EVENTS.MOUSE_MOVE, self.controller, 'mouse_move')
		ui.bind_event(self.canvas.element, ui.EVENTS.MOUSE_RELEASE, self.controller, 'mouse_release')

	# User defined destructor
	def __del__(self):
		ui.close_window(self.field_window)

	# Statechart enter/exit action method(s) :

	def enter_Root_root(self):
		self.current_state[self.Root].append(self.Root_root)

	def exit_Root_root(self):
		if self.Root_root_waiting in self.current_state[self.Root_root] :
			self.exit_Root_root_waiting()
		if self.Root_root_packing in self.current_state[self.Root_root] :
			self.exit_Root_root_packing()
		if self.Root_root_deleting in self.current_state[self.Root_root] :
			self.exit_Root_root_deleting()
		if self.Root_root_creating in self.current_state[self.Root_root] :
			self.exit_Root_root_creating()
		if self.Root_root_initializing in self.current_state[self.Root_root] :
			self.exit_Root_root_initializing()
		if self.Root_root_deleted in self.current_state[self.Root_root] :
			self.exit_Root_root_deleted()
		if self.Root_root_running in self.current_state[self.Root_root] :
			self.exit_Root_root_running()
		self.current_state[self.Root] = []

	def enter_Root_root_running(self):
		self.current_state[self.Root_root].append(self.Root_root_running)

	def exit_Root_root_running(self):
		self.exit_Root_root_running_main_behaviour()
		self.exit_Root_root_running_deleting_behaviour()
		self.exit_Root_root_running_child_behaviour()
		self.current_state[self.Root_root] = []

	def enter_Root_root_running_main_behaviour(self):
		self.current_state[self.Root_root_running].append(self.Root_root_running_main_behaviour)

	def exit_Root_root_running_main_behaviour(self):
		if self.Root_root_running_main_behaviour_running in self.current_state[self.Root_root_running_main_behaviour] :
			self.exit_Root_root_running_main_behaviour_running()
		if self.Root_root_running_main_behaviour_creating in self.current_state[self.Root_root_running_main_behaviour] :
			self.exit_Root_root_running_main_behaviour_creating()
		self.current_state[self.Root_root_running] = []

	def enter_Root_root_running_deleting_behaviour(self):
		self.current_state[self.Root_root_running].append(self.Root_root_running_deleting_behaviour)

	def exit_Root_root_running_deleting_behaviour(self):
		if self.Root_root_running_deleting_behaviour_running in self.current_state[self.Root_root_running_deleting_behaviour] :
			self.exit_Root_root_running_deleting_behaviour_running()
		self.current_state[self.Root_root_running] = []

	def enter_Root_root_running_child_behaviour(self):
		self.current_state[self.Root_root_running].append(self.Root_root_running_child_behaviour)

	def exit_Root_root_running_child_behaviour(self):
		if self.Root_root_running_child_behaviour_listening in self.current_state[self.Root_root_running_child_behaviour] :
			self.exit_Root_root_running_child_behaviour_listening()
		self.current_state[self.Root_root_running] = []

	def enter_Root_root_waiting(self):
		self.current_state[self.Root_root].append(self.Root_root_waiting)

	def exit_Root_root_waiting(self):
		self.current_state[self.Root_root] = []

	def enter_Root_root_packing(self):
		self.current_state[self.Root_root].append(self.Root_root_packing)

	def exit_Root_root_packing(self):
		self.current_state[self.Root_root] = []

	def enter_Root_root_deleting(self):
		self.timers[0] = 0.05
		self.current_state[self.Root_root].append(self.Root_root_deleting)

	def exit_Root_root_deleting(self):
		self.timers.pop(0, None)
		self.current_state[self.Root_root] = []

	def enter_Root_root_creating(self):
		self.current_state[self.Root_root].append(self.Root_root_creating)

	def exit_Root_root_creating(self):
		self.current_state[self.Root_root] = []

	def enter_Root_root_initializing(self):
		self.current_state[self.Root_root].append(self.Root_root_initializing)

	def exit_Root_root_initializing(self):
		self.current_state[self.Root_root] = []

	def enter_Root_root_deleted(self):
		self.current_state[self.Root_root].append(self.Root_root_deleted)

	def exit_Root_root_deleted(self):
		self.current_state[self.Root_root] = []

	def enter_Root_root_running_main_behaviour_running(self):
		self.current_state[self.Root_root_running_main_behaviour].append(self.Root_root_running_main_behaviour_running)

	def exit_Root_root_running_main_behaviour_running(self):
		self.current_state[self.Root_root_running_main_behaviour] = []

	def enter_Root_root_running_main_behaviour_creating(self):
		self.current_state[self.Root_root_running_main_behaviour].append(self.Root_root_running_main_behaviour_creating)

	def exit_Root_root_running_main_behaviour_creating(self):
		self.current_state[self.Root_root_running_main_behaviour] = []

	def enter_Root_root_running_deleting_behaviour_running(self):
		self.current_state[self.Root_root_running_deleting_behaviour].append(self.Root_root_running_deleting_behaviour_running)

	def exit_Root_root_running_deleting_behaviour_running(self):
		self.current_state[self.Root_root_running_deleting_behaviour] = []

	def enter_Root_root_running_child_behaviour_listening(self):
		self.current_state[self.Root_root_running_child_behaviour].append(self.Root_root_running_child_behaviour_listening)

	def exit_Root_root_running_child_behaviour_listening(self):
		self.current_state[self.Root_root_running_child_behaviour] = []

	#Statechart enter/exit default method(s) :

	def enterDefault_Root_root(self):
		self.enter_Root_root()
		self.enter_Root_root_waiting()

	def enterDefault_Root_root_running(self):
		self.enter_Root_root_running()
		self.enterDefault_Root_root_running_main_behaviour()
		self.enterDefault_Root_root_running_deleting_behaviour()
		self.enterDefault_Root_root_running_child_behaviour()

	def enterDefault_Root_root_running_main_behaviour(self):
		self.enter_Root_root_running_main_behaviour()
		self.enter_Root_root_running_main_behaviour_running()

	def enterDefault_Root_root_running_deleting_behaviour(self):
		self.enter_Root_root_running_deleting_behaviour()
		self.enter_Root_root_running_deleting_behaviour_running()

	def enterDefault_Root_root_running_child_behaviour(self):
		self.enter_Root_root_running_child_behaviour()
		self.enter_Root_root_running_child_behaviour_listening()

	#Statechart transitions :

	def transition_Root(self, event) :
		catched = False
		if not catched :
			if self.current_state[self.Root][0] == self.Root_root:
				catched = self.transition_Root_root(event)
		return catched

	def transition_Root_root(self, event) :
		catched = False
		if not catched :
			if self.current_state[self.Root_root][0] == self.Root_root_waiting:
				catched = self.transition_Root_root_waiting(event)
			elif self.current_state[self.Root_root][0] == self.Root_root_packing:
				catched = self.transition_Root_root_packing(event)
			elif self.current_state[self.Root_root][0] == self.Root_root_deleting:
				catched = self.transition_Root_root_deleting(event)
			elif self.current_state[self.Root_root][0] == self.Root_root_creating:
				catched = self.transition_Root_root_creating(event)
			elif self.current_state[self.Root_root][0] == self.Root_root_initializing:
				catched = self.transition_Root_root_initializing(event)
			elif self.current_state[self.Root_root][0] == self.Root_root_deleted:
				catched = self.transition_Root_root_deleted(event)
			elif self.current_state[self.Root_root][0] == self.Root_root_running:
				catched = self.transition_Root_root_running(event)
		return catched

	def transition_Root_root_waiting(self, event) :
		catched = False
		enableds = []
		if event.name == "set_association_name" and event.getPort() == "" :
			enableds.append(1)

		if len(enableds) > 1 :
			print "Runtime warning : indeterminism detected in a transition from node Root_root_waiting. Only the first in document order enabled transition is executed."

		if len(enableds) > 0 :
			enabled = enableds[0]
			if enabled == 1 :
				parameters = event.getParameters()
				association_name = parameters[0]
				self.exit_Root_root_waiting()
				self.association_name = association_name
				self.enter_Root_root_initializing()
			catched = True

		return catched

	def transition_Root_root_packing(self, event) :
		catched = False
		enableds = []
		if event.name == "button_created" and event.getPort() == "" :
			enableds.append(1)

		if len(enableds) > 1 :
			print "Runtime warning : indeterminism detected in a transition from node Root_root_packing. Only the first in document order enabled transition is executed."

		if len(enableds) > 0 :
			enabled = enableds[0]
			if enabled == 1 :
				self.exit_Root_root_packing()
				self.enterDefault_Root_root_running()
			catched = True

		return catched

	def transition_Root_root_deleting(self, event) :
		catched = False
		enableds = []
		if event.name == "_0after" and event.getPort() == "" :
			enableds.append(1)

		if len(enableds) > 1 :
			print "Runtime warning : indeterminism detected in a transition from node Root_root_deleting. Only the first in document order enabled transition is executed."

		if len(enableds) > 0 :
			enabled = enableds[0]
			if enabled == 1 :
				self.exit_Root_root_deleting()
				send_event = Event("delete_field", parameters = [self.association_name])
				self.object_manager.addEvent(Event("narrow_cast", parameters = [self, 'parent' , send_event]))
				self.enter_Root_root_deleted()
			catched = True

		return catched

	def transition_Root_root_creating(self, event) :
		catched = False
		enableds = []
		if event.name == "instance_created" and event.getPort() == "" :
			enableds.append(1)

		if len(enableds) > 1 :
			print "Runtime warning : indeterminism detected in a transition from node Root_root_creating. Only the first in document order enabled transition is executed."

		if len(enableds) > 0 :
			enabled = enableds[0]
			if enabled == 1 :
				parameters = event.getParameters()
				association_name = parameters[0]
				self.exit_Root_root_creating()
				self.object_manager.addEvent(Event("start_instance", parameters = [self, association_name]))
				self.enter_Root_root_packing()
			catched = True

		return catched

	def transition_Root_root_initializing(self, event) :
		catched = False
		enableds = []
		enableds.append(1)

		if len(enableds) > 1 :
			print "Runtime warning : indeterminism detected in a transition from node Root_root_initializing. Only the first in document order enabled transition is executed."

		if len(enableds) > 0 :
			enabled = enableds[0]
			if enabled == 1 :
				self.exit_Root_root_initializing()
				self.object_manager.addEvent(Event("create_instance", parameters = [self, 'buttons','Button',self,'create_new_field','Spawn New Window']))
				self.enter_Root_root_creating()
			catched = True

		return catched

	def transition_Root_root_deleted(self, event) :
		catched = False
		return catched

	def transition_Root_root_running(self, event) :
		catched = False
		enableds = []
		if event.name == "window_close" and event.getPort() == "ui" :
			parameters = event.getParameters()
			window = parameters[0]
			if window == self.field_window or window == ui.window :
				enableds.append(1)

		if len(enableds) > 1 :
			print "Runtime warning : indeterminism detected in a transition from node Root_root_running. Only the first in document order enabled transition is executed."

		if len(enableds) > 0 :
			enabled = enableds[0]
			if enabled == 1 :
				parameters = event.getParameters()
				window = parameters[0]
				self.exit_Root_root_running()
				self.object_manager.addEvent(Event("delete_instance", parameters = [self, 'buttons']))
				send_event = Event("delete_self", parameters = [])
				self.object_manager.addEvent(Event("narrow_cast", parameters = [self, 'balls' , send_event]))
				self.enter_Root_root_deleting()
			catched = True

		if not catched :
			catched = self.transition_Root_root_running_main_behaviour(event) or catched
			catched = self.transition_Root_root_running_deleting_behaviour(event) or catched
			catched = self.transition_Root_root_running_child_behaviour(event) or catched
		return catched

	def transition_Root_root_running_main_behaviour(self, event) :
		catched = False
		if not catched :
			if self.current_state[self.Root_root_running_main_behaviour][0] == self.Root_root_running_main_behaviour_running:
				catched = self.transition_Root_root_running_main_behaviour_running(event)
			elif self.current_state[self.Root_root_running_main_behaviour][0] == self.Root_root_running_main_behaviour_creating:
				catched = self.transition_Root_root_running_main_behaviour_creating(event)
		return catched

	def transition_Root_root_running_main_behaviour_running(self, event) :
		catched = False
		enableds = []
		if event.name == "right_click" and event.getPort() == "field_ui" :
			enableds.append(1)

		if len(enableds) > 1 :
			print "Runtime warning : indeterminism detected in a transition from node Root_root_running_main_behaviour_running. Only the first in document order enabled transition is executed."

		if len(enableds) > 0 :
			enabled = enableds[0]
			if enabled == 1 :
				parameters = event.getParameters()
				x = parameters[0]
				y = parameters[1]
				button = parameters[2]
				self.exit_Root_root_running_main_behaviour_running()
				self.object_manager.addEvent(Event("create_instance", parameters = [self, 'balls','Ball',self.canvas,x,y,self.field_window]))
				self.enter_Root_root_running_main_behaviour_creating()
			catched = True

		return catched

	def transition_Root_root_running_main_behaviour_creating(self, event) :
		catched = False
		enableds = []
		if event.name == "instance_created" and event.getPort() == "" :
			enableds.append(1)

		if len(enableds) > 1 :
			print "Runtime warning : indeterminism detected in a transition from node Root_root_running_main_behaviour_creating. Only the first in document order enabled transition is executed."

		if len(enableds) > 0 :
			enabled = enableds[0]
			if enabled == 1 :
				parameters = event.getParameters()
				association_name = parameters[0]
				self.exit_Root_root_running_main_behaviour_creating()
				send_event = Event("set_association_name", parameters = [association_name])
				self.object_manager.addEvent(Event("narrow_cast", parameters = [self, association_name , send_event]))
				self.object_manager.addEvent(Event("start_instance", parameters = [self, association_name]))
				self.enter_Root_root_running_main_behaviour_running()
			catched = True

		return catched

	def transition_Root_root_running_deleting_behaviour(self, event) :
		catched = False
		if not catched :
			if self.current_state[self.Root_root_running_deleting_behaviour][0] == self.Root_root_running_deleting_behaviour_running:
				catched = self.transition_Root_root_running_deleting_behaviour_running(event)
		return catched

	def transition_Root_root_running_deleting_behaviour_running(self, event) :
		catched = False
		enableds = []
		if event.name == "delete_ball" and event.getPort() == "" :
			enableds.append(1)

		if len(enableds) > 1 :
			print "Runtime warning : indeterminism detected in a transition from node Root_root_running_deleting_behaviour_running. Only the first in document order enabled transition is executed."

		if len(enableds) > 0 :
			enabled = enableds[0]
			if enabled == 1 :
				parameters = event.getParameters()
				association_name = parameters[0]
				self.exit_Root_root_running_deleting_behaviour_running()
				self.object_manager.addEvent(Event("delete_instance", parameters = [self, association_name]))
				self.enter_Root_root_running_deleting_behaviour_running()
			catched = True

		return catched

	def transition_Root_root_running_child_behaviour(self, event) :
		catched = False
		if not catched :
			if self.current_state[self.Root_root_running_child_behaviour][0] == self.Root_root_running_child_behaviour_listening:
				catched = self.transition_Root_root_running_child_behaviour_listening(event)
		return catched

	def transition_Root_root_running_child_behaviour_listening(self, event) :
		catched = False
		enableds = []
		if event.name == "button_pressed" and event.getPort() == "" :
			enableds.append(1)

		if len(enableds) > 1 :
			print "Runtime warning : indeterminism detected in a transition from node Root_root_running_child_behaviour_listening. Only the first in document order enabled transition is executed."

		if len(enableds) > 0 :
			enabled = enableds[0]
			if enabled == 1 :
				parameters = event.getParameters()
				event_name = parameters[0]
				self.exit_Root_root_running_child_behaviour_listening()
				send_event = Event("button_pressed", parameters = [event_name])
				self.object_manager.addEvent(Event("narrow_cast", parameters = [self, 'parent' , send_event]))
				self.enter_Root_root_running_child_behaviour_listening()
			catched = True

		return catched

	# Execute transitions
	def transition(self, event = Event("")):
		self.state_changed = self.transition_Root(event)
	# inState method for statechart
	def inState(self, nodes):
		for actives in self.current_state.itervalues():
			nodes = [node for node in nodes if node not in actives]
			if not nodes :
				return True
		return False


class MainApp(RuntimeClassBase):

	# Unique IDs for all statechart nodes
	Root = 0
	Root_running = 1
	Root_running_root = 2
	Root_running_root_main_behaviour = 3
	Root_running_root_cd_behaviour = 4
	Root_running_stopped = 5
	Root_running_root_main_behaviour_initializing = 6
	Root_running_root_main_behaviour_running = 7
	Root_running_root_cd_behaviour_creating = 8
	Root_running_root_cd_behaviour_waiting = 9
	Root_running_root_cd_behaviour_check_nr_of_fields = 10

	def commonConstructor(self, controller = None):
		"""Constructor part that is common for all constructors."""
		RuntimeClassBase.__init__(self)

		# User defined input ports
		self.inports = {}
		self.controller = controller
		self.object_manager = controller.getObjectManager()
		self.current_state = {}
		self.history_state = {}

		#Initialize statechart :

		self.current_state[self.Root] = []
		self.current_state[self.Root_running] = []
		self.current_state[self.Root_running_root] = []
		self.current_state[self.Root_running_root_main_behaviour] = []
		self.current_state[self.Root_running_root_cd_behaviour] = []

	def start(self):
		super(MainApp, self).start()
		self.enterDefault_Root_running()

	#The actual constructor
	def __init__(self, controller):
		self.commonConstructor(controller)

		#constructor body (user-defined)
		self.nr_of_fields = 0
		ui.bind_event(ui.window, ui.EVENTS.WINDOW_CLOSE, self.controller, 'window_close')

	# Statechart enter/exit action method(s) :

	def enter_Root_running(self):
		self.current_state[self.Root].append(self.Root_running)

	def exit_Root_running(self):
		if self.Root_running_stopped in self.current_state[self.Root_running] :
			self.exit_Root_running_stopped()
		if self.Root_running_root in self.current_state[self.Root_running] :
			self.exit_Root_running_root()
		self.current_state[self.Root] = []

	def enter_Root_running_root(self):
		self.current_state[self.Root_running].append(self.Root_running_root)

	def exit_Root_running_root(self):
		self.exit_Root_running_root_main_behaviour()
		self.exit_Root_running_root_cd_behaviour()
		self.current_state[self.Root_running] = []

	def enter_Root_running_root_main_behaviour(self):
		self.current_state[self.Root_running_root].append(self.Root_running_root_main_behaviour)

	def exit_Root_running_root_main_behaviour(self):
		if self.Root_running_root_main_behaviour_initializing in self.current_state[self.Root_running_root_main_behaviour] :
			self.exit_Root_running_root_main_behaviour_initializing()
		if self.Root_running_root_main_behaviour_running in self.current_state[self.Root_running_root_main_behaviour] :
			self.exit_Root_running_root_main_behaviour_running()
		self.current_state[self.Root_running_root] = []

	def enter_Root_running_root_cd_behaviour(self):
		self.current_state[self.Root_running_root].append(self.Root_running_root_cd_behaviour)

	def exit_Root_running_root_cd_behaviour(self):
		if self.Root_running_root_cd_behaviour_creating in self.current_state[self.Root_running_root_cd_behaviour] :
			self.exit_Root_running_root_cd_behaviour_creating()
		if self.Root_running_root_cd_behaviour_waiting in self.current_state[self.Root_running_root_cd_behaviour] :
			self.exit_Root_running_root_cd_behaviour_waiting()
		if self.Root_running_root_cd_behaviour_check_nr_of_fields in self.current_state[self.Root_running_root_cd_behaviour] :
			self.exit_Root_running_root_cd_behaviour_check_nr_of_fields()
		self.current_state[self.Root_running_root] = []

	def enter_Root_running_stopped(self):
		self.current_state[self.Root_running].append(self.Root_running_stopped)

	def exit_Root_running_stopped(self):
		self.current_state[self.Root_running] = []

	def enter_Root_running_root_main_behaviour_initializing(self):
		self.current_state[self.Root_running_root_main_behaviour].append(self.Root_running_root_main_behaviour_initializing)

	def exit_Root_running_root_main_behaviour_initializing(self):
		self.current_state[self.Root_running_root_main_behaviour] = []

	def enter_Root_running_root_main_behaviour_running(self):
		self.current_state[self.Root_running_root_main_behaviour].append(self.Root_running_root_main_behaviour_running)

	def exit_Root_running_root_main_behaviour_running(self):
		self.current_state[self.Root_running_root_main_behaviour] = []

	def enter_Root_running_root_cd_behaviour_creating(self):
		self.current_state[self.Root_running_root_cd_behaviour].append(self.Root_running_root_cd_behaviour_creating)

	def exit_Root_running_root_cd_behaviour_creating(self):
		self.current_state[self.Root_running_root_cd_behaviour] = []

	def enter_Root_running_root_cd_behaviour_waiting(self):
		self.current_state[self.Root_running_root_cd_behaviour].append(self.Root_running_root_cd_behaviour_waiting)

	def exit_Root_running_root_cd_behaviour_waiting(self):
		self.current_state[self.Root_running_root_cd_behaviour] = []

	def enter_Root_running_root_cd_behaviour_check_nr_of_fields(self):
		self.current_state[self.Root_running_root_cd_behaviour].append(self.Root_running_root_cd_behaviour_check_nr_of_fields)

	def exit_Root_running_root_cd_behaviour_check_nr_of_fields(self):
		self.current_state[self.Root_running_root_cd_behaviour] = []

	#Statechart enter/exit default method(s) :

	def enterDefault_Root_running(self):
		self.enter_Root_running()
		self.enterDefault_Root_running_root()

	def enterDefault_Root_running_root(self):
		self.enter_Root_running_root()
		self.enterDefault_Root_running_root_main_behaviour()
		self.enterDefault_Root_running_root_cd_behaviour()

	def enterDefault_Root_running_root_main_behaviour(self):
		self.enter_Root_running_root_main_behaviour()
		self.enter_Root_running_root_main_behaviour_initializing()

	def enterDefault_Root_running_root_cd_behaviour(self):
		self.enter_Root_running_root_cd_behaviour()
		self.enter_Root_running_root_cd_behaviour_waiting()

	#Statechart transitions :

	def transition_Root(self, event) :
		catched = False
		if not catched :
			if self.current_state[self.Root][0] == self.Root_running:
				catched = self.transition_Root_running(event)
		return catched

	def transition_Root_running(self, event) :
		catched = False
		if not catched :
			if self.current_state[self.Root_running][0] == self.Root_running_stopped:
				catched = self.transition_Root_running_stopped(event)
			elif self.current_state[self.Root_running][0] == self.Root_running_root:
				catched = self.transition_Root_running_root(event)
		return catched

	def transition_Root_running_stopped(self, event) :
		catched = False
		return catched

	def transition_Root_running_root(self, event) :
		catched = False
		if not catched :
			catched = self.transition_Root_running_root_main_behaviour(event) or catched
			catched = self.transition_Root_running_root_cd_behaviour(event) or catched
		return catched

	def transition_Root_running_root_main_behaviour(self, event) :
		catched = False
		if not catched :
			if self.current_state[self.Root_running_root_main_behaviour][0] == self.Root_running_root_main_behaviour_initializing:
				catched = self.transition_Root_running_root_main_behaviour_initializing(event)
			elif self.current_state[self.Root_running_root_main_behaviour][0] == self.Root_running_root_main_behaviour_running:
				catched = self.transition_Root_running_root_main_behaviour_running(event)
		return catched

	def transition_Root_running_root_main_behaviour_initializing(self, event) :
		catched = False
		enableds = []
		enableds.append(1)

		if len(enableds) > 1 :
			print "Runtime warning : indeterminism detected in a transition from node Root_running_root_main_behaviour_initializing. Only the first in document order enabled transition is executed."

		if len(enableds) > 0 :
			enabled = enableds[0]
			if enabled == 1 :
				self.exit_Root_running_root_main_behaviour_initializing()
				self.addEvent(Event("create_field", parameters = []))
				self.enter_Root_running_root_main_behaviour_running()
			catched = True

		return catched

	def transition_Root_running_root_main_behaviour_running(self, event) :
		catched = False
		enableds = []
		if event.name == "button_pressed" and event.getPort() == "" :
			parameters = event.getParameters()
			event_name = parameters[0]
			if event_name == 'create_new_field' :
				enableds.append(1)

		if len(enableds) > 1 :
			print "Runtime warning : indeterminism detected in a transition from node Root_running_root_main_behaviour_running. Only the first in document order enabled transition is executed."

		if len(enableds) > 0 :
			enabled = enableds[0]
			if enabled == 1 :
				parameters = event.getParameters()
				event_name = parameters[0]
				self.exit_Root_running_root_main_behaviour_running()
				self.addEvent(Event("create_field", parameters = []))
				self.enter_Root_running_root_main_behaviour_running()
			catched = True

		return catched

	def transition_Root_running_root_cd_behaviour(self, event) :
		catched = False
		if not catched :
			if self.current_state[self.Root_running_root_cd_behaviour][0] == self.Root_running_root_cd_behaviour_creating:
				catched = self.transition_Root_running_root_cd_behaviour_creating(event)
			elif self.current_state[self.Root_running_root_cd_behaviour][0] == self.Root_running_root_cd_behaviour_waiting:
				catched = self.transition_Root_running_root_cd_behaviour_waiting(event)
			elif self.current_state[self.Root_running_root_cd_behaviour][0] == self.Root_running_root_cd_behaviour_check_nr_of_fields:
				catched = self.transition_Root_running_root_cd_behaviour_check_nr_of_fields(event)
		return catched

	def transition_Root_running_root_cd_behaviour_creating(self, event) :
		catched = False
		enableds = []
		if event.name == "instance_created" and event.getPort() == "" :
			enableds.append(1)

		if len(enableds) > 1 :
			print "Runtime warning : indeterminism detected in a transition from node Root_running_root_cd_behaviour_creating. Only the first in document order enabled transition is executed."

		if len(enableds) > 0 :
			enabled = enableds[0]
			if enabled == 1 :
				parameters = event.getParameters()
				association_name = parameters[0]
				self.exit_Root_running_root_cd_behaviour_creating()
				self.object_manager.addEvent(Event("start_instance", parameters = [self, association_name]))
				send_event = Event("set_association_name", parameters = [association_name])
				self.object_manager.addEvent(Event("narrow_cast", parameters = [self, association_name , send_event]))
				self.nr_of_fields += 1
				self.enter_Root_running_root_cd_behaviour_waiting()
			catched = True

		return catched

	def transition_Root_running_root_cd_behaviour_waiting(self, event) :
		catched = False
		enableds = []
		if event.name == "create_field" and event.getPort() == "" :
			enableds.append(1)

		if event.name == "delete_field" and event.getPort() == "" :
			enableds.append(2)

		if len(enableds) > 1 :
			print "Runtime warning : indeterminism detected in a transition from node Root_running_root_cd_behaviour_waiting. Only the first in document order enabled transition is executed."

		if len(enableds) > 0 :
			enabled = enableds[0]
			if enabled == 1 :
				self.exit_Root_running_root_cd_behaviour_waiting()
				self.object_manager.addEvent(Event("create_instance", parameters = [self, 'fields']))
				self.enter_Root_running_root_cd_behaviour_creating()
			elif enabled == 2 :
				parameters = event.getParameters()
				association_name = parameters[0]
				self.exit_Root_running_root_cd_behaviour_waiting()
				self.object_manager.addEvent(Event("delete_instance", parameters = [self, association_name]))
				self.nr_of_fields -= 1
				self.enter_Root_running_root_cd_behaviour_check_nr_of_fields()
			catched = True

		return catched

	def transition_Root_running_root_cd_behaviour_check_nr_of_fields(self, event) :
		catched = False
		enableds = []
		if self.nr_of_fields != 0 :
			enableds.append(1)

		if self.nr_of_fields == 0 :
			enableds.append(2)

		if len(enableds) > 1 :
			print "Runtime warning : indeterminism detected in a transition from node Root_running_root_cd_behaviour_check_nr_of_fields. Only the first in document order enabled transition is executed."

		if len(enableds) > 0 :
			enabled = enableds[0]
			if enabled == 1 :
				self.exit_Root_running_root_cd_behaviour_check_nr_of_fields()
				self.enter_Root_running_root_cd_behaviour_waiting()
			elif enabled == 2 :
				self.exit_Root_running_root()
				ui.close_window(ui.window)
				self.enter_Root_running_stopped()
			catched = True

		return catched

	# Execute transitions
	def transition(self, event = Event("")):
		self.state_changed = self.transition_Root(event)
	# inState method for statechart
	def inState(self, nodes):
		for actives in self.current_state.itervalues():
			nodes = [node for node in nodes if node not in actives]
			if not nodes :
				return True
		return False


class Ball(RuntimeClassBase):

	# Unique IDs for all statechart nodes
	Root = 0
	Root_main_behaviour = 1
	Root_main_behaviour_dragging = 2
	Root_main_behaviour_selected = 3
	Root_main_behaviour_initializing = 4
	Root_main_behaviour_bouncing = 5
	Root_deleted = 6

	def commonConstructor(self, controller = None):
		"""Constructor part that is common for all constructors."""
		RuntimeClassBase.__init__(self)

		# User defined input ports
		self.inports = {}
		self.inports["ball_ui"] = controller.addInputPort("ball_ui", self)

		# User defined attributes
		self.field_window = None
		self.canvas = None
		self.element = None

		self.controller = controller
		self.object_manager = controller.getObjectManager()
		self.current_state = {}
		self.history_state = {}
		self.timers = {}

		#Initialize statechart :

		self.current_state[self.Root] = []
		self.current_state[self.Root_main_behaviour] = []

	def start(self):
		super(Ball, self).start()
		self.enterDefault_Root_main_behaviour()

	#The actual constructor
	def __init__(self, controller, canvas, x, y, field_window):
		self.commonConstructor(controller)

		#constructor body (user-defined)
		self.canvas = canvas
		self.field_window = field_window
		self.r = 20.0
		self.vel = {'x':utils.random() * 2.0 - 1.0, 'y':utils.random() * 2.0 - 1.0}
		self.mouse_pos = {'':''}
		self.smooth = 0.4
		circle = self.canvas.add_circle(x, y, self.r, {'fill':'#000'})
		ui.bind_event(circle, ui.EVENTS.MOUSE_PRESS, self.controller, 'mouse_press', self.inports['ball_ui'])
		ui.bind_event(circle, ui.EVENTS.MOUSE_RIGHT_CLICK, self.controller, 'right_click')
		self.element = circle

	# User defined destructor
	def __del__(self):
		self.canvas.remove_element(self.element)

	# Statechart enter/exit action method(s) :

	def enter_Root_main_behaviour(self):
		self.current_state[self.Root].append(self.Root_main_behaviour)

	def exit_Root_main_behaviour(self):
		if self.Root_main_behaviour_dragging in self.current_state[self.Root_main_behaviour] :
			self.exit_Root_main_behaviour_dragging()
		if self.Root_main_behaviour_selected in self.current_state[self.Root_main_behaviour] :
			self.exit_Root_main_behaviour_selected()
		if self.Root_main_behaviour_initializing in self.current_state[self.Root_main_behaviour] :
			self.exit_Root_main_behaviour_initializing()
		if self.Root_main_behaviour_bouncing in self.current_state[self.Root_main_behaviour] :
			self.exit_Root_main_behaviour_bouncing()
		self.current_state[self.Root] = []

	def enter_Root_main_behaviour_dragging(self):
		self.current_state[self.Root_main_behaviour].append(self.Root_main_behaviour_dragging)

	def exit_Root_main_behaviour_dragging(self):
		self.current_state[self.Root_main_behaviour] = []

	def enter_Root_main_behaviour_selected(self):
		self.current_state[self.Root_main_behaviour].append(self.Root_main_behaviour_selected)

	def exit_Root_main_behaviour_selected(self):
		self.current_state[self.Root_main_behaviour] = []

	def enter_Root_main_behaviour_initializing(self):
		self.current_state[self.Root_main_behaviour].append(self.Root_main_behaviour_initializing)

	def exit_Root_main_behaviour_initializing(self):
		self.current_state[self.Root_main_behaviour] = []

	def enter_Root_main_behaviour_bouncing(self):
		self.timers[0] = 0.01
		self.current_state[self.Root_main_behaviour].append(self.Root_main_behaviour_bouncing)

	def exit_Root_main_behaviour_bouncing(self):
		self.timers.pop(0, None)
		self.current_state[self.Root_main_behaviour] = []

	def enter_Root_deleted(self):
		self.current_state[self.Root].append(self.Root_deleted)

	def exit_Root_deleted(self):
		self.current_state[self.Root] = []

	#Statechart enter/exit default method(s) :

	def enterDefault_Root_main_behaviour(self):
		self.enter_Root_main_behaviour()
		self.enter_Root_main_behaviour_initializing()

	#Statechart transitions :

	def transition_Root(self, event) :
		catched = False
		if not catched :
			if self.current_state[self.Root][0] == self.Root_main_behaviour:
				catched = self.transition_Root_main_behaviour(event)
			elif self.current_state[self.Root][0] == self.Root_deleted:
				catched = self.transition_Root_deleted(event)
		return catched

	def transition_Root_main_behaviour(self, event) :
		catched = False
		enableds = []
		if event.name == "delete_self" and event.getPort() == "" :
			enableds.append(1)

		if len(enableds) > 1 :
			print "Runtime warning : indeterminism detected in a transition from node Root_main_behaviour. Only the first in document order enabled transition is executed."

		if len(enableds) > 0 :
			enabled = enableds[0]
			if enabled == 1 :
				self.exit_Root_main_behaviour()
				send_event = Event("delete_ball", parameters = [self.association_name])
				self.object_manager.addEvent(Event("narrow_cast", parameters = [self, 'parent' , send_event]))
				self.enter_Root_deleted()
			catched = True

		if not catched :
			if self.current_state[self.Root_main_behaviour][0] == self.Root_main_behaviour_dragging:
				catched = self.transition_Root_main_behaviour_dragging(event)
			elif self.current_state[self.Root_main_behaviour][0] == self.Root_main_behaviour_selected:
				catched = self.transition_Root_main_behaviour_selected(event)
			elif self.current_state[self.Root_main_behaviour][0] == self.Root_main_behaviour_initializing:
				catched = self.transition_Root_main_behaviour_initializing(event)
			elif self.current_state[self.Root_main_behaviour][0] == self.Root_main_behaviour_bouncing:
				catched = self.transition_Root_main_behaviour_bouncing(event)
		return catched

	def transition_Root_main_behaviour_dragging(self, event) :
		catched = False
		enableds = []
		if event.name == "mouse_release" and event.getPort() == "ui" :
			enableds.append(1)

		if event.name == "mouse_move" and event.getPort() == "ui" :
			enableds.append(2)

		if len(enableds) > 1 :
			print "Runtime warning : indeterminism detected in a transition from node Root_main_behaviour_dragging. Only the first in document order enabled transition is executed."

		if len(enableds) > 0 :
			enabled = enableds[0]
			if enabled == 1 :
				parameters = event.getParameters()
				x = parameters[0]
				y = parameters[1]
				self.exit_Root_main_behaviour_dragging()
				self.element.set_color('#f00')
				self.enter_Root_main_behaviour_bouncing()
			elif enabled == 2 :
				parameters = event.getParameters()
				x = parameters[0]
				y = parameters[1]
				button = parameters[2]
				self.exit_Root_main_behaviour_dragging()
				dx = x - self.mouse_pos['x']
				dy = y - self.mouse_pos['y']
				self.element.move(dx, dy)
				pos = self.element.get_position()
				if pos.x - self.r <= 0:
					pos.x = self.r + 1
				else:
					if pos.x + self.r >= self.canvas.width:
						pos.x = self.canvas.width - self.r - 1
				if pos.y - self.r <= 0:
					pos.y = self.r + 1
				else:
					if pos.y + self.r >= self.canvas.height:
						pos.y = self.canvas.height - self.r - 1
				self.element.set_position(pos.x, pos.y)
				self.mouse_pos = {'x':x, 'y':y}
				self.vel = {'x':(1 - self.smooth) * dx + self.smooth * self.vel['x'], 'y':(1 - self.smooth) * dy + self.smooth * self.vel['y']}
				self.enter_Root_main_behaviour_dragging()
			catched = True

		return catched

	def transition_Root_main_behaviour_selected(self, event) :
		catched = False
		enableds = []
		if event.name == "mouse_press" and event.getPort() == "ball_ui" :
			parameters = event.getParameters()
			x = parameters[0]
			y = parameters[1]
			button = parameters[2]
			if button == ui.MOUSE_BUTTONS.LEFT :
				enableds.append(1)

		if event.name == "key_press" and event.getPort() == "ui" :
			parameters = event.getParameters()
			key = parameters[0]
			active_window = parameters[1]
			if key == ui.KEYCODES.DELETE and active_window == self.field_window :
				enableds.append(2)

		if len(enableds) > 1 :
			print "Runtime warning : indeterminism detected in a transition from node Root_main_behaviour_selected. Only the first in document order enabled transition is executed."

		if len(enableds) > 0 :
			enabled = enableds[0]
			if enabled == 1 :
				parameters = event.getParameters()
				x = parameters[0]
				y = parameters[1]
				button = parameters[2]
				self.exit_Root_main_behaviour_selected()
				self.mouse_pos = {'x':x, 'y':y}
				self.enter_Root_main_behaviour_dragging()
			elif enabled == 2 :
				parameters = event.getParameters()
				key = parameters[0]
				active_window = parameters[1]
				self.exit_Root_main_behaviour_selected()
				self.addEvent(Event("delete_self", parameters = []))
				self.enter_Root_main_behaviour_selected()
			catched = True

		return catched

	def transition_Root_main_behaviour_initializing(self, event) :
		catched = False
		enableds = []
		if event.name == "set_association_name" and event.getPort() == "" :
			enableds.append(1)

		if len(enableds) > 1 :
			print "Runtime warning : indeterminism detected in a transition from node Root_main_behaviour_initializing. Only the first in document order enabled transition is executed."

		if len(enableds) > 0 :
			enabled = enableds[0]
			if enabled == 1 :
				parameters = event.getParameters()
				association_name = parameters[0]
				self.exit_Root_main_behaviour_initializing()
				self.association_name = association_name
				self.enter_Root_main_behaviour_bouncing()
			catched = True

		return catched

	def transition_Root_main_behaviour_bouncing(self, event) :
		catched = False
		enableds = []
		if event.name == "_0after" and event.getPort() == "" :
			enableds.append(1)

		if event.name == "mouse_press" and event.getPort() == "ball_ui" :
			parameters = event.getParameters()
			x = parameters[0]
			y = parameters[1]
			button = parameters[2]
			if button == ui.MOUSE_BUTTONS.LEFT :
				enableds.append(2)

		if len(enableds) > 1 :
			print "Runtime warning : indeterminism detected in a transition from node Root_main_behaviour_bouncing. Only the first in document order enabled transition is executed."

		if len(enableds) > 0 :
			enabled = enableds[0]
			if enabled == 1 :
				self.exit_Root_main_behaviour_bouncing()
				pos = self.element.get_position()
				if pos.x - self.r <= 0 or pos.x + self.r >= self.canvas.width:
					self.vel['x'] = -self.vel['x']
				if pos.y - self.r <= 0 or pos.y + self.r >= self.canvas.height:
					self.vel['y'] = -self.vel['y']
				self.element.move(self.vel['x'], self.vel['y'])
				self.enter_Root_main_behaviour_bouncing()
			elif enabled == 2 :
				parameters = event.getParameters()
				x = parameters[0]
				y = parameters[1]
				button = parameters[2]
				self.exit_Root_main_behaviour_bouncing()
				self.element.set_color('#ff0')
				self.enter_Root_main_behaviour_selected()
			catched = True

		return catched

	def transition_Root_deleted(self, event) :
		catched = False
		return catched

	# Execute transitions
	def transition(self, event = Event("")):
		self.state_changed = self.transition_Root(event)
	# inState method for statechart
	def inState(self, nodes):
		for actives in self.current_state.itervalues():
			nodes = [node for node in nodes if node not in actives]
			if not nodes :
				return True
		return False

class ObjectManager (ObjectManagerBase):
	def __init__(self, controller):
		super(ObjectManager, self).__init__(controller)

	def instantiate(self, class_name, construct_params):
		associations = []
		if class_name == "Button" :
			instance =  Button(self.controller, *construct_params)
			associations.append(Association("parent", "Field", 1, 1))
		elif class_name == "Field" :
			instance =  Field(self.controller, *construct_params)
			associations.append(Association("parent", "MainApp", 1, 1))
			associations.append(Association("buttons", "Button", 0, -1))
			associations.append(Association("balls", "Ball", 0, -1))
		elif class_name == "MainApp" :
			instance =  MainApp(self.controller, *construct_params)
			associations.append(Association("fields", "Field", 0, -1))
		elif class_name == "Ball" :
			instance =  Ball(self.controller, *construct_params)
			associations.append(Association("parent", "Field", 1, 1))
		if instance:
			return InstanceWrapper(instance, associations)
		else :
			return None

from python_runtime.statecharts_core import GameLoopControllerBase
class Controller(GameLoopControllerBase):
	def __init__(self, keep_running = True):
		super(Controller, self).__init__(ObjectManager(self), keep_running)
		self.addInputPort("field_ui")
		self.addInputPort("ball_ui")
		self.addInputPort("ui")
		self.object_manager.createInstance("MainApp", [])

def main():
	controller = Controller()
	controller.start()

if __name__ == "__main__":
	main()
