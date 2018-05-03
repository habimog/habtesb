#!/usr/local/bin/python3.4
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
		self.client_message = deepcopy(CLIENT_MESSAGE)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.port = 10000
		self.login = True
		self.load = 0

	def run(self):
		time.sleep(120)
		# Send Client status
		hostName, ip, mac, load = self._sendStatus()

		while True:
			# VM wakes randomly
			rand_time = random.randint(60, 180)
			print("VM wakes after = {} sec".format(rand_time))
			time.sleep(rand_time)

			# Choose action
			action = self.rlAgent.takeAction()
			migrate = True if action != hostName else False
			print("migrate? = {}, action = {}".format(migrate, action))

			# Update Login request
			self.login = migrate

			# Migrate
			if(migrate):
				self.client_message["request"]["login"] = False
				self.client_message["request"]["migration"] = True
				self.client_message["request"]["temperature"] = False
				self.client_message["vm"]["mac"] = mac
				self.client_message["vm"]["target"] = action
				self.client_message["vm"]["load"] = load
				self.client_message["prob"]["trident1.vlab.cs.hioa.no"] = self.rlAgent.prob["trident1"]
				self.client_message["prob"]["trident2.vlab.cs.hioa.no"] = self.rlAgent.prob["trident2"]
				self.client_message["prob"]["trident3.vlab.cs.hioa.no"] = self.rlAgent.prob["trident3"]
				self.sock.sendto(json.dumps(self.client_message).encode('utf-8'), (ip, self.port))
				print("sent: {} to {}".format(self.client_message, action))
				
				# Sleep for 30 sec, for migration to complete
				time.sleep(30)
			else:
				print("VM choose to stay")

			try:
				# Send Client status
				hostName, ip, mac, load = self._sendStatus()
				
				# Request Temperature 
				self.client_message["request"]["login"] = False
				self.client_message["request"]["temperature"] = True
				self.client_message["request"]["migration"] = False
				self.client_message["vm"]["mac"] = mac
				self.client_message["vm"]["target"] = hostName
				self.client_message["vm"]["load"] = load
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

	def _sendStatus(self):
		# Get client data
		hostName = getHostName()
		ip = getHostIp(hostName)
		mac = getVmMac()
		load = getLoad()
		print('VM is at: {}, on {}'.format(hostName, (ip, self.port)))
		print('Load: {}, Load Changed: {}'.format(load, self.load != load))

		# Send Login request / Load change notification
		if(self.login or self.load != load):
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
					self.client_message["prob"]["trident1.vlab.cs.hioa.no"] = self.rlAgent.prob["trident1"]
					self.client_message["prob"]["trident2.vlab.cs.hioa.no"] = self.rlAgent.prob["trident2"]
					self.client_message["prob"]["trident3.vlab.cs.hioa.no"] = self.rlAgent.prob["trident3"]
					self.sock.sendto(json.dumps(self.client_message).encode('utf-8'), (ip, self.port))
					print("sent: {}".format(self.client_message))
				
					# Receive response
					print("waiting to receive login request")
					self.sock.settimeout(5.0)
					data, server = self.sock.recvfrom(512)
					self.sock.settimeout(None)
					server_message = json.loads(data.decode('utf-8'))
					print("received: {} from {}".format(server_message, server))
					acked = True
				except:
					print("Login Request Socket Timed out, Retrying ...")
					acked = False
					time.sleep(30)
		return hostName, ip, mac, load

''' 
	Main
'''
if __name__ == "__main__":
	Client().run()
