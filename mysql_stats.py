#!/usr/bin/env python

# By default, MySQL does not allow root to run mysqladmin with no password.
# To get this script working, create /root/.my.cnf and put the following lines 
# in it (sans # signs)...
#
#[client]
#user = a_valid_mysql_user
#password = a_secret_password_1234
#host = localhost
#
# ...filling in your values for the user and password. Be sure to chmod .my.cnf
# to 600. You don't want other users to be able to read the username and 
# password.

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
