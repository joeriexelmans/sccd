
#     removes the last character from the argument string
def remove_last_char(inp: str) -> str:
    return inp[:-1]

#     if the argument string represents an integer, returns its integer value
def stoi(inp: str) -> int:
    return int(inp)

#     returns true if the argument string represents an integer, else false
def is_numerical(inp: str) -> bool:
    try:
        int(inp)
        return True
    except ValueError:
        print("could not turn into int:", inp)
        return False

def is_backspace(char):
    return char == "\b"

def is_enter(char):
    return char == "\r" # Tkinter uses this symbol for 'enter' key press

from sccd.action_lang.static.types import *

SCCD_EXPORTS = {
    "remove_last_char": (remove_last_char, SCCDFunction([SCCDString], SCCDString)),
    "stoi": (stoi, SCCDFunction([SCCDString], SCCDInt)),
    "is_numerical": (is_numerical, SCCDFunction([SCCDString], SCCDBool)),
    "is_backspace": (is_backspace, SCCDFunction([SCCDString], SCCDBool)),
    "is_enter": (is_enter, SCCDFunction([SCCDString], SCCDBool)),
}
