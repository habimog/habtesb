# -*- coding: utf-8 -*-

import subprocess
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
	},
	"prob" : {
		"trident1.vlab.cs.hioa.no" : 0.0,
		"trident2.vlab.cs.hioa.no" : 0.0,
		"trident3.vlab.cs.hioa.no" : 0.0
	}
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
