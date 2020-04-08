'''
Created on 27-jul.-2014

@author: Simon
'''

import target_py.target_performance_cpu_time as target
import sys
from sccd.runtime.statecharts_core import Event

if __name__ == '__main__':
	# fields_to_create, balls_to_create
    controller = target.Controller(int(sys.argv[1]), int(sys.argv[2]))
    controller.start()
