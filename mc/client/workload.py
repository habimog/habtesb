#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

from collections import deque
from threading import Timer
#from random import shuffle
import subprocess

class PeriodicTask(object):
	def __init__(self, interval, callback, daemon=False, **kwargs):
		self.interval = interval
		self.callback = callback
		self.daemon = daemon
		self.kwargs = kwargs
	
		# Initialize random load from list	
		loadList = [75, 100] #[50, 100][25, 100]
		#shuffle(loadList)
		self.load = deque(loadList)
	
	def run(self):
		load = self.load.pop()
		self.load.appendleft(load)
		self.callback(self.interval, load, **self.kwargs)
		t = Timer(self.interval, self.run)
		t.daemon = self.daemon
		t.start()

def job(timeout, load):
	cmd = "stress-ng --cpu 1 --cpu-method matrixprod --timeout %s --cpu-load %s &" % (timeout, load)
	output = subprocess.check_call(cmd, shell=True)
	return output
	
'''
	Main
'''
if __name__ == "__main__":
	# Load changes every 90 minutes
	task = PeriodicTask(interval=5400, callback=job)
	task.run()
