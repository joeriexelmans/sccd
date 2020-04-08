from Tank import Tank
from player_controller import Controller, Event
from sccd.runtime.tkinter_eventloop import *
from sccd.runtime.libs.ui import ui

class PlayerTank(Tank):
	def __init__(self, field, data):		
		Tank.__init__(self, field, data)
		self.controller = Controller(self, TkEventLoop(field.canvas.master))
		self.controller.start()
		
	def destroy(self):
		Tank.destroy(self)
				
	def addListener(self, ports):
		return self.controller.addOutputListener(ports)
								
	def event(self, event_name, port):
		self.controller.addInput(Event(event_name, port))
			
	def update(self, delta):
		self.controller.addInput(Event("update","engine"))
		
		
