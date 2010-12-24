#!/usr/bin/env python
# Cloudkick plugin for monitoring Nvidia GPU metrics

import re
import sys
import subprocess

COMMAND = 'nvidia-smi'
COMMAND_ARGS = [ '-q', '-a' ]

METRIC_MAPPINGS = {
                  'gpu': {'type': 'int', 'display_name': 'gpu_usage'},
                  'memory': {'type': 'int', 'display_name': 'memory_usage'},
                  'product name': {'type': 'string', 'display_name': 'product_name'}
}

GPU_NUMBER_RE = re.compile(r'GPU\s+(\d+)', re.IGNORECASE)

def close_file(file_handle):
  try:
    file_handle.close()
  except Exception:
    pass

def main():
  file_handle = open('/tmp/cloudkick-plugin-tmp', 'w')

  command = [ COMMAND ] + COMMAND_ARGS
  (stdout, stderr) = subprocess.Popen(command, stdout = subprocess.PIPE, \
                       stderr = subprocess.PIPE, close_fds = True).communicate()

  try:
    metric_values = parse_output(stdout)
  except Exception, e:
    if stderr:
      error = stderr
    else:
      error = str(e)
    print 'status err Failed to parse metrics: %s' % (error)
    close_file(file_handle)
    sys.exit(1)

  if not metric_values:
    print 'status err Failed to retrieve metrics %s' % (', ' .join(METRIC_MAPPINGS.keys()))
    close_file(file_handle)
    sys.exit(1)

  close_file(file_handle)
  print_metrics(metric_values)

def parse_output(output):
  lines = output.split('\n')

  metric_keys = METRIC_MAPPINGS.keys()
  metric_values = {}
  gpu_number = None
  for line in lines:
    line_original = line.strip()
    line_lower = line_original.lower()

    match = re.match(GPU_NUMBER_RE, line_lower)
    if match:
      gpu_number = match.group(1)
      continue

    split_lower = line_lower.split(':')
    split_original = line_original.split(':')
    if len(split_lower) != 2:
      continue

    name = split_lower[0].strip()
    value = split_original[1].strip()
    metric = METRIC_MAPPINGS.get(name, None)

    if metric and gpu_number is not None:
      name = 'gpu_%s_%s' % (gpu_number, name)
      display_name = 'gpu_%s_%s' % (gpu_number, metric['display_name'])
      metric_values[name] = { 'display_name': display_name, 'value': value}

  return metric_values

def print_metrics(metric_values):
  metrics = []
  output = []
  for key, value in metric_values.items():
    key = re.sub('gpu_\d+_', '', key)
    metric_type = METRIC_MAPPINGS.get(key).get('type')
    display_name = value['display_name']
    metric_value = value['value']

    metrics.append('%s: %s' % (display_name, metric_value))
    output.append('metric %s %s %s' % (display_name, metric_type, metric_value))

  print 'status ok %s' % (', ' . join(metrics))
  print '\n' . join(output)

main()
