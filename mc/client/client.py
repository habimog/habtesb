#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

import socket
import json
import time
import random
from copy import deepcopy
from utils import *

''' Client
'''
class Client(object):
	def __init__(self):
		self.client_message = deepcopy(CLIENT_MESSAGE)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.port = 10000
		self.login = True
		self.delta = 0.0
		self.load = 0

	def run(self):
		# Send Client status
		hostName, ip, mac, load = self._sendStatus()
		time.sleep(600)
		while True:
			# Update Client status
			hostName, ip, mac, load = self._sendStatus()

			# Wake VM randomly
			rand_time = random.randint(30, 120)
			print("Rand Time = {}".format(rand_time))
			time.sleep(rand_time)

			try:
				# Request Temperature
				self.client_message["request"]["login"] = False
				self.client_message["request"]["temperature"] = True
				self.client_message["request"]["migration"] = False
				self.client_message["vm"]["mac"] = mac
				self.client_message["vm"]["target"] = hostName
				self.client_message["vm"]["load"] = load
				self.sock.sendto(json.dumps(self.client_message).encode('utf-8'), (ip, self.port))
				print("sent: {}".format(self.client_message))

				# Receive response
				print("waiting to receive Temperature request")
				self.sock.settimeout(5.0)
				data, server = self.sock.recvfrom(512)
				self.sock.settimeout(None)
				server_message = json.loads(data.decode('utf-8'))
				print("received: {} from {}".format(server_message, server))

				# Process and make a decision
				try:
					hostTemp = server_message[hostName]
					avgTemp = sum(server_message.values()) / len(server_message)
					migrate = True if hostTemp > (avgTemp + self.delta) else False
					print("migrate? {}, AvgTemp = {}, HostTemp = {}".format(migrate, avgTemp, hostTemp))

					# Update Login request
					self.login = migrate

					if(migrate):
						# Determine destination
						if hostName in server_message:
							del server_message[hostName]
						destination = min(server_message, key=server_message.get)

						# Send Migration Request
						self.client_message["request"]["login"] = False
						self.client_message["request"]["migration"] = True
						self.client_message["request"]["temperature"] = False
						self.client_message["vm"]["mac"] = mac
						self.client_message["vm"]["target"] = destination
						self.client_message["vm"]["load"] = load
						self.sock.sendto(json.dumps(self.client_message).encode('utf-8'), (ip, self.port))
						print("sent: {} to {}".format(self.client_message, destination))
			
						# Sleep for 30 sec, for migration to complete
						time.sleep(30)
				except:
					print("An unexpected error occurred")
			except:
				print("Socket timeout")

	def _sendStatus(self):
		# Get client data
		hostName = getHostName()
		ip = getHostIp(hostName)
		mac = getVmMac()
		load = getLoad()
		print('VM is on host: {}, ip: {} port: {}'.format(hostName, ip, self.port))
		print('Load: {}, Load Changed: {}'.format(load, self.load != load))

		# Send Login request/Load change notification
		loadChanged = (self.load != 0) and (self.load != load)
		if(self.login or loadChanged):
			self.load = load
			acked = False
			while not acked:
				try:
					# Send Request
					self.client_message["request"]["login"] = True
					self.client_message["request"]["temperature"] = False
					self.client_message["request"]["migration"] = False
					self.client_message["vm"]["mac"] = mac
					self.client_message["vm"]["target"] = hostName
					self.client_message["vm"]["load"] = load
					self.sock.sendto(json.dumps(self.client_message).encode('utf-8'), (ip, self.port))
					print("sent: {}".format(self.client_message))
				
					# Receive response
					print("waiting to receive login request")
					self.sock.settimeout(5.0)
					data, server = self.sock.recvfrom(512)
					self.sock.settimeout(None)
					client_message = json.loads(data.decode('utf-8'))
					self.delta = client_message["vm"]["deltaTemp"]
					print("received: {} from {}".format(client_message, server))
					acked = True
				except:
					print("Login Request Socket Timed out, Retry ...")
					acked = False
					time.sleep(30)

				# Pause for 10min if Load changed
			if loadChanged:
				print("Load Changed, Pause for 10 minutes.")
				time.sleep(600)
		return hostName, ip, mac, load				

'''
	Main
'''
if __name__ == "__main__":
	Client().run()
	
