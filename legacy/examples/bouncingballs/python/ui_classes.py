from widget_private_ports import Widget
from sccd.runtime.statecharts_core import Event
import Tkinter as tk
import random

class WindowVis(tk.Toplevel, Widget):
    def __init__(self, sccd_object):
        tk.Toplevel.__init__(self)
        self.sccd_object = sccd_object
        self.inport = self.sccd_object.inports["window_ui_in"]
        self.outport = self.sccd_object.outports["window_ui_out"]
        Widget.__init__(self, True, self.inport, self.outport)

        self.buttons = {}
        self.balls = {}

        self.title('BouncingBalls')
        self.c = tk.Canvas(self, relief=tk.RIDGE)
        self.repack()
        self.set_bindable_and_tagorid(self.c)
        self.c.bind("<Configure>", self.window_resize_handler)

        self.listener = self.sccd_object.controller.addOutputListener(self.outport)
        self.after(40, self.handle_output_events)
        Widget.controller.addInput(Event("ui_initialized", self.inport, [self.winfo_width(), self.winfo_height()]))

    def destruct(self):
        self.destroy()

    def repack(self):
        self.c.pack_forget()
        for b in self.buttons.itervalues():
            b.pack_forget()
            b.pack(expand=False, fill=tk.X, side=tk.TOP)
        self.c.focus_force()
        self.c.pack(expand=True, fill=tk.BOTH)
        self.update()

    def window_resize_handler(self, event):
        Widget.controller.addInput(Event("size_changed", self.inport, [event.width, event.height]))

    def on_click(self, event):
        event_name = None

        if event.num == 1:
            event_name = "left-click"
        elif event.num == 2:
            event_name = "middle-click"
        elif event.num == 3:
            event_name = "right-click"

        if event_name == "right-click":
            self.last_x = event.x
            self.last_y = event.y
            Widget.controller.addInput(Event("create_ball", self.inport, [self.last_x, self.last_y]))

    def handle_output_events(self):
        while True:
            output_event = self.listener.fetch(0)
            if not output_event is None:
                if output_event.getName() == "create_new_button":
                    self.on_create_new_button(output_event)
                elif output_event.getName() == "delete_ball":
                    self.on_delete_ball(output_event)
                elif output_event.getName() == "create_new_ball":
                    self.on_create_new_ball(output_event)
                elif output_event.getName() == "resize_window":
                    self.on_resize_window(output_event)
            else:
                break
        for b in self.buttons.itervalues():
            b.handle_output_events()
        for b in self.balls.itervalues():
            b.handle_output_events()

        self.after(40, self.handle_output_events)

    def on_create_new_button(self, event):
        assoc_name = event.getParameters()[0]
        sccd_object = event.getParameters()[1]
        self.buttons[assoc_name] = ButtonVis(sccd_object, self)
        self.repack()

    def on_delete_ball(self, event):
        self.balls[event.getParameters()[0]].destruct()
        del self.balls[event.getParameters()[0]]

    def on_create_new_ball(self, event):
        assoc_name = event.getParameters()[0]
        sccd_object = event.getParameters()[1]
        self.balls[assoc_name] = BallVis(sccd_object, self.c)

    def on_resize_window(self, event):
        #self.geometry("%sx%s" % tuple(event.getParameters()))
        pass

class ButtonVis(tk.Button, Widget):
    def __init__(self, sccd_object, window):
        tk.Button.__init__(self, window)
        self.sccd_object = sccd_object
        self.inport = self.sccd_object.inports["button_ui_in"]
        self.outport = self.sccd_object.outports["button_ui_out"]
        Widget.__init__(self, False, self.inport, self.outport)

        self.listener = self.sccd_object.controller.addOutputListener(self.outport)

        Widget.controller.addInput(Event("ui_initialized", self.inport))

    def on_click(self, event):
        event_name = None

        if event.num == 1:
            event_name = "left-click"
        elif event.num == 2:
            event_name = "middle-click"
        elif event.num == 3:
            event_name = "right-click"

        if event_name == "left-click":
            Widget.controller.addInput(Event("clicked", self.inport))

    def handle_output_events(self):
        while True:
            output_event = self.listener.fetch(0)
            if not output_event is None:
                if output_event.getName() == "set_text":
                    self.on_set_text(output_event)
            else:
                break

    def on_set_text(self, event):
        self.config(text=event.getParameters()[0])

    def mymethod(self):
        pass

class BallVis(Widget):
    def __init__(self, sccd_object, canvas):
        self.sccd_object = sccd_object
        self.inport = self.sccd_object.inports["ball_ui_in"]
        self.outport = self.sccd_object.outports["ball_ui_out"]
        Widget.__init__(self, True, self.inport, self.outport)
        self.canvas = canvas

        self.listener = self.sccd_object.controller.addOutputListener(self.outport)

        Widget.controller.addInput(Event("ui_initialized", self.inport))

    def destruct(self):
        self.canvas.delete(self.id)

    def on_click(self, event):
        event_name = None

        if event.num == 1:
            event_name = "left-click"
        elif event.num == 2:
            event_name = "middle-click"
        elif event.num == 3:
            event_name = "right-click"

        if event_name == "left-click":
            self.last_x = event.x
            self.last_y = event.y
            Widget.controller.addInput(Event("select_ball", self.inport))

    def on_release(self, event):
        event_name = None

        if event.num == 1:
            event_name = "left-release"
        elif event.num == 2:
            event_name = "middle-release"
        elif event.num == 3:
            event_name = "right-release"

        if event_name == "left-release":
            self.last_x = event.x
            self.last_y = event.y
            Widget.controller.addInput(Event("unselect_ball", self.inport))

    def on_motion(self, event):
        Widget.controller.addInput(Event("motion", self.inport, [self.canvas.canvasx(event.x) - self.canvas.canvasx(self.last_x), self.canvas.canvasy(event.y) - self.canvas.canvasy(self.last_y)]))
        self.last_x = event.x
        self.last_y = event.y

    def handle_output_events(self):
        while True:
            output_event = self.listener.fetch(0)
            if not output_event is None:
                if output_event.getName() == "set_initial_params":
                    self.on_set_initial_params(output_event)
                if output_event.getName() == "change_position":
                    self.on_change_position(output_event)
                if output_event.getName() == "change_color":
                    self.on_change_color(output_event)
            else:
                break

    def on_set_initial_params(self, event):
        self.x, self.y, self.r = event.getParameters()
        self.id = self.canvas.create_oval(self.x, self.y, self.x + (self.r * 2), self.y + (self.r * 2), fill="black")
        self.set_bindable_and_tagorid(self.canvas, self.id)

    def on_change_position(self, event):
        self.x, self.y = event.getParameters()
        self.canvas.coords(self.id, self.x, self.y, self.x + (self.r * 2), self.y + (self.r * 2))

    def on_change_color(self, event):
        self.canvas.itemconfig(self.id, fill=event.getParameters()[0])