import tkinter as tk
from lib.scrollable_frame import VerticalScrolledFrame
from sccd.realtime.threads_platform import ThreadsPlatform

class ChatWindowGUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.resizable(width=tk.FALSE, height=tk.FALSE)
        self.width = 230
        self.height = 100
        self.labelwidth = 30

        self.frame = tk.Frame(self)
        self.frame.focus_set()
        self.chat_field = VerticalScrolledFrame(self.frame, bd='2', height=self.height, width=self.width, relief=tk.RIDGE)
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

colors = {'info': 'black', 'local_message': 'red', 'remote_message': 'blue', 'warning': 'yellow'}
window = ChatWindowGUI()
buf = ""

def init(eventloop):
    global window

    def on_key_press(key):
        eventloop.add_input_now(port="ui", event_name="input", params=[key.char])

    window.bind('<Key>', on_key_press)
    # window = ChatWindowGUI(on_key_press)

#     shows the message in the chat window, with the specified type (as a string, either "info", "local_message", or "remote_message"))
def add_message(msg: str, type: str):
    window.addMessage(msg, colors[type])

#     adds a string to the input field and visualizes the change
def append_to_buffer(char: str):
    global buf
    buf += char
    window.redraw_buffer(buf)

#     removes the final character from the input field and visualizes the change
def remove_last_in_buffer():
    global buf
    buf = buf[:-1]
    window.redraw_buffer(buf)

#     clears the input field and visualizes the change
def clear_input():
    global buf
    buf = ""
    window.redraw_buffer(buf)

#     color the input field in the 'join' mode
def input_join():
    window.setColor('green')

#     color the input field in the 'message' mode
def input_msg():
    window.setColor('white')

#     color the input field in the 'command' mode
def input_command():
    window.setColor('grey')

#     returns the current content of the input field
def get_buffer() -> str:
    return buf

from sccd.action_lang.static.types import *

SCCD_EXPORTS = {
    "add_message": (add_message, SCCDFunction([SCCDString, SCCDString])),
    "append_to_buffer": (append_to_buffer, SCCDFunction([SCCDString])),
    "remove_last_in_buffer": (remove_last_in_buffer, SCCDFunction([])),
    "clear_input": (clear_input, SCCDFunction([])),
    "input_join": (input_join, SCCDFunction([])),
    "input_msg": (input_msg, SCCDFunction([])),
    "input_command": (input_command, SCCDFunction([])),
    "get_buffer": (get_buffer, SCCDFunction([], SCCDString)),
}
