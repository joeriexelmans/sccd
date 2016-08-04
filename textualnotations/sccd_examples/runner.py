'''
Created on 10-sep.-2014

@author: Bruno
'''
from fsaclasses import State, Transition, After, AtomValue, Float, FSAModel,Event,RunTimeEvent,Events
import fsasimulator

def buildModel():
    statea = State("a")
    stateb = State("b")
    statec = State("c")
    stated = State("d")    
        
    transitionab = Transition("a2b",statea,stateb)
    transitionab.trigger = After(Float(5.0))

    transitionbc = Transition("b2c",stateb,statec)
    transitionbc.trigger = After(Float(2.0))

    transitioncd = Transition("c2d",statec,stated)
    transitioncd.trigger = Event("c")

    transitionda = Transition("d2a",stated,statea)
    transitionda.trigger = After(Float(5.0))

    fsamodel = FSAModel(
                        [statea,stateb,statec,stated],
                        [transitionab,transitionbc,transitioncd,transitionda]
                        )
    fsamodel.initialState = statea
    return fsamodel    

if __name__ == '__main__':
    
    fsamodel = buildModel()
    events = Events([RunTimeEvent('a',3.0),RunTimeEvent('b',5.0),RunTimeEvent('c',10.0)])
    controller = fsasimulator.Controller(fsamodel, events, [])
    controller.start()