#!/usr/bin/env python
"""
Count the approximate number of messaages in your Amazon SQS queue(s).
Requires the boto python library (http://code.google.com/p/boto/).

Set the aws_key and aws_secret values before enabling using the plugin.

LICENSE: http://www.opensource.org/licenses/mit-license.php
AUTHOR:  Caleb Groom <http://github.com/calebgroom>
"""

from boto.sqs.connection import SQSConnection
from boto.exception import SQSError

MAX_MESSAGES = 100
MIN_MESSAGES = 0
aws_key = ''
aws_secret = ''

try:
    conn = SQSConnection(aws_key, aws_secret)
    queues = conn.get_all_queues()
    error_queues = []
    total = 0
    for queue in queues:
        count = queue.count()
        total += count
        if count > MAX_MESSAGES or count < MIN_MESSAGES:
            error_queues.append(queue.name)
        print 'metric %s int %d' % (queue.name, count)

    if len(error_queues) == 0:
        print 'status ok %d messages in all queues' % total
    else:
        s = '/'.join(error_queues)
        print 'status err %s contains an unexpected number of messages' % s

except SQSError as e:
    print 'status err SQS error:', e.reason  
except:
    print 'status err Unhandled error'
