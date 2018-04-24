#!/bin/bash

# Collect provisioned vms
vms=$(virsh list | awk '{ print $2 }'| tail -n +3)

# Destroy and Undefine VMs
for vm in $vms
do
	virsh destroy "$vm" &> /dev/null&
	virsh undefine "$vm" &> /dev/null&
	echo "$vm Undefined and Destroyed!"
done
