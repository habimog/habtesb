# -*- coding: utf-8 -*-

from utils import getHostTemp
from multiprocessing import Process, Queue
import time

class Calibrate():
	def __init__(self, timeout=600):
		self.timeout = timeout
		self.queue = Queue()
		self.process = Process(target=self._calibrate, args=(self.queue,))

	# Get server temperature
	def _calibrate(self, queue):
		while True:
			queue.put(getHostTemp())
			time.sleep(1)	

	def getCalibrationTemp(self):
		# We start the process and we block for 10 minutes.
		self.process.start()
		self.process.join(timeout=self.timeout)

		# We terminate the process
		self.process.terminate()
	
		# Compute average temperature
		temps = []
		while not self.queue.empty():
        		temps.append(self.queue.get())
	
		avgTemp = sum(temps) / len(temps)
		return avgTemp
