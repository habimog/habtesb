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
	def __init__(self, initialTemp):
		# Calibration temperature
		self.calibrationTemp = initialTemp
		self.deltaTemp = deltaTemp()

		# Register Signal Handler
		signal.signal(signal.SIGINT, self._signal_handler)

		# Server message containing the temperature of all the servers and delta temperature
		self.server_message = deepcopy(SERVER_MESSAGE)
		
		# List of VMs running on server with their corresponging load
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
		# Handle login
		loginThread = threading.Thread(target=self._handleLogin)
		loginThread.start()
		
		# Handle plot
		plotThread = threading.Thread(target=self._handlePlot)
		plotThread.start()
		
		# Handle server
		serverThread = threading.Thread(target=self._handleServer)
		serverThread.start()

		# Handle client
		clientThread = threading.Thread(target=self._handleClient)
		clientThread.start()

		clientThread.join()
		serverThread.join()
		plotThread.join()
		loginThread.join()

	def _handleLogin(self):
		while True:
			logging.debug("---------------------- handleLogin ---------------")
			
			try:
				# Delete VMs Loggedout
				vms = getVmsLoggedin()
				self.my_mutex.acquire()
				loggedoutVms = [vm for vm in self.vms if vm not in vms]
				for vm in loggedoutVms:
					logging.info("VM: {} Loggedout".format(vm))
					del self.vms[vm]
				logging.debug("Logged in clients = {}".format(self.vms))
				
				# Update deltaTemp
				self.deltaTemp = deltaTemp()
				logging.debug("Updated deltaTemp = {}".format(self.deltaTemp))
				self.my_mutex.release()
			except:
				logging.error("Exception in HandleLogin thread")
			time.sleep(15)

	def _handlePlot(self):
		while True:
			logging.debug("---------------------- handlePlot ---------------")
			logging.info("waiting to receive server plot data request")
			data, address = self.plot_socket.recvfrom(1024)
			logging.info("Received server plot data request")

			# Server plot data
			try:
				plotData = deepcopy(SERVER_PLOT_DATA)
				host = getHostName()

				self.my_mutex.acquire()
				plotData["hostTemp"] = self.server_message[host] / getNumberOfNodes()
				plotData["numVms"] = getNumberOfVms()
				for vm, load in self.vms.items():
					plotData["vmLoads"][str(load)] += 1
				self.my_mutex.release()

				sent = self.plot_socket.sendto(json.dumps(plotData).encode('utf-8'), address)
				logging.info("Sent {} to {}".format(plotData, address))
			except:
				logging.error("Exception in HandlePlot thread")
		
	def _handleServer(self):
		while True:
			logging.debug("---------------------- handleServer ---------------")
			time.sleep(2)

			try:
				host = getHostName()
				servers = list(SERVERS.keys())
				servers.remove(str(host))
				hostTemp = getHostTemp() - self.calibrationTemp
				logging.debug("Host temerature = {}".format(hostTemp))
				
				self.my_mutex.acquire()
				self.server_message[host] = hostTemp if hostTemp >= 0.0 else 0.0
				for server in servers:
					server_address = (getIpFromHostName(server), self.server_port)
					sent = self.server_socket.sendto(json.dumps(self.server_message).encode('utf-8'), server_address)
					logging.info("Sent {} to {}".format(self.server_message, server_address))
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
						logging.error("Server socket timeout for: {}".format(server))
			except:
				logging.error("Exception in HandleServer thread")

	def _handleClient(self):
		while True:
			logging.debug("---------------------- handleClient ---------------")
			
			# Get VM message
			logging.debug("Waiting to receive client messages")
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
						# Register VM Load
						if str(vmLoad) in SERVER_PLOT_DATA["vmLoads"]:
							logging.info("Added VM: {} Load: {}".format(vm, vmLoad))
							self.my_mutex.acquire()
							self.vms[vm] = vmLoad
							client_message["vm"]["deltaTemp"] = self.deltaTemp
							self.my_mutex.release()

							# Send Response
							sent = self.client_socket.sendto(json.dumps(client_message).encode('utf-8'), address)
							logging.info("Sent {} back to {}".format(client_message, address))
						else:
							logging.error("VM Load not in SERVER_PLOT_DATA")
					elif client_message["request"]["temperature"]:
						# Send Response
						self.my_mutex.acquire()
						sent = self.client_socket.sendto(json.dumps(self.server_message).encode('utf-8'), address)
						logging.info("Sent {} back to {}".format(self.server_message, address))

						# Update VM Load
						if str(vmLoad) in SERVER_PLOT_DATA["vmLoads"]:
							logging.info("Updated VM: {} Load: {}".format(vm, vmLoad))
							self.vms[vm] = vmLoad
						else:
							logging.error("VM Load not in SERVER_PLOT_DATA")
						self.my_mutex.release()
					elif client_message["request"]["migration"]:
						# Migrate VM
						target = client_message["vm"]["target"]
						migrationThread = threading.Thread(target=migrateVm, args=[vm, target])
						migrationThread.setDaemon(True)
						migrationThread.start()
						migrationThread.join()
						logging.debug("migrated {} to {}".format(vm, target))

						# Delete VM Load
						self.my_mutex.acquire()
						if vm in self.vms:
							logging.info("Deleted VM: {} Load: {}".format(vm, self.vms[vm]))
							del self.vms[vm]
						self.my_mutex.release()
					else:
						logging.error("Wrong VM Request Message")
				else:
					logging.error("VM Domain-Name did not deduced correctly")
			except:
				logging.error("Exception in HandleClient thread")

'''
	Main
'''
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

