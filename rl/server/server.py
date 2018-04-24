#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import json
import threading
import time
import signal
import sys
import logging
from utils import *
import calibrate

logging.basicConfig(filename="/var/tmp/server.log",
	level=logging.DEBUG,
	format="%(asctime)s:%(levelname)s:%(message)s")

''' Server
'''
class Server():
	def __init__(self, initialTemp, maxTemp):
		# Calibration temperature 
		self.calibrationTemp = initialTemp

		# Register Signal Handler 
		signal.signal(signal.SIGINT, self._signal_handler)

		# Server message containing max and host temperature
		self.server_message = {"maxTemp" : maxTemp, "hostTemp" : 0.0} 

		# Create a UDP socket and bind the socket to the port
		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.plot_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
		self.client_port = 10000
		self.plot_port = 10002
		
		self.client_socket.bind(("", self.client_port))
		self.plot_socket.bind(("", self.plot_port))

	def _signal_handler(self, signal, frame):
		logging.info('Signal Interrupt Caught!')
		self.client_socket.close()
		self.plot_socket.close()
		sys.exit(0)

	def __del__(self):
		logging.debug("Server Exited")

	def run(self):
		# Handle plot
		plotThread = threading.Thread(target=self._handlePlot)
		plotThread.start()

		# Handle client
		clientThread = threading.Thread(target=self._handleClient)
		clientThread.start()

		clientThread.join()
		plotThread.join()

	def _handlePlot(self):
		while True:
			logging.debug("---------------------- handlePlot ---------------")
			logging.info("waiting to receive server plot data request")
			data, address = self.plot_socket.recvfrom(512)

			# Server plot data
			logging.info("Received server plot data request")
			plotData = {} #SERVER_PLOT_DATA
			hostTemp = (getHostTemp() - self.calibrationTemp) / getNumberOfNodes()
			plotData["hostTemp"] = hostTemp if hostTemp >= 0.0 else 0.0
			plotData["numVms"] = getNumberOfVms()

			sent = self.plot_socket.sendto(json.dumps(plotData).encode('utf-8'), address)
			logging.info("Sent {} to {}".format(plotData, address))

	def _handleClient(self):
		while True:
			logging.debug("---------------------- handleClient ---------------")
			logging.debug("Waiting to receive client message")
			
			data, address = self.client_socket.recvfrom(512)
			client_message = json.loads(data.decode('utf-8'))
			logging.info("Received {} from {}".format(client_message, address))

			if client_message["request"]["temperature"]:
				logging.debug("Received Temperature request client message")
				hostTemp = getHostTemp() - self.calibrationTemp
				self.server_message["hostTemp"] = hostTemp if hostTemp >= 0.0 else 0.0
				
				sent = self.client_socket.sendto(json.dumps(self.server_message).encode('utf-8'), address)
				logging.info("Sent {} back to {}".format(self.server_message, address))
			elif client_message["request"]["migration"]:
				logging.debug("Received Migration request client message")
				vm = getVmName(client_message["vm"]["mac"])
				target = client_message["vm"]["target"]
				
				# MigrateVm
				migrationThread = threading.Thread(target=migrateVm, args=[vm, target])
				migrationThread.setDaemon(True)
				migrationThread.start()
				migrationThread.join()
				
				logging.debug("migrated {} to {}".format(vm, target))
			else:
				logging.error("ERROR")

''' Main
'''
if __name__ == "__main__":
	# Clear Log Content 
	with open('/var/tmp/server.log','w'): pass
	
	# Get calibration temperature 
	initialTemp = calibrate.Calibrate(600).getCalibrationTemp() 
	maxTemp = 360
	logging.info("Initial Average Host Temperature = {} and maxTemp = {}".format(initialTemp, maxTemp))

	# Start Server 
	Server(initialTemp, maxTemp).run()
