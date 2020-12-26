import math

def log(s: str) -> None:
    print(termcolor.colored("log: ",'blue')+s)

from sccd.action_lang.static.types import *

SCCD_EXPORTS = {
    "log10": (math.log10, SCCDFunction([SCCDInt], SCCDFloat)),
    "print": (log, SCCDFunction([SCCDString])),
    "float_to_int": (int, SCCDFunction([SCCDFloat], SCCDInt)),
    "int_to_str": (str, SCCDFunction([SCCDInt], SCCDString)),
}
