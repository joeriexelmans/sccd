'''
Created on 27-jul.-2014

@author: Simon
'''

import target_py.target_performance_threads as target
import sys
from sccd.runtime.statecharts_core import Event

if __name__ == '__main__':
    def callback(ctrl, behind_schedule):
        if behind_schedule > 2000:
            print len(ctrl.object_manager.instances)
            ctrl.stop()
            sys.exit()
    controller = target.Controller(behind_schedule_callback=callback)
    controller.start()
