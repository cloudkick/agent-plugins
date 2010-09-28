#!/usr/bin/env python
#
# Cloudkick plugin for monitoring latency between local and remote host.
#
# Plugin takes the following arguments:
#
# 1. IPv4 or IPv6 address of the target machine
# 2. number of packets to send
# 3. timeout (how long to wait for a response before quitting)
#
# Note 1: timeout must be lower or equal to 19, because plugins running longer then 20 seconds are 
#         automatically killed by the agent
# Note 2: If using IPv6 address, the address must be in the full uncompressed form 
#         (http://grox.net/utils/ipv6.php)
#

import re
import os
import sys
import subprocess

DEFAULT_PACKET_COUNT = 3
DEFAULT_TIMEOUT = DEFAULT_PACKET_COUNT * 4

IPV4_RE = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
IPV6_RE = re.compile(r'^(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}$', re.IGNORECASE)

LINUX_PACKETS_RE = re.compile(r'(\d+) packets transmitted, (\d+) received, (.*?)% packet loss, time (\d+)ms')
LINUX_STATS_RE = re.compile(r'rtt min/avg/max/mdev = (\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+) ms')
FREEBSD_PACKETS_RE = re.compile(r'(\d+) packets transmitted, (\d+) packets received, (.*?)% packet loss')
FREEBSD_STATS_RE = re.compile(r'round-trip min/avg/max/(stddev|std-dev) = (\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+) ms')

METRIC_TYPES = {
  'trans_packets': 'int',
  'recv_packets': 'int',
  'lost_packets': 'int',
  
  'response_min': 'float',
  'response_max': 'float',
  'response_avg': 'float'
}

def main(ip_address, packet_count, timeout):
  platform = get_platform()
  
  if platform == 'unknown':
    print 'status err Unsupported platform: %s' % (sys.platform)
    sys.exit(1)
  
  command_arguments = ['-c', packet_count]
  if re.match(IPV4_RE, ip_address):
    command = 'ping'
    
    if platform == 'freebsd':
      command_arguments.extend(['-t', timeout])
    else:
      command_arguments.extend(['-w', timeout])
  elif re.match(IPV6_RE, ip_address):
    command = 'ping6'
  
  command_arguments.insert(0, command)
  command_arguments.append(ip_address)
  
  (stdout, stderr) = subprocess.Popen(command_arguments, stdout = subprocess.PIPE, \
                                      stderr = subprocess.PIPE, close_fds = True).communicate()
  
  if stderr:
    print 'status err Failed executing %s command: %s' % (command, stderr[:17])
    sys.exit(1)
  
  metric_values = parse_response(stdout)
  print_metrics(metric_values)
    
def parse_response(response):
  platform = get_platform()
  
  if platform == 'linux':
    packets_re = LINUX_PACKETS_RE
    stats_re = LINUX_STATS_RE
  elif platform == 'freebsd':
    packets_re = FREEBSD_PACKETS_RE
    stats_re = FREEBSD_STATS_RE
    
  packet_stats = re.search(packets_re, response)
  response_stats = re.search(stats_re, response)
  
  if not packet_stats:
    print 'status err Failed to parse response: %s' % (response[:21])
    sys.exit(1)
  
  metric_values = {}
  metric_values['trans_packets'] = packet_stats.group(1)
  metric_values['recv_packets'] = packet_stats.group(2)
  metric_values['lost_packets'] = int(metric_values['trans_packets']) - int(metric_values['recv_packets'])
  
  
  if response_stats:  
    metric_values['response_min'] = response_stats.group(1)
    metric_values['response_max'] = response_stats.group(2)
    metric_values['response_avg'] = response_stats.group(3)

  return metric_values

def print_metrics(metric_values):
  for key, value in metric_values.items():
      print 'metric %s %s %s' % (key, METRIC_TYPES[key], value)

def get_platform():
  if sys.platform.find('linux') != -1:
    platform = 'linux'
  elif sys.platform.find('freebsd') != -1:
    platform = 'freebsd'
  else:
    platform = 'unknown'
    
  return platform

if __name__ == '__main__':
  arg_len = len(sys.argv)
  
  if arg_len not in [2, 3, 4]:
    print 'status err Invalid number of arguments (%s)' % (arg_len - 1)
    sys.exit(1)
  
  packet_count = None
  timeout = None  
  if arg_len >= 2:
    ip_address = sys.argv[1]
  if arg_len >= 3:
    packet_count = sys.argv[2]
  if arg_len >= 4:
    timeout = sys.argv[3]
  
  packet_count = int(packet_count or DEFAULT_PACKET_COUNT)
  timeout = int(timeout or DEFAULT_TIMEOUT)
  
  if timeout > 19:
    print 'status err timeout argument (%s) must be <= 19' % (timeout)
    sys.exit(1)
  
  if not re.match(IPV4_RE, ip_address) and not re.match(IPV6_RE, ip_address):
    print 'status err Invalid address: %s' % (ip_address)
    sys.exit(1)
  
  main(ip_address, str(packet_count), str(timeout))
