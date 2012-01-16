#!/bin/bash

# Cloudkick plugin to check that a Ubic managed process is running.
# Alerts if it is not running

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <matt@williams-tech.net> wrote this file. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return 
# ----------------------------------------------------------------------------

if [ $# -ne 1 ]; then
  echo "Usage: $0 <ubic process>"
  exit
fi

process=$1

perl -I/usr/local/lib/perl5/site_perl/5.14.1 \
  -I/usr/local/lib/perl5/site_perl/5.14.1/x86_64-linux \
  /usr/local/bin/ubic status | \
  grep -i $process | \
  grep "running" >/dev/null 2>&1

if [ $? -ne 0 ]; then
  echo "status err no process running!"
else
  echo "status ok ok"
fi

exit
