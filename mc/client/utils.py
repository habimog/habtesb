import subprocess
from uuid import getnode as get_mac

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
		host = subprocess.check_output("sudo traceroute %s | tail -n+2 | awk '{ print $2 }' | head -1" % (value), shell=True).decode('UTF-8').rstrip("\n")
		print("host = {} key = {} value = {}".format(host, key, value))
		if(host in SERVERS):
			hostName = host
			break
		elif(host == "*" or host != "192.168.122.1"):
			print("host deduced to be = {}".format(key))
			hostName = key

	return hostName

def getHostIp(hostName):
	hostIp = ""
	if hostName in SERVERS:
		hostIp = SERVERS[hostName]
	
	return hostIp

def getVmMac():
	mac = get_mac()
	return ':'.join(("%012x" % mac)[i:i+2] for i in range(0, 12, 2))

def getLoad():
	load = subprocess.check_output("ps | grep stress-ng | head -1 | awk '{print $NF}'", shell=True).decode('UTF-8').rstrip("\n")
	print("Load = {}".format(load))
	
	try:
		return int(load)
	except:
		print("Load not int")
		return 0
		