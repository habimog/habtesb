#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-

import socket
import subprocess
import json
import time
import random
from uuid import getnode as get_mac

SERVERS = {
	"trident1.vlab.cs.hioa.no" : "128.39.120.89",
	"trident2.vlab.cs.hioa.no" : "128.39.120.90",
	"trident3.vlab.cs.hioa.no" : "128.39.120.91"
}

CLIENT_MESSAGE = {
	"request" : {
		"temperature" : False,
		"migration" : False
	},
	"vm" : {
                "mac" : "",
                "target" : ""
        }
}

SERVER_MESSAGE = {
	"trident1.vlab.cs.hioa.no" : 0.0,
	"trident2.vlab.cs.hioa.no" : 0.0,
	"trident3.vlab.cs.hioa.no" : 0.0
}

def getHostName():
	hostName = ""
	for key, value in SERVERS.items():	
		if(int(subprocess.check_output("sudo traceroute -n %s | tail -n+2 | awk '{ print $2 }' | wc -l" % (value), shell=True).decode('UTF-8').rstrip("\n")) == 1):
			hostName = key
			break

	return hostName

def getHostIp(hostName):
	hostIp = ""
	if hostName in SERVERS:
		hostIp = SERVERS[hostName]
	
	return hostIp

def getVmMac():
	mac = get_mac()
	return ':'.join(("%012x" % mac)[i:i+2] for i in range(0, 12, 2))

class Client(object):
	def __init__(self):
		self.client_message = CLIENT_MESSAGE
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.port = 10000

	def run(self):
		while True:
			# VM wakes randomly
			rand_time = random.randint(1, 100)
			print("Rand Time = {}".format(rand_time))
			time.sleep(rand_time)
			
			# Get server ip
			hostName = getHostName()
			ip = getHostIp(hostName)
			#self.sock.bind((ip, self.port))
			print('starting on: {}'.format((ip, self.port)))

			# Send Temperature request
			self.client_message["request"]["temperature"] = True
			self.client_message["request"]["migration"] = False
			self.client_message["vm"]["mac"] = ""
			self.client_message["vm"]["target"] = ""
			print("sending: {}".format(self.client_message))
			self.sock.sendto(json.dumps(self.client_message).encode('utf-8'), (ip, self.port))

			# Receive response
			print("waiting to receive")
			try:
				self.sock.settimeout(100.0)
				data, server = self.sock.recvfrom(512)
				self.sock.settimeout(None)
				server_message = json.loads(data.decode('utf-8'))
				print("received: {} from {}".format(server_message, server))

				# Process and make a decision
				try:
					hostTemp = server_message[hostName]
					avgTemp = sum(server_message.values()) / len(server_message)
					migrate = True if hostTemp > avgTemp else False
					print("migrate? {}, AvgTemp = {}, HostTemp = {}".format(migrate, avgTemp, hostTemp))

					if(migrate):
						# Determine destination
						if hostName in server_message:
							del server_message[hostName]
						destination = min(server_message, key=server_message.get)

						# Send Migration Request
						self.client_message["request"]["migration"] = True
						self.client_message["request"]["temperature"] = False
						self.client_message["vm"]["mac"] = getVmMac()
						self.client_message["vm"]["target"] = destination
						print("sending: {} to {}".format(self.client_message, destination))
						self.sock.sendto(json.dumps(self.client_message).encode('utf-8'), (ip, self.port))
		
						# Sleep for 10 sec, for migration to complete
						time.sleep(10)
				except:
					print("An unexpected error occurred")

			except:
				print("Socket timeout")

'''
	Main
'''
if __name__ == "__main__":
	client = Client()
	client.run()
