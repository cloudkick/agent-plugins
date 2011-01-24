#!/usr/bin/env python

# Redis monitoring for Cloudkick
#
# Requirements:
#  1. redis-py (https://github.com/andymccurdy/redis-py)
#  2. Tested on redis 2.1.4
#
# Arguments:
#  --host   Redis host (defaults to localhost)
#  --port   Redis port (defaults to 6379)
#
# To install, copy script to /usr/lib/cloudkick-agent/plugins/
#
# Copyright (c) 2011 Brad Jasper <bjasper@gmail.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# 

import re
import optparse

from redis import Redis
from redis.exceptions import RedisError

dbregex = re.compile(r'db\d+')

parser = optparse.OptionParser()
parser.add_option('--host', help='Redis host', default='localhost')
parser.add_option('--port', help='Redis port', type='int', default=6379)
(options, args) = parser.parse_args()

metrics = {
    'blocked_clients': 'int',
    'changes_since_last_save': 'int',
    'connected_clients': 'int',
    'connected_slaves': 'int',
    'expired_keys': 'int',
    'used_memory': 'int',
    'pubsub_channels': 'int',
    'pubsub_patterns': 'int',

    'mem_fragmentation_ratio': 'float',
    'used_cpu_sys': 'float',
    'used_cpu_user': 'float',
    'used_cpu_sys_childrens': 'float',
    'used_cpu_user_childrens': 'float',

    'last_save_time': 'gauge',
    'total_commands_processed': 'gauge',
    'total_connections_received': 'gauge',
    'uptime_in_seconds': 'gauge'
}

try:
    db = Redis(host=options.host, port=options.port)
    info = db.info()
except RedisError, msg:
    print 'status err Error from Redis: %s' % msg
else:

    print 'status ok redis success'

    for metric, _type in metrics.iteritems():
        print 'metric %s %s %s' % (metric, _type, info.get(metric))

    # We also want to output the dbindex-specific metrics
    # Redis INFO returns these as
    #   'db0': {'expires': 0, 'keys': 935},
    #   'db1': {'expires': 4, 'keys': 100},
    #
    # These should be converted to db0_expires, db0_keys, etc...
    for key in info:
        if dbregex.match(key):
            for metric, value in info[key].iteritems():
                print 'metric %s_%s int %s' % (key, metric, value)
