#!/bin/bash

# process_count.sh <process_name>
# Cloudkick plugin to check if a named process is running and count number of
# processes. The process name is matched as regex.

# Copyright (C) 2010 by David E. Chen <dchen@alumni.cmu.edu>
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
  echo -e "usage: `basename $0` <process_name>"
  exit 1
fi

PS_COUNT=`ps -Ao command | grep -ve grep -e process_count.sh | grep -ce $1`

if [ "$PS_COUNT" -lt "1" ]; then
  echo "status err $1 has 0 processes"
else
  echo "status ok $1 has $PS_COUNT processes"
  echo "metric process_count_$1 int $PS_COUNT"
fi
