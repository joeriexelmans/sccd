
############### runtime classes

class RunTimeEvent:
    def __init__(self, name, time):
        self.name = name
        self.time = time

class Events:
    def __init__(self, events):
        self.events = events
        
    def pop(self):
        if self.events != []:
            return self.events.pop(0)

    def getInputAt(self,time):
        input = None
        while self.events != []:
            if(self.events[0].time <= time):
                input = self.events.pop(0)
                break
            else:
                break
        return input

############### static classes - invariants

class Expression:
    def __init__(self):
        pass

class FSAModel:
    def __init__(self,states,transitions):
        self.transitions = transitions
        self.states = states
        self.initialState = None
        
    def getTransitionFrom(self, state, event):
        if event == None:
            return None

        for t in self.transitions:
            if t.source == state and isinstance(t.trigger,Event) and t.trigger.name == event.name:
                    return t
        return None

    def getTransitionAfter(self, state, elapsed):
        for t in self.transitions:
            if t.source == state and isinstance(t.trigger,After):
                if ExpressionVisitor(t.trigger.after).visit() <= elapsed:
                    return t
        return None 

class ExpressionVisitor:
    def __init__(self, expression):
        self.expression = expression
        
    def visit(self):
        if(isinstance(self.expression,AtomValue)):
            return self.expression.value
        if(isinstance(self.expression,Operation)):
            left = ExpressionVisitor(self.expression.left).visit()
            right = ExpressionVisitor(self.expression.right).visit()
            if(self.expression.op == '+'):
                return left + right
            if(self.expression.op == '-'):
                return left - right
            if(self.expression.op == '*'):
                return left * right
            if(self.expression.op == '/'):
                return left / right
            if(self.expression.op == 'and'):
                return left and right
            if(self.expression.op == 'or'):
                return left or right
        if(isinstance(self.expression,Not)):
            return not ExpressionVisitor(self.expression.expression).visit()

class State:
    def __init__(self, name, default = False):
        self.name = name
        self.final = default
        
    def getName(self):
        return self.name

class Operation(Expression):
    def __init__(self, left, right, op):
        self.op = op
        self.left = left
        self.right = right
        
class Transition:
    def __init__(self,name, source,target):
        self.name = name
        self.source = source
        self.target = target
        self.trigger = None
        self.guard = None
    
class Trigger:
    def __init__(self):
        pass

class Event(Trigger):
    def __init__(self,name):
        self.name = name

class After(Trigger):
    def __init__(self, expression):
        self.after = expression

class Guard:
    def __init__(self, expression):
        self.expression = expression

class And(Operation):
    def __init__(self, lexpression, rexpression):
        self.left = lexpression
        self.right = rexpression
        self.op = "and"

class Or(Operation):
    def __init__(self, lexpression, rexpression):
        self.left = lexpression
        self.right = rexpression
        self.op = "or"

class Not(Expression):
    def __init__(self, expression):
        self.expression = expression

class Variable(Expression):
    def __init__(self, varname):
        self.name = varname

class AtomValue(Expression):
    def __init__(self, value):
        self.value = value

class Integer(AtomValue):
    def __init__(self, value):
        self.value = value
    
class Float(AtomValue):
    def __init__(self, value):
        self.value = value

class String(AtomValue):
    def __init__(self, value):
        self.value = value
