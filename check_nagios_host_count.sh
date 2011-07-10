#!/bin/sh

# check_nagios_host_count.sh <min_hosts>
# Cloudkick plugin to check if nagios has at least min_hosts hosts
#
# Copyright (C) 2010 by Ben Firshman <ben@firshman.co.uk>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


if [ $# -ne 1 ]; then
  echo -e "usage: `basename $0` <min_hosts>"
  exit 1
fi

HOST_COUNT=`nagios3stats | grep "Total Hosts" | awk '{ print $3 }'`

echo "metric nagios_host_count int $HOST_COUNT"

if [ "$HOST_COUNT" -lt "$1" ]; then
  echo "status err nagios has less than $1 hosts"
else
  echo "status ok nagios has $HOST_COUNT hosts"
fi


