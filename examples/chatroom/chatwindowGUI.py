import Tkinter as tk
import scrollable_frame

class ChatWindowGUI(tk.Tk):
	def __init__(self, keypress):
		tk.Tk.__init__(self)
		self.resizable(width=tk.FALSE, height=tk.FALSE)
		self.width = 230
		self.height = 100
		self.labelwidth = 30

		self.frame = tk.Frame(self)
		self.frame.focus_set()
		self.frame.bind('<Key>', keypress)
		self.chat_field = scrollable_frame.VerticalScrolledFrame(self.frame, bd='2', height=self.height, width=self.width, relief=tk.RIDGE)
		tk.Label(self.chat_field.interior, text='SCCD Chat Client -- Tk version', justify=tk.LEFT, anchor=tk.NW, width=self.labelwidth).pack()
		self.tk_buffer = tk.StringVar()
		input_frame = tk.Frame(self.frame, bd='2', height=100, width=self.width, relief=tk.RIDGE)
		self.input_text = tk.Label(input_frame, textvar=self.tk_buffer, anchor=tk.NW, justify=tk.LEFT, wraplength=self.width, width=self.labelwidth, background='grey')
		self.chat_field.pack(anchor=tk.NW)
		input_frame.pack(anchor=tk.NW, fill=tk.X)
		self.input_text.pack(anchor=tk.NW, fill=tk.X)
		self.frame.pack(anchor=tk.NW)
	
	def redraw_buffer(self, text):
		self.tk_buffer.set(text)
	
	def setColor(self, color):
		self.input_text.configure(background=color)
		
	def addMessage(self, msg, color):
		tk.Label(self.chat_field.interior, text=msg, anchor=tk.NW, justify=tk.LEFT, foreground=color, wraplength=230, width=30).pack(anchor=tk.NW)