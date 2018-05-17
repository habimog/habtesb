#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from collections import deque
from threading import Timer
from random import shuffle
import subprocess

class PeriodicTask():
	def __init__(self, interval, callback, daemon=False, **kwargs):
		self.interval = interval
		self.callback = callback
		self.daemon = daemon
		self.kwargs = kwargs
	
		# Initialize random load from list	
		loadList = [25, 50, 75, 100]
		shuffle(loadList)
		self.load = deque(loadList)
	
	def run(self):
		load = self.load.pop()
		self.load.appendleft(load)
		self.callback(load, self.interval, **self.kwargs)
		t = Timer(self.interval, self.run)
		t.daemon = self.daemon
		t.start()

def job(load, timeout):
	cmd = "stress-ng --cpu 1 --cpu-method matrixprod --cpu-load %s --timeout %s &" % (load, timeout)
	output = subprocess.check_call(cmd, shell=True)
	return output
	
'''
	Main
'''
if __name__ == "__main__":
	task = PeriodicTask(interval=1800, callback=job)
	task.run()
