#!/usr/bin/env python
"""
Count the approximate number of messaages in your Amazon SQS queue(s).
Requires the boto python library (http://code.google.com/p/boto/).

Set the aws_key and aws_secret values before using the plugin.

Usage:
  sqs.py [minimum_count] [maximum_count]

LICENSE: http://www.opensource.org/licenses/mit-license.php
AUTHOR:  Caleb Groom <http://github.com/calebgroom>
"""

from boto.sqs.connection import SQSConnection
from boto.exception import SQSError
import sys

MAX_MESSAGES = 100
MIN_MESSAGES = 0
aws_key = ''
aws_secret = ''

# The alerting thresholds can be overridden via command line arguments
limits = [MIN_MESSAGES, MAX_MESSAGES]
for i in [2,3]:
    if len(sys.argv) >= i:
      try:
          limits[i-2] = int(sys.argv[i-1])
      except ValueError:
          print 'status err argument "%s" is not a valid integer' % sys.argv[i-1]
          sys.exit(1)

try:
    conn = SQSConnection(aws_key, aws_secret)
    queues = conn.get_all_queues()
    error_queues = []
    total = 0
    for queue in queues:
        count = queue.count()
        total += count
        if count < limits[0] or count > limits[1]:
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
