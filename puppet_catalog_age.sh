#!/bin/bash
#
# License: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# puppet_catalog_age.sh: Check how old the puppet catalog is. If the puppet 
# catalog on a machine hasn't been updated in a while, you likely have an 
# error in your puppet config.

# Different versions of puppet keep their catalog files in different places. 0.25+ seems to use this path.
CATALOG_TIME=`stat -c %Y /var/lib/puppet/client_yaml/catalog/\`hostname\`.yaml`
CURRENT_TIME=`date +%s`
CATALOG_AGE=$((CURRENT_TIME - CATALOG_TIME))

# Puppet catalog should be updated every 30 minutes. If it's been three hours, something is wrong.
if [ "$CATALOG_AGE" -gt "10800" ]
then
  echo "status err Puppet catalog age is $CATALOG_AGE seconds"
elif [ "$CATALOG_AGE" -gt "7200" ]
then
  echo "status warn Puppet catalog age is $CATALOG_AGE seconds"
else
  echo "status ok Puppet catalog age is $CATALOG_AGE seconds"
fi

echo "metric puppet_catalog_age int $CATALOG_AGE"
