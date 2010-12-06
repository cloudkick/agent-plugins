#!/bin/bash

# Cloudkick plugin to count number of http connections.  
# Alerts if no clients and/or no listeners.

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <lo@petalphile.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return 
# ----------------------------------------------------------------------------


NOW=`netstat -ano |grep :80`;
SIMULTANEOUS=`echo "$NOW" |grep -c :80`
ACTIVE=`echo "$NOW" |grep -c ESTABLISHED`
IDLE=`echo "$NOW" |grep -c TIME_WAIT`
#remove the listener
SIMULTANEOUS=$(($SIMULTANEOUS - 1))
if [ $SIMULTANEOUS -lt 5 ]; then
	if [ $SIMULTANEOUS -lt 0 ]; then
		echo "status err no server listening!"
	else
		echo "status critical no users connected!";
	fi
else
	echo "status ok ok";
fi
echo "metric https_users int $SIMULTANEOUS";
echo "metric https_users_active int $ACTIVE";
echo "metric https_users_idle int $IDLE";

