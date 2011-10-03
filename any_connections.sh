#!/bin/bash

# Cloudkick plugin to count number of connections.  
# Alerts if no clients and/or no listeners.

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <lo@petalphile.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return 
# ----------------------------------------------------------------------------

if [ $# -ne 1 ]; then
	echo -e "usage `basename $0` <port to check>\nwhere <port to check> is 443 for https, 3306 for mysql, etc.\nalerts if no clients and/or listeners"
	exit 1
fi

PORT=$1
NOW=`netstat -an|grep -v 'LISTEN'`
SIMULTANEOUS=`echo $NOW|grep -c :$PORT\ `
ACTIVE=`echo "$NOW" |grep -c ESTABLISHED`
IDLE=`echo "$NOW" |grep -c TIME_WAIT`
CLOSING=`echo "$NOW" |grep -c FIN`

if [ $SIMULTANEOUS -lt 1 ]; then
	if [ $SIMULTANEOUS -lt 0 ]; then
		echo "status err no server listening!"
		SIMULTANEOUS=0
	else
		echo "status err no users connected!";
	fi
	exit
else
	echo "status ok ok";
fi
echo "metric port$PORT\users int $SIMULTANEOUS";
echo "metric port$PORT\users_active int $ACTIVE";
echo "metric port$PORT\users_idle int $IDLE";
echo "metric port$PORT\users_closing int $CLOSING";

