# -*- coding: utf-8 -*-

import subprocess

SERVERS = {
	"trident1.vlab.cs.hioa.no" : "128.39.120.89",
	"trident2.vlab.cs.hioa.no" : "128.39.120.90",
	"trident3.vlab.cs.hioa.no" : "128.39.120.91"
}

CLIENT_MESSAGE = {
	"request" : {
		"login" : False,
		"temperature" : False,
		"migration" : False
	},
	"vm" : {
		"mac" : "",
		"target" : "",
		"load" : 0
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
		cmd = "sudo traceroute -n %s | tail -n+2 | awk '{ print $2 }' | wc -l" % (value)	
		if(int(subprocess.check_output(cmd, shell=True).decode('UTF-8').rstrip("\n")) == 1):
			hostName = key
			break
	return hostName

def getHostIp(hostName):
	hostIp = ""
	if hostName in SERVERS:
		hostIp = SERVERS[hostName]
	return hostIp

def getVmMac():
	mac = subprocess.check_output("sudo ifconfig | grep 'HWaddr' | awk '{print $NF}'", shell=True).decode('UTF-8').rstrip("\n")
	return mac.lower()

def getLoad():
	load = subprocess.check_output("sudo ps | grep stress-ng | head -1 | awk '{print $NF}'", shell=True).decode('UTF-8').rstrip("\n")
	print("Load = {}".format(load))
	return load
		
