from sccd.action_lang.static.types import SCCDType

# In the Python interpreter, a state configuration is a 'Bitmap' (basically just an 'int')
# In generated Rust code, a state configuration is the statechart-specific type called 'Root'.
class SCCDStateConfiguration(SCCDType):
    
    def __init__(self, state):
        self.state = state

    def _str(self):
        return "sconf"
