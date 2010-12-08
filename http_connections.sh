#!/bin/bash

# Cloudkick plugin to count number of http connections.  
# Alerts if no clients and/or no listeners.

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <lo@petalphile.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return 
# ----------------------------------------------------------------------------

if [ "$1" = "help" ]; then
	echo "CloudKick check to return established, connected, and idle users, and ensure there is a listener (critical if there is not)
usage: $0 <threshold|help>
where 
	help prints this message
	threshold is the number of minimum users.  Below this number is a critical alert.
	if no argument, threshold is 1."
	exit
else
	if [ "$1" ]; then
		THRESHOLD=$1
	else
		THRESHOLD=1
	fi
fi 

NOW=`netstat -ano |grep :80`;
SIMULTANEOUS=`echo "$NOW" |grep -c :80`
ACTIVE=`echo "$NOW" |grep -c ESTABLISHED`
IDLE=`echo "$NOW" |grep -c TIME_WAIT`
#remove the listener
SIMULTANEOUS=$(($SIMULTANEOUS - 1))
if [ $SIMULTANEOUS -lt $THRESHOLD ]; then
	if [ $SIMULTANEOUS -lt 0 ]; then
		echo "status err no server listening!"
		exit
	else
		echo "status critical less than $THRESHOLD users connected!";
	fi
else
	echo "status ok ok";
fi
echo "metric http_users int $SIMULTANEOUS";
echo "metric http_users_active int $ACTIVE";
echo "metric http_users_idle int $IDLE";

