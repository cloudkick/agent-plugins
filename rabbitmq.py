#!/usr/bin/env python
#
# License: MIT
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
# Cloudkick plugin for monitoring a RabbitMQ stats.
#
# Example usage (arguments which you pass in to the plugin the Cloudkick
#                dashboard):
#
# Monitor queue "bg_jobs" memory usage, number of consumers and number of
# messages:
#
# --action list_queues --queue bg_jobs --parameters memory,consumers,messages
#
# Monitor exchange "amqp.direct" type, durability and auto_delete value
#
# --action list_exchanges --exchange amqp.direct --parameters type,durable,auto_delete

import re
import sys
import subprocess
import optparse

METRIC_TYPES = {
  'list_queues': {
    'name': 'string',
    'durable': 'string',
    'auto_delete': 'string',
    'arguments': 'string',
    'pid': 'int',
    'owner_pid': 'int',
    'messages_ready': 'int',
    'messages_unacknowledged': 'int',
    'messages': 'int',
    'consumers': 'int',
    'memory': 'int'
  },

  'list_exchanges': {
    'name': 'string',
    'type': 'string',
    'durable': 'string',
    'auto_delete': 'string',
    'internal': 'string',
    'argument': 'string'
  }
}

def retrieve_stats(vhost, action, queue, exchange, parameters,
                   rabbitmqctl_path):
  value = queue or exchange
  command = [ rabbitmqctl_path, action, '-p', vhost ]
  parameters = parameters.split(',')

  parameters = [ p.lower() for p in parameters \
                 if p.lower() in METRIC_TYPES[action].keys() ]

  command.extend( [ 'name' ] + parameters)
  process1 = subprocess.Popen(command, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
  process2 = subprocess.Popen([ 'grep', value ], stdin=process1.stdout,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
  process1.stdout.close()
  stdout, stderr = process2.communicate()

  if stderr:
    return None, stderr

  stdout = stdout.split('\n')
  stdout = stdout[0]

  if not stdout:
    return None, 'Empty output'

  return parse_stats( [ 'name' ] + parameters, stdout), None

def parse_stats(parameters, data):
  values = re.split('\s+', data)

  stats = {}
  for index, parameter in enumerate(parameters):
    stats[parameter] = values[index]

  return stats

def print_metrics(action, metrics):
  for key, value in metrics.iteritems():
    metric_type = METRIC_TYPES[action].get(key, None)

    if not metric_type:
      continue

    print 'metric %s %s %s' % (key, metric_type, value)

if __name__ == '__main__':
  parser = optparse.OptionParser()
  parser.add_option('--path', action='store', dest='rabbitmqctl_path',
                    default='rabbitmqctl',
                    help='Path to the rabbitmqctl binary (optional)')
  parser.add_option('--action', action='store', dest='action',
                    help='Action (list_queues or list_exchanges)')
  parser.add_option('--vhost', action='store', dest='vhost', default='/',
                    help='Vhost (optional)')
  parser.add_option('--queue', action='store', dest='queue',
                    help='Queue name')
  parser.add_option('--exchange', action='store', dest='exchange',
                    help='Exchange name')
  parser.add_option('--parameters', action='store', dest='parameters',
                    default='messages',
                    help='Comma separated list of parameters to retrieve (default = messages)')
  parser.add_option('--queue-length', type='int', action='store', dest='length',
                    help='Max messages in the queue before alert')

  (options, args) = parser.parse_args(sys.argv)

  rabbitmqctl_path = options.rabbitmqctl_path
  action = getattr(options, 'action', None)
  vhost = options.vhost
  queue = getattr(options, 'queue', None)
  exchange = getattr(options, 'exchange', None)
  parameters = options.parameters
  length = getattr(options, 'length', None)

  if not action:
    print 'status err Missing required argument: action'
    sys.exit(1)

  if action == 'list_queues' and not queue:
    print 'status err Missing required argument: queue'
    sys.exit(1)
  elif action == 'list_exchanges' and not exchange:
    print 'status err Missing required argument: exchange'
    sys.exit(1)

  if action not in METRIC_TYPES.keys():
    print 'status err Invalid action: %s' % (action)
    sys.exit(1)

  if not parameters:
    print 'status err Missing required argument: parameters'
    sys.exit(1)

  metrics, error = retrieve_stats(vhost, action, queue, exchange,
                                  parameters, rabbitmqctl_path)

  if error:
    print 'status err %s' % (error)
    sys.exit(1)
  if length:
    if int(metrics['messages']) > length:
      print 'status err Message queue %s at %d and above threshold of %d' % (
            queue, int(metrics['messages']), length)
      sys.exit(1)
  print 'status ok metrics successfully retrieved'
  print_metrics(action, metrics)
