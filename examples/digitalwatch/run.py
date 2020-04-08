from DigitalWatchGUI import DigitalWatchGUI
import tkinter
from tkinter.constants import NO

from sccd.controller.controller import *
from sccd.statechart.parser.xml import parse_f, create_statechart_parser
from sccd.model.model import *

g = Globals()
sc_parser = create_statechart_parser(g, "statechart_digitalwatch.xml")
statechart = parse_f("statechart_digitalwatch.xml", rules=sc_parser)
model = SingleInstanceModel(g, statechart)
controller = Controller(model)


root = tkinter.Tk()
root.withdraw()
topLevel = tkinter.Toplevel(root)
topLevel.resizable(width=NO, height=NO)
topLevel.title("DWatch")
gui = DigitalWatchGUI(topLevel)

gui.controller.

root.mainloop()