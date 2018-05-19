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
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.port = 10000
		self.delta = 0.0
		self.client_message = deepcopy(CLIENT_MESSAGE)
		self.client_data = {
			"hostName" : "",
			"ip" : "",
			"mac" : "",
			"load" : 0
		}

	def run(self):
		# Get Client data
		self._getClientData()
		
		# Wait 5 minutes
		time.sleep(300)

		while True:
			# Wake VM randomly
			rand_time = random.randint(120, 300)
			print("Rand Time = {}".format(rand_time))
			time.sleep(rand_time)

			# Update Client status
			self._getClientData()

			try:
				# Request Temperature
				self.client_message["request"]["login"] = False
				self.client_message["request"]["temperature"] = True
				self.client_message["request"]["migration"] = False
				self.client_message["vm"]["mac"] = self.client_data["mac"]
				self.client_message["vm"]["target"] = self.client_data["hostName"]
				self.client_message["vm"]["load"] = self.client_data["load"]
				self.sock.sendto(json.dumps(self.client_message).encode('utf-8'), (self.client_data["ip"], self.port))
				print("sent: {}".format(self.client_message))

				# Receive response
				print("waiting to receive Temperature request")
				self.sock.settimeout(15.0)
				data, server = self.sock.recvfrom(1024)
				self.sock.settimeout(None)
				server_message = json.loads(data.decode('utf-8'))
				print("received: {} from {}".format(server_message, server))

				# Process and make a decision
				try:
					hostTemp = server_message[self.client_data["hostName"]]
					avgTemp = sum(server_message.values()) / len(server_message)
					migrate = True if(hostTemp >= (avgTemp + self.delta)) else False
					#migrate = True if((hostTemp > avgTemp) and ((hostTemp - min(server_message.values())) >= self.delta)) else False
					print("migrate? {}, AvgTemp = {}, HostTemp = {}".format(migrate, avgTemp, hostTemp))

					if(migrate):
						# Determine destination
						if self.client_data["hostName"] in server_message:
							del server_message[self.client_data["hostName"]]
						destination = min(server_message, key=server_message.get)

						# Send Migration Request
						self.client_message["request"]["login"] = False
						self.client_message["request"]["migration"] = True
						self.client_message["request"]["temperature"] = False
						self.client_message["vm"]["mac"] = self.client_data["mac"]
						self.client_message["vm"]["target"] = destination
						self.client_message["vm"]["load"] = self.client_data["load"]
						self.sock.sendto(json.dumps(self.client_message).encode('utf-8'), (self.client_data["ip"], self.port))
						print("sent: {} to {}".format(self.client_message, destination))
			
						# Sleep for 60 sec, for migration to complete
						time.sleep(60)
				except:
					print("An unexpected error occurred")
			except:
				print("Socket timeout")

	def _getClientData(self):
		# Send client data request
		while True:
			try:
				# Update client data
				self.client_data["hostName"] = getHostName()
				self.client_data["ip"] = getHostIp(self.client_data["hostName"])
				self.client_data["mac"] = getVmMac()
				self.client_data["load"] = getLoad()
				print('VM is at: {}, on {}'.format(self.client_data["hostName"], (self.client_data["ip"], self.port)))
				
				# Send Request
				self.client_message["request"]["login"] = True
				self.client_message["request"]["temperature"] = False
				self.client_message["request"]["migration"] = False
				self.client_message["vm"]["mac"] = self.client_data["mac"]
				self.client_message["vm"]["target"] = self.client_data["hostName"]
				self.client_message["vm"]["load"] = self.client_data["load"]
				self.sock.sendto(json.dumps(self.client_message).encode('utf-8'), (self.client_data["ip"], self.port))
				print("sent: {}".format(self.client_message))
			
				# Receive response
				print("waiting to receive login request")
				self.sock.settimeout(15.0)
				data, server = self.sock.recvfrom(1024)
				self.sock.settimeout(None)
				client_message = json.loads(data.decode('utf-8'))
				self.delta = client_message["vm"]["deltaTemp"]
				print("received: {} from {}".format(client_message, server))
				break
			except:
				print("Login Request Socket Timed out, Retrying ...")
				time.sleep(30)
		

'''
	Main
'''
if __name__ == "__main__":
	Client().run()
	
