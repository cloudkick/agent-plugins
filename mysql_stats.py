#!/usr/bin/env python

import commands
import sys

metric_types = {
                "threads": "int",
                "questions": "gauge",
                "slow_queries": "gauge",
                "opens": "gauge",
                "flush_tables": "gauge",
                "open_tables": "int",
                "queries_per_second_avg": "float",
                }

(status, output) = commands.getstatusoutput("su -c \"mysqladmin status\"")

if status != 0:
  print "status err Error running mysqladmin status: %s" % output
  sys.exit(status)

print "status ok mysqladmin success"

pairs = output.split("  ")

for pair in pairs:
  (key, value) = pair.split(": ")
  key = key.lower().replace(" ", "_")

  if metric_types.get(key):
    print "metric %s %s %s" % (key, metric_types[key], value)
