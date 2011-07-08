#!/bin/bash

MINS=$1
MAXS=$2
DIR=$3

if [ -z "$MINS" ] || [ -z "$MAXS" ] || [ -z "$DIR" ]; then
  echo "usage: $0 <minimum size in MB> <maximum size in MB> <directory>
	example: $0 100 100000 /home"
  exit 2
fi

if [ ! -d $DIR ]; then
  echo "status err $DIR does not exist"
  exit
fi

SIZE="`du -sm $DIR | awk '{ print $1 }'`"

RES="ok"
if [ $SIZE -lt $MINS ] || [ $SIZE -gt $MAXS ]; then
  RES="err"
fi

echo "status $RES $DIR is ${SIZE}MB"
echo "metric dir_size int ${SIZE}"
