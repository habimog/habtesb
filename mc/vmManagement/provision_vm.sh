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

# Provision new VMs
if [ $# -ne 1 ]; then
	echo "Error: One Argument Expected"
	exit 3
else
	if [ "$1" -eq "$1" 2> /dev/null ]; then
		if [ $1 -ge 0 ]; then
			for n in `seq $1`
			do
				virt-install --name=vm"${n}" --cdrom=/var/lib/libvirt/images/ezremaster.iso --virt-type=kvm --os-type=linux --ram=256 --network bridge=virbr0 --nodisk --graphics=none --noautoconsole
				echo "------------------------- VM$n Provisioned! -------------------------"
			done	
		else
			echo "You should Enter a Positive Integer"
			exit 2
		fi
	else
		echo "You Should Enter an Integer"
		exit 1
	fi
fi
