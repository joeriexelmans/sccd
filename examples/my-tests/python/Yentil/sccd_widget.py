'''
Created on 31-jul.-2014

@author: Simon
'''

from PIL import Image, ImageTk

import Tkinter as tk
import atexit
from sccd.runtime.statecharts_core import Event

class SCCDWidget:
    controller = None

    def __init__(self, configure_later=False):
        if not configure_later:
            self.set_bindable_and_tagorid(None, None)

    def set_bindable_and_tagorid(self, bindable=None, tagorid=None):
        if bindable is None:
            bindable = self
        self.bindable = bindable
        self.mytagorid = tagorid
        if isinstance(self, tk.Toplevel):
            self.protocol("WM_DELETE_WINDOW", self.window_close)
        if tagorid is not None:
            if not isinstance(tagorid, list):
                tagorid = [tagorid]
            for t in tagorid:
                self.bindable.tag_bind(t, "<Button>", self.on_click)
                self.bindable.tag_bind(t, "<Double-Button>", self.on_dbclick)
                self.bindable.tag_bind(t, "<ButtonRelease>", self.on_release)
                self.bindable.tag_bind(t, "<Motion>", self.on_motion)
                self.bindable.tag_bind(t, "<Enter>", self.on_enter)
                self.bindable.tag_bind(t, "<Leave>", self.on_leave)
                self.bindable.tag_bind(t, "<Key>", self.on_key)
                self.bindable.tag_bind(t, "<KeyRelease>", self.on_key_release)
        else:
            self.bindable.bind("<Button>", self.on_click)
            self.bindable.bind("<ButtonRelease>", self.on_release)
            self.bindable.bind("<Motion>", self.on_motion)
            self.bindable.bind("<Enter>", self.on_enter)
            self.bindable.bind("<Leave>", self.on_leave)
            self.bindable.bind("<Key>", self.on_key)
            self.bindable.bind("<KeyRelease>", self.on_key_release)
            self.bindable.bind("<Shift-Up>",self.zoom_in)
            self.bindable.bind("<Shift-Down>", self.zoom_out)
            self.bindable.bind("<MouseWheel>", self.scroller)

        self.last_x = 50
        self.last_y = 50
        self.event_delta = 0
        self.zoomer_count = 0
        self.selected_type = None

    def scroller(self, event):
        self.event_delta = event.delta
        event_name= "scroll_mousewheel"
        self.last_x = event.x
        self.last_y = event.y
        SCCDWidget.controller.addInput(Event(event_name, "input", [id(self)]))
        return "break"

    def zoom_in(self, event):
        event_name = "zoomer_event"
        self.last_x = event.x
        self.last_y = event.y
        if self.zoomer_count <=6:
            self.event_delta = 120
            self.zoomer_count +=1
        SCCDWidget.controller.addInput(Event(event_name, "input", [id(self)]))
        return "break"

    def zoom_out(self, event):
        event_name = "zoomer_event"
        self.last_x = event.x
        self.last_y = event.y
        if self.zoomer_count >=-6:
            self.event_delta = -120
            self.zoomer_count -=1
        SCCDWidget.controller.addInput(Event(event_name, "input", [id(self)]))
        return "break"

    def on_dbclick(self, event):
        event_name = None

        if event.num == 1:
            event_name = "left-dbclick"
        elif event.num == 2:
            event_name = "middle-dbclick"
        elif event.num == 3:
            event_name = "right-dbclick"

        if event_name:
            self.last_x = event.x
            self.last_y = event.y
            SCCDWidget.controller.addInput(Event(event_name, "input", [id(self)]))
        return "break"

    def on_click(self, event):
        event_name = None
        if event.num == 1:
            event_name = "left-click"
        elif event.num == 2:
            event_name = "middle-click"
        elif event.num == 3:
            event_name = "right-click"

        if event_name:
            self.last_x = event.x
            self.last_y = event.y
            SCCDWidget.controller.addInput(Event(event_name, "input", [id(self)]))
        return "break"

    def on_release(self, event):
        event_name = None

        if event.num == 1:
            event_name = "left-release"
        elif event.num == 2:
            event_name = "middle-release"
        elif event.num == 3:
            event_name = "right-release"

        if event_name:
            self.last_x = event.x
            self.last_y = event.y
            SCCDWidget.controller.addInput(Event(event_name, "input", [id(self)]))
        return "break"

    def on_motion(self, event):
        self.last_x = event.x
        self.last_y = event.y
        SCCDWidget.controller.addInput(Event("motion", "input", [id(self)]))
        return "break"

    def on_enter(self, event):
        SCCDWidget.controller.addInput(Event("enter", "input", [id(self)]))
        return "break"

    def on_leave(self, event):
        SCCDWidget.controller.addInput(Event("leave", "input", [id(self)]))
        return "break"

    def on_key(self, event):
        event_name = None

        if event.keysym == 'Escape':
            event_name = "escape"
        elif event.keysym == 'Return':
            event_name = "return"
        elif event.keysym == 'Delete':
            event_name = "delete"
        elif event.keysym == 'Shift_L':
            event_name = "shift"
        elif event.keysym == 'Control_L':
            event_name = "control"
        elif event.keysym == 'Left':
            event_name = "left_key"
        elif event.keysym == 'Right':
            event_name = "right_key"
        elif event.keysym == 'Up':
            event_name = "up_key"
        elif event.keysym == 'Down':
            event_name = "down_key"

        if event_name:
            SCCDWidget.controller.addInput(Event(event_name, "input", [id(self)]))
        return "break"

    def on_key_release(self, event):
        event_name = None

        if event.keysym == 'Escape':
            event_name = "escape-release"
        elif event.keysym == 'Return':
            event_name = "return-release"
        elif event.keysym == 'Delete':
            event_name = "delete-release"
        elif event.keysym == 'Shift_L':
            event_name = "shift-release"
        elif event.keysym == 'Control_L':
            event_name = "control-release"

        if event_name:
            SCCDWidget.controller.addInput(Event(event_name, "input", [id(self)]))
        return "break"

    def window_close(self):
        SCCDWidget.controller.addInput(Event("window-close", "input", [id(self)]))

class HorizontalScrolledFrame(tk.Frame):
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a horizontal scrollbar for scrolling it
        hscrollbar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        hscrollbar.pack(fill=tk.X, side=tk.BOTTOM, expand=tk.FALSE)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                                xscrollcommand=hscrollbar.set, height=78)
        self.canvas.pack(side=tk.LEFT, fill=tk.X, expand=tk.TRUE)

        hscrollbar.config(command=self.canvas.xview)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(self.canvas)
        self.canvas.create_window(0, 0, window=interior, anchor=tk.NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            self.canvas.config(scrollregion="0 0 %s %s" % size)

        interior.bind('<Configure>', _configure_interior)

class VerticalScrolledFrame(tk.Frame):
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)

        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set, width=100)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        def _configure_interior(event):
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind('<Configure>', _configure_canvas)

        return

class VerticallyScrolledWindow(tk.Frame):
    def __init__(self, root):

        tk.Frame.__init__(self, root)
        defaultbg = root.cget('bg')
        self.canvas = tk.Canvas(root, borderwidth=0, background=defaultbg)
        self.frame = tk.Frame(self.canvas, background=defaultbg)
        self.vsb = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.frame, anchor="nw",
                                  tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)
        self.frame.bind_all("<MouseWheel>", self.scroll)

    def scroll(self, event):
        self.canvas.yview_scroll(-1 * (event.delta / 120), "units")

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

class Visual(object):
    def get_params(self):
        raise NotImplementedError()

class TextVisual(Visual):
    def __init__(self, text):
        super(TextVisual, self).__init__()
        self.text = text

    def get_params(self):
        return {'text': self.text}

class ImageVisual(Visual):
    def __init__(self, img_loc):
        super(ImageVisual, self).__init__()
        self.img = ImageTk.PhotoImage(Image.open(img_loc).resize((32, 32), Image.ANTIALIAS))

    def get_params(self):
        return {'image': self.img}

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.text = text

    def showtip(self):
        "Display text in tooltip window"
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + cx + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() - 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        try:
            # For Mac OS
            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")
        except tk.TclError:
            pass
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()
