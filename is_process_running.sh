#!/bin/bash

# This script alerts if there is no running process with the string java in it.
# A better practice is to use a log freshness check, since a running process 
# can still be hung. 

# Change this process name to suit
PROCESS_NAME="java"

NUM_PROCESSES=`ps ax | grep "$PROCESS_NAME" | grep -v grep | wc -l`

if [ $NUM_PROCESSES -lt 1 ]; then
  echo "status err $PROCESS_NAME is not running"
else
  echo "status ok $PROCESS_NAME is running"
fi
