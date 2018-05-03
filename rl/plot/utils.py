# -*- coding: utf-8 -*-

import socket
import json
from copy import deepcopy

SERVERS = {
	"trident1.vlab.cs.hioa.no" : "128.39.120.89",
	"trident2.vlab.cs.hioa.no" : "128.39.120.90",
	"trident3.vlab.cs.hioa.no" : "128.39.120.91"
}

SERVER_PLOT_DATA = {
	"hostTemp" : 0.0,
	"numVms" : 0,
	"vmLoads" : { 
		"25"  : 0,
		"50"  : 0,
		"75"  : 0,
		"100" : 0
	},
	"vms" : []
}

SETER_PLOT_PORT = 10002

TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"

# Get Plot Data
def getPlotData():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_message = {}
	for host, ip in SERVERS.items():
		server_message[host] = deepcopy(SERVER_PLOT_DATA)
		try:
			# Request server plot data 
			sock.sendto(json.dumps(deepcopy(SERVER_PLOT_DATA)).encode('utf-8'), (ip, SETER_PLOT_PORT))
			print("sent server plot data request to {}".format((ip, SETER_PLOT_PORT)))

			# Receive response
			print("waiting to receive")
			sock.settimeout(5.0)
			data, address = sock.recvfrom(512)
			sock.settimeout(None)
			server_message[host] = json.loads(data.decode('utf-8'))
			print("received: {} from {}".format(server_message[host], address))
		except:
			print("Socket timeout for {}".format((ip, SETER_PLOT_PORT)))
			return {}

	return server_message