# -*- coding: utf-8 -*-

import subprocess
from datetime import datetime

SERVERS = {
	"trident1.vlab.cs.hioa.no" : "128.39.120.89",
	"trident2.vlab.cs.hioa.no" : "128.39.120.90",
	"trident3.vlab.cs.hioa.no" : "128.39.120.91"
}

SERVER_MESSAGE = {
	"trident1.vlab.cs.hioa.no" : 0.0,
	"trident2.vlab.cs.hioa.no" : 0.0,
	"trident3.vlab.cs.hioa.no" : 0.0
}

SERVER_PLOT_DATA = {
	"hostTemp" : 0.0,
	"numVms" : 0,
	"vmLoads" : { 
		"25"  : 0,
		"50"  : 0,
		"75"  : 0,
		"100" : 0
	}
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
		"load" : 0,
		"deltaTemp" : 0.0
	}
}

class DeltaTemp():
	def __init__(self):
		self._started_at = datetime.now()
		self.deltaTemp = 56.0

	def __call__(self):
		time_passed = datetime.now() - self._started_at
		if time_passed.total_seconds() > 120:
			self._started_at = datetime.now()
			if self.deltaTemp > 24.0:
				 self.deltaTemp -= 1.0
		return self.deltaTemp
deltaTemp = DeltaTemp()

# Get server temperature
def getHostTemp():
	try:
		temp_str = subprocess.check_output("sensors | grep 'temp1' | awk '{print $2}' | cut -c 2- | rev | cut -c 4- | rev", shell=True).decode('UTF-8').splitlines()
		temp_float = [float(temp) for temp in temp_str]
		return sum(temp_float)
	except subprocess.CalledProcessError as e:
		print("ERROR: : {reason}".format(reason=e))
	return 0.0

# Get server full hostname
def getHostName():
	try:
		host = subprocess.check_output("hostname --all-fqdns", shell=True).decode('UTF-8').rstrip(" \n")
		return host
	except subprocess.CalledProcessError as e:
		print("ERROR: : {reason}".format(reason=e))
	return ""

# Get Host IP from hostname
def getIpFromHostName(host):
	ip = ""
	if host in SERVERS:
		ip = SERVERS[host]	
	return ip	

# Get Host name from hostIp
def getHostNameFromIp(ip):
	host = ""
	for key, value in SERVERS.items():
		if(ip == value):
			host = key
			break
	return host

# Migrate VM
def migrateVm(vm, target):
	try:
		cmd = "virsh migrate --live %s qemu+ssh://%s/system --undefinesource --persistent" % (vm, target)
		subprocess.check_call(cmd, shell=True)
	except subprocess.CalledProcessError as e:
		print("ERROR: : {reason}".format(reason=e))

# get list of vms logged in
def getVmsLoggedin():
	try:
		vms = subprocess.check_output("virsh list | awk '{ print $2 }' | tail -n +3 | head -n -1", shell=True).decode('UTF-8').splitlines()
		return list(vms)
	except subprocess.CalledProcessError as e:
		print("ERROR: : {reason}".format(reason=e))
	return []

# Get VM name from MAC Address
def getVmName(mac):
	vms = getVmsLoggedin()
	for vm in vms:
		try:
			vm_mac = subprocess.check_output("virsh domiflist %s | awk '{ print $5 }' | tail -n +3 | head -n -1" % (vm), shell=True).decode('UTF-8').rstrip("\n")
			if(mac == vm_mac): return vm
		except subprocess.CalledProcessError as e:
			print("ERROR: : {reason}".format(reason=e))
	return ""

# Get number of VMs running on the host
def getNumberOfVms():
	return len(getVmsLoggedin())

# Get number of NUMA nodes
def getNumberOfNodes():
	try:
		numOfNodes = subprocess.check_output("numactl --hardware | grep 'nodes' | awk '{print $2}'", shell=True).decode('UTF-8').rstrip('\n')
		return int(numOfNodes)
	except subprocess.CalledProcessError as e:
		print("ERROR: : {reason}".format(reason=e))
	return 1
