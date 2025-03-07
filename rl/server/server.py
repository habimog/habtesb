#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import json
import threading
import time
import sys
import os
import signal
import logging
from copy import deepcopy

from utils import *
import calibrate

logging.basicConfig(filename="/var/tmp/server.log",
	level=logging.DEBUG,
	format="%(asctime)s:%(levelname)s:%(message)s")

''' Server
'''
class Server(object):
	def __init__(self, initialTemp, maxTemp):
		# Calibration temperature 
		self.calibrationTemp = initialTemp

		# Register Signal Handler 
		signal.signal(signal.SIGINT, self._signal_handler)

		# Server message containing max and host temperature
		self.server_message = deepcopy(SERVER_MESSAGE) 
		self.server_message["maxTemp"] = maxTemp 

		# List of VMs running on server with their corresponging load
		self.vms = {} 

		# Python create mutex
		self.my_mutex = threading.Lock()

		# Create a UDP socket and bind the socket to the port
		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.plot_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
		# Ports
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
		# Handle login
		loginThread = threading.Thread(target=self._handleLogin)
		loginThread.start()

		# Handle plot
		plotThread = threading.Thread(target=self._handlePlot)
		plotThread.start()

		# Handle client
		clientThread = threading.Thread(target=self._handleClient)
		clientThread.start()

		clientThread.join()
		plotThread.join()
		loginThread.join()

	def _handleLogin(self):
		while True:
			logging.debug("---------------------- handleLogin ---------------")
			
			# Delete VMs Loggedout
			try:
				vms = getVmsLoggedin()
				self.my_mutex.acquire()
				loggedoutVms = [vm for vm in self.vms if vm not in vms]
				for vm in loggedoutVms:
					logging.info("VM: {} Loggedout".format(vm))
					del self.vms[vm]
				self.my_mutex.release()
				logging.debug("Logged in clients = {}".format(self.vms))
			except:
				logging.error("Exception in HandleLogin thread")
			time.sleep(15)

	def _handlePlot(self):
		while True:
			logging.debug("---------------------- handlePlot ---------------")
			logging.info("waiting to receive server plot data request")
			data, address = self.plot_socket.recvfrom(4096)
			logging.info("Received server plot data request")

			# Server plot data
			try:
				plotData = deepcopy(SERVER_PLOT_DATA)
				hostTemp = (getHostTemp() - self.calibrationTemp) / getNumberOfNodes()
				plotData["hostTemp"] = hostTemp if hostTemp >= 0.0 else 0.0
				plotData["numVms"] = getNumberOfVms()

				self.my_mutex.acquire()
				for vm, value in self.vms.items():
					plotData["vmLoads"][str(value["load"])] += 1
					plotData["vms"].append(self.vms[vm])
				self.my_mutex.release()

				sent = self.plot_socket.sendto(json.dumps(plotData).encode('utf-8'), address)
				logging.info("Sent {} to {}".format(plotData, address))
			except:
				logging.error("Exception in HandlePlot thread")

	def _handleClient(self):
		while True:
			logging.debug("---------------------- handleClient ---------------")
			
			# Get VM message
			logging.debug("Waiting to receive client message")
			data, address = self.client_socket.recvfrom(1024)
			client_message = json.loads(data.decode('utf-8'))
			logging.info("Received {} from {}".format(client_message, address))

			try:
				# Get VM Domain Name
				vm = getVmName(client_message["vm"]["mac"]) 
				vmLoad = client_message["vm"]["load"]

				# Process Client Message
				if vm != "":
					if client_message["request"]["login"]:
						# Register VM
						if str(vmLoad) in SERVER_PLOT_DATA["vmLoads"]:
							logging.info("Added VM: {} Load: {}".format(vm, vmLoad))
							self.my_mutex.acquire()
							self.vms[vm] = {
								"vm" : vm,
								"load" : vmLoad,
								"prob" : client_message["prob"]
							}
							self.my_mutex.release()

							# Send Response
							sent = self.client_socket.sendto(json.dumps(client_message).encode('utf-8'), address)
							logging.info("Sent {} back to {}".format(client_message, address))
						else:
							logging.error("VM Load not in SERVER_PLOT_DATA")
					elif client_message["request"]["temperature"]:
						# Send Response
						hostTemp = getHostTemp() - self.calibrationTemp
						self.server_message["hostTemp"] = hostTemp if hostTemp >= 0.0 else 0.0
						sent = self.client_socket.sendto(json.dumps(self.server_message).encode('utf-8'), address)
						logging.info("Sent {} back to {}".format(self.server_message, address))
					
						# Update VM Load
						self.my_mutex.acquire()
						if str(vmLoad) in SERVER_PLOT_DATA["vmLoads"]:
							logging.info("Updated VM: {} Load: {}".format(vm, vmLoad))
							self.vms[vm]["vm"] = vm
							self.vms[vm]["load"] = vmLoad
							self.vms[vm]["prob"] = client_message["prob"]
						else:
							logging.error("VM Load not in SERVER_PLOT_DATA")
						self.my_mutex.release()
					elif client_message["request"]["migration"]:
						# MigrateVm
						target = client_message["vm"]["target"]
						migrationThread = threading.Thread(target=migrateVm, args=[vm, target])
						migrationThread.setDaemon(True)
						migrationThread.start()
						migrationThread.join()
						logging.debug("migrated {} to {}".format(vm, target))
					
						# Delete VM Load
						self.my_mutex.acquire()
						if vm in self.vms:
							logging.info("Deleted VM: {} Load: {}".format(vm, self.vms[vm]["load"]))
							del self.vms[vm]
						self.my_mutex.release()
					else:
						logging.error("Wrong VM Request Message")
				else:
					logging.error("VM Domain-Name did not deduced correctly")
			except:
				logging.error("Exception in HandleClient thread")

''' Main
'''
if __name__ == "__main__":
	# Clear Log Content 
	with open('/var/tmp/server.log','w'): pass
	
	# Get calibration temperature 
	initialTemp = calibrate.Calibrate(600).getCalibrationTemp() 
	maxTemp = 250 # for 10 VMs @100% load
	logging.info("Initial Average Host Temperature = {} and maxTemp = {}".format(initialTemp, maxTemp))

	# Start Server 
	Server(initialTemp, maxTemp).run()
