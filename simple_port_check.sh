#!/bin/bash

# Cloudkick plugin to check that a port is open.
# Alerts if a connection cannot be established.

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <matt@williams-tech.net> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return 
# ----------------------------------------------------------------------------

if [ $# -ne 1 ]; then
  echo "Usage: $0 <port>"
  exit
fi

PORT=$1

nc 127.0.0.1 $PORT </dev/null
if [ $? -ne 0 ]; then
	echo "status err no server listening!"
else
  echo "status ok ok"
fi
