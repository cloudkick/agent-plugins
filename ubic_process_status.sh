#!/bin/bash

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
