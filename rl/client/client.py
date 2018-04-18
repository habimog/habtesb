#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

import socket
import json
import time
import random

from utils import *
from rl import RlAgent

''' Client
'''
class Client():
	def __init__(self):
		self.client_message = CLIENT_MESSAGE
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.port = 10000
		self.rlAgent = RlAgent()

	def run(self):
		while True:
			# VM wakes randomly
			rand_time = random.randint(60, 180)
			print("VM wakes after = {} sec".format(rand_time))
			time.sleep(rand_time)

			# Get host name and ip
			hostName = getHostName()
			ip = getHostIp(hostName)
			print('VM is on host: {}, ip: {}, port: {}'.format((hostName, ip, self.port)))

			# Choose action
			action = self.rlAgent.takeAction()
			migrate = True if action != hostName else False
			print("migrate = {}, action = {}".format(migrate, action))

			# Migrate
			if(migrate):
				self.client_message["request"]["migration"] = True
				self.client_message["request"]["temperature"] = False
				self.client_message["vm"]["mac"] = getVmMac()
				self.client_message["vm"]["target"] = action
				self.sock.sendto(json.dumps(self.client_message).encode('utf-8'), (ip, self.port))
				print("sent: {} to {}".format(self.client_message, action))
				
				# Sleep for 30 sec, for migration to complete
				time.sleep(30)

				# Update host name and ip
				hostName = getHostName()
				ip = getHostIp(hostName)
				print('VM is on: {}'.format((ip, self.port)))
			else:
				print("VM choose to stay")

			try:
				# Request Temperature 
				self.client_message["request"]["temperature"] = True
				self.client_message["request"]["migration"] = False
				self.client_message["vm"]["mac"] = ""
				self.client_message["vm"]["target"] = ""
				self.client_message["prob"]["trident1.vlab.cs.hioa.no"] = self.rlAgent.prob["trident1"]
				self.client_message["prob"]["trident2.vlab.cs.hioa.no"] = self.rlAgent.prob["trident2"]
				self.client_message["prob"]["trident3.vlab.cs.hioa.no"] = self.rlAgent.prob["trident3"]
				self.sock.sendto(json.dumps(self.client_message).encode('utf-8'), (ip, self.port))
				print("sent: {}".format(self.client_message))

				# Receive response
				print("waiting to receive")
				self.sock.settimeout(5.0)
				data, server = self.sock.recvfrom(512)
				self.sock.settimeout(None)
				server_message = json.loads(data.decode('utf-8'))
				print("received: {} from {}".format(server_message, server))
			
				# Learn
				maxTemp = server_message["maxTemp"]
				hostTemp = server_message["hostTemp"]
				self.rlAgent.learn(action, maxTemp, hostTemp)
			except:
				print("Socket timeout")
			

''' Main
'''
if __name__ == "__main__":
	# Start Client 
	Client().run()
