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
parser.add_option('--host', help='Redis host')
parser.add_option('--port', help='Redis port', type='int')
(options, args) = parser.parse_args()

host = options.host or 'localhost'
port = options.port or 6379

try:
    db = Redis(host=host, port=port)
    info = db.info()
except RedisError, msg:
    print 'status err Error from Redis: %s' % msg
else:

    print 'status ok redis success'

    # Integer metrics
    for key in ['blocked_clients', 'changes_since_last_save', 'connected_clients',
                'connected_slaves', 'expired_keys', 'used_memory',
                'pubsub_channels', 'pubsub_patterns']:
        print 'metric', key, 'int', info.get(key)

    # Float metrics
    for key in ['mem_fragmentation_ratio', 'used_cpu_sys', 'used_cpu_user',
                'used_cpu_sys_childrens', 'used_cpu_user_childrens']:
        print 'metric', key, 'float', info.get(key)

    # Gauge metrics
    for key in ['last_save_time', 'total_commands_processed',
                'total_connections_received', 'uptime_in_seconds']:
        print 'metric', key, 'gauge', info.get(key)

    # We want to combine the dbindex-specific metrics with their keys
    # So {'db0': {'expires': 0, 'keys': 935}} becomes 'db0_keys => 935', etc...
    for key in info:
        if dbregex.match(key):
            for metric, value in info[key].iteritems():
                name = '%s_%s' % (key, metric)
                print 'metric', name, 'int', value
