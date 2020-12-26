# Demo of a library that can be imported into the action language with the import-statement.

import time

def meaning_of_life():
    time.sleep(0.001) # takes a while to compute ;)
    return 42

from sccd.action_lang.static.types import *

SCCD_EXPORTS = {
    # adapt native Python to action language's static type system
    "meaning_of_life": (meaning_of_life, SCCDFunction([], SCCDInt)), 
}
