#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import socket
import json
import time
import random
from copy import deepcopy
from utils import *
from rl import RlAgent

''' Client
'''
class Client(object):
	def __init__(self):
		self.rlAgent = RlAgent()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.port = 10000
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
			# VM wakes randomly
			rand_time = random.randint(60, 180)
			print("Rand Time = {}".format(rand_time))
			time.sleep(rand_time)

			# Choose action
			action = self.rlAgent.takeAction()
			migrate = True if action != self.client_data["hostName"] else False
			print("migrate? = {}, action = {}".format(migrate, action))

			# Migrate
			if(migrate):
				self.client_message["request"]["login"] = False
				self.client_message["request"]["migration"] = True
				self.client_message["request"]["temperature"] = False
				self.client_message["vm"]["mac"] = self.client_data["mac"]
				self.client_message["vm"]["target"] = action
				self.client_message["vm"]["load"] = self.client_data["load"]
				self.client_message["prob"]["trident1.vlab.cs.hioa.no"] = self.rlAgent.prob["trident1"]
				self.client_message["prob"]["trident2.vlab.cs.hioa.no"] = self.rlAgent.prob["trident2"]
				self.client_message["prob"]["trident3.vlab.cs.hioa.no"] = self.rlAgent.prob["trident3"]
				self.sock.sendto(json.dumps(self.client_message).encode('utf-8'), (self.client_data["ip"], self.port))
				print("sent: {} to {}".format(self.client_message, action))
				
				# Sleep for 60 sec, for migration to complete
				time.sleep(60)
			else:
				print("VM choose to stay")

			try:
				# Update Client status
				self._getClientData()
				
				# Request Temperature 
				self.client_message["request"]["login"] = False
				self.client_message["request"]["temperature"] = True
				self.client_message["request"]["migration"] = False
				self.client_message["vm"]["mac"] = self.client_data["mac"]
				self.client_message["vm"]["target"] = self.client_data["hostName"]
				self.client_message["vm"]["load"] = self.client_data["load"]
				self.client_message["prob"]["trident1.vlab.cs.hioa.no"] = self.rlAgent.prob["trident1"]
				self.client_message["prob"]["trident2.vlab.cs.hioa.no"] = self.rlAgent.prob["trident2"]
				self.client_message["prob"]["trident3.vlab.cs.hioa.no"] = self.rlAgent.prob["trident3"]
				self.sock.sendto(json.dumps(self.client_message).encode('utf-8'), (self.client_data["ip"], self.port))
				print("sent: {}".format(self.client_message))

				# Receive response
				print("waiting to receive")
				self.sock.settimeout(15.0)
				data, server = self.sock.recvfrom(1024)
				self.sock.settimeout(None)
				server_message = json.loads(data.decode('utf-8'))
				print("received: {} from {}".format(server_message, server))
			
				# Learn
				maxTemp = server_message["maxTemp"]
				hostTemp = server_message["hostTemp"]
				self.rlAgent.learn(action, maxTemp, hostTemp)
			except:
				print("Socket timeout")	

	def _getClientData(self):
		# Send client data request
		while True:
			try:
				# Get client data
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
				self.client_message["prob"]["trident1.vlab.cs.hioa.no"] = self.rlAgent.prob["trident1"]
				self.client_message["prob"]["trident2.vlab.cs.hioa.no"] = self.rlAgent.prob["trident2"]
				self.client_message["prob"]["trident3.vlab.cs.hioa.no"] = self.rlAgent.prob["trident3"]
				self.sock.sendto(json.dumps(self.client_message).encode('utf-8'), (self.client_data["ip"], self.port))
				print("sent: {}".format(self.client_message))
			
				# Receive response
				print("waiting to receive login request")
				self.sock.settimeout(15.0)
				data, server = self.sock.recvfrom(1024)
				self.sock.settimeout(None)
				server_message = json.loads(data.decode('utf-8'))
				print("received: {} from {}".format(server_message, server))
				break
			except:
				print("Login Request Socket Timed out, Retrying ...")
				time.sleep(30)

''' 
	Main
'''
if __name__ == "__main__":
	Client().run()
