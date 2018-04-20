#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import json
import threading
import time
import os
import signal
import logging
from multiprocessing import Process
from utils import *
import calibrate

logging.basicConfig(filename="/var/tmp/plot.log",
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
		self.server_message = {} #SERVER_MESSAGE

		# Python create mutex
		self.my_mutex = threading.Lock()

		# Create a UDP socket and bind the socket to the port
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
		# Port
		self.server_port = 10001

		#print('starting up on {} port {}'.format(*server_address))
		self.server_socket.bind(("", self.server_port))

	def _signal_handler(self, signal, frame):
		logging.info('Signal Interrupt Caught!')
		self.server_socket.close()
		sys.exit(0)

	def __del__(self):
		logging.debug("Server Exited")

	def run(self):

		# Handle Server
		serverThread = threading.Thread(target=self._handleServer)
		serverThread.start()
		serverThread.join()

		
	def _handleServer(self):
		while True:
			logging.debug("---------------------- handleServer ---------------")
			time.sleep(1)

			host = getHostName()
			servers = list(SERVERS.keys())
			servers.remove(str(host))

			# Python acquire mutex: acquire the thread
			# to keep waiting until the lock is released
			self.my_mutex.acquire()
			hostTemp = getHostTemp() - self.calibrationTemp
			logging.debug("Host temerature = {}".format(hostTemp))
			self.server_message[host] = hostTemp if hostTemp >= 0 else 0
			for server in servers:
				server_address = (getIpFromHostName(server), self.server_port)
				sent = self.server_socket.sendto(json.dumps(self.server_message).encode('utf-8'), server_address)
				logging.info("Sent {} to {}".format(self.server_message, server_address))

			# Python release mutex: release the thread
                        # is done, we release the lock
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

	


if __name__ == "__main__":
	# Clear Log Content
	with open('/var/tmp/plot.log','w'): pass
	
	# Get calibration temperature
	initialTemp = calibrate.Calibrate(10).getCalibrationTemp() 
	logging.info("Initial Average Host Temperature = {}".format(initialTemp))

	# Start the server Manager
	Server(initialTemp).run()
