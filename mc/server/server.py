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
from multiprocessing import Process
from copy import deepcopy
from utils import *
import calibrate

logging.basicConfig(filename="/var/tmp/server.log",
	level=logging.DEBUG,
	format="%(asctime)s:%(levelname)s:%(message)s")

# Server
class Server(object):
	def __init__(self, initialTemp):
		# Calibration temperature
		self.calibrationTemp = initialTemp

		# Register Signal Handler
		signal.signal(signal.SIGINT, self._signal_handler)

		# Server message containing the temperature of all the servers
		self.server_message = deepcopy(SERVER_MESSAGE)

		# List of VMs running on server
		self.vms = {} 

		# Python create mutex
		self.my_mutex = threading.Lock()

		# Create a UDP socket and bind the socket to the port
		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.plot_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
		# Ports
		self.client_port = 10000
		self.server_port = 10001
		self.plot_port = 10002

		self.client_socket.bind(("", self.client_port))
		self.server_socket.bind(("", self.server_port))
		self.plot_socket.bind(("", self.plot_port))

	def _signal_handler(self, signal, frame):
		logging.info('Signal Interrupt Caught!')
		self.client_socket.close()
		self.server_socket.close()
		self.plot_socket.close()
		sys.exit(0)

	def __del__(self):
		logging.debug("Server Exited")

	def run(self):
		# Handle plot
		plotThread = threading.Thread(target=self._handlePlot)
		plotThread.start()
		
		# Handle Server
		serverThread = threading.Thread(target=self._handleServer)
		serverThread.start()

		# Handle client
		clientThread = threading.Thread(target=self._handleClient)
		clientThread.start()

		clientThread.join()
		serverThread.join()
		plotThread.join()

	def _handlePlot(self):
		while True:
			logging.debug("---------------------- handlePlot ---------------")
			logging.info("waiting to receive server plot data request")
			data, address = self.plot_socket.recvfrom(512)

			# Server plot data
			logging.info("Received server plot data request")
			plotData = deepcopy(SERVER_PLOT_DATA)
			hostTemp = (getHostTemp() - self.calibrationTemp) / getNumberOfNodes()
			plotData["hostTemp"] = hostTemp if hostTemp >= 0.0 else 0.0
			plotData["numVms"] = getNumberOfVms()

			self.my_mutex.acquire()
			for vm, load in self.vms.items():
				plotData["vmLoads"][str(load)] += 1
			self.my_mutex.release()

			sent = self.plot_socket.sendto(json.dumps(plotData).encode('utf-8'), address)
			logging.info("Sent {} to {}".format(plotData, address))
		
	def _handleServer(self):
		while True:
			logging.debug("---------------------- handleServer ---------------")
			time.sleep(5)

			host = getHostName()
			servers = list(SERVERS.keys())
			servers.remove(str(host))

			# Python acquire mutex
			self.my_mutex.acquire()
			hostTemp = getHostTemp() - self.calibrationTemp
			logging.debug("Host temerature = {}".format(hostTemp))
			self.server_message[host] = hostTemp if hostTemp >= 0.0 else 0.0
			for server in servers:
				server_address = (getIpFromHostName(server), self.server_port)
				sent = self.server_socket.sendto(json.dumps(self.server_message).encode('utf-8'), server_address)
				logging.info("Sent {} to {}".format(self.server_message, server_address))

			# Python release mutex
			self.my_mutex.release()
			
			for server in servers:
				logging.debug("Waiting to receive server message")
				try:
					self.server_socket.settimeout(5.0)
					data, address = self.server_socket.recvfrom(512)
					self.server_socket.settimeout(None)
					server_message = json.loads(data.decode('utf-8'))
					logging.info("Received {} from {}".format(server_message, address))
			
					host = getHostNameFromIp(address[0])
					self.my_mutex.acquire()
					self.server_message[host] = server_message[host]
					self.my_mutex.release()
				except:
					logging.error("Server socket timeout")

	def _handleClient(self):
		while True:
			logging.debug("---------------------- handleClient ---------------")
			logging.debug("Waiting to receive client message")
			
			data, address = self.client_socket.recvfrom(512)
			client_message = json.loads(data.decode('utf-8'))
			logging.info("Received {} from {}".format(client_message, address))

			if client_message["request"]["temperature"]:
				self.my_mutex.acquire()
				
				# Save VM Load
				vm = getVmName(client_message["vm"]["mac"])
				vmLoad = client_message["vm"]["load"]
				if vmLoad != 0:
					self.vms[vm] = vmLoad

				# Send Response
				sent = self.client_socket.sendto(json.dumps(self.server_message).encode('utf-8'), address)
				logging.info("Sent {} back to {}".format(self.server_message, address))
				self.my_mutex.release()
			elif client_message["request"]["migration"]:
				vm = getVmName(client_message["vm"]["mac"])
				target = client_message["vm"]["target"]
				logging.debug("{} and Target {}".format(vm, target))
				
				# Delete VM Load
				self.my_mutex.acquire()
				if vm in self.vms:
					del self.vms[vm]
				self.my_mutex.release()

				# MigrateVm
				migrationThread = threading.Thread(target=migrateVm, args=[vm, target])
				migrationThread.setDaemon(True)
				migrationThread.start()
				migrationThread.join()
			else:
				logging.error("ERROR")


if __name__ == "__main__":
	logging.info("Server Started")

	# Clear Log Content
	with open('/var/tmp/server.log','w'): pass
	
	# Get calibration temperature
	initialTemp = calibrate.Calibrate(600).getCalibrationTemp() 
	logging.info("Initial Average Host Temperature = {}".format(initialTemp))
	print("Initial Average Host Temperature = {}".format(initialTemp))

	# Start the Server
	Server(initialTemp).run()
