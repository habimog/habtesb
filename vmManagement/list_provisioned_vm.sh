#!/bin/bash

# Collect provisioned vms
vms=$(virsh list | awk '{ print $2 }'| tail -n +3)

#Get mac address and IP address of running VMs
echo "---------------List of Provisioned VMs-----------------"
for vm in $vms
do
	mac=$(virsh domiflist $vm | awk '{ print $5 }'| tail -n +3)
	ip=$(arp -an | grep $mac | awk '{ gsub(/[\(\)]/,"",$2); print $2 }')
	echo "$vm has MAC Address $mac and IP Address $ip"
done
