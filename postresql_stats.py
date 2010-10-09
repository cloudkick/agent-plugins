#!/usr/bin/env python
#
# Cloudkick plugin for monitoring PostgreSQL server status.
#
# Author: Steve Hoffmann
#
# Requirements:
# - Python PostgreSQL adapter (http://initd.org/psycopg/)
#
# Plugin arguments:
# 1. database name (default = postgres)
# 2. user (default = postgres)
# 3. hostname (default = localhost)
# 4. password (default = None)
#

DEFAULT_DATABASE = 'postgres'
DEFAULT_USER = 'postgres'
DEFAULT_HOST = 'localhost'
DEFAULT_PASSWORD = None

import sys
import commands
import warnings
import psycopg2

warnings.filterwarnings('ignore', category = DeprecationWarning)

def open_db(database, user, host = None, password = None):
  dsn = "dbname=%s user=%s" % (database, user)

  if host:
    dsn += ' host=%s' % (host)

  if password:
    dsn += ' password=%s' % (password)

  try:
    return psycopg2.connect(dsn)
  except psycopg2.OperationalError, e:
    print 'status err %s' % (e.message[:48].strip())
    sys.exit(1)

def retrieve_metrics(database, user, host, password):
  conn = open_db(database, user, host, password)
  cur = conn.cursor()

  stats = dict()

  cur.execute("SELECT datname, count(1) FROM pg_stat_activity GROUP BY datname");
  for row in cur:
     stats['conns_' + row[0]] = ('int', row[1])

  cur.execute("SELECT datname, count(1) FROM pg_stat_activity WHERE current_query != '<IDLE>'"
              " GROUP BY datname")
  for row in cur:
     stats['active_queries_' + row[0]] = ('int', row[1])

  cur.execute("SELECT datname, count(1) FROM pg_stat_activity WHERE waiting=true GROUP BY datname")
  for row in cur:
     stats['waiting_queries_' + row[0]] = ('int', row[1])

  cur.execute("SELECT checkpoints_timed, checkpoints_req, buffers_alloc FROM pg_stat_bgwriter")
  row = cur.fetchone()
  stats['expected_checkpoints'] = ('gauge', row[0])
  stats['actual_checkpoints'] = ('gauge', row[1])
  stats['buffers_alloc'] = ('gauge', row[2])

  int_cols = "xact_commit", "xact_rollback", "blks_read", "tup_fetched","tup_inserted", "tup_updated", \
             "tup_deleted"
  cur.execute("SELECT datname, " + ', ' . join(int_cols) + ", (blks_read - blks_hit) / (blks_read+0.000001)"
              " AS blk_miss_pct FROM pg_stat_database")

  for row in cur:
     datname = row[0]
     colno = 1
     for key in int_cols:
       stats[datname + '_' + key] = ('gauge', row[colno])
       colno += 1
     if 0 <= row[colno] <= 1:
       stats[datname + '_blk_miss_pct'] = ('float', row[colno])

  cur.close()
  conn.close()

  return stats

def print_metrics(metrics):
  print "status ok postgresql_stats success"
  for (key, stat) in metrics.iteritems():
     print "metric %s %s %s" % (key, stat[0], stat[1])

def main():
  arg_len = len(sys.argv)

  if arg_len >= 2:
    database = sys.argv[1]
  else:
    database = DEFAULT_DATABASE

  if arg_len >= 3:
    user = sys.argv[2]
  else:
    user = DEFAULT_USER

  if arg_len >= 4:
    host = sys.argv[3]
  else:
    host = DEFAULT_HOST

  if arg_len >= 5:
    password = sys.argv[4]
  else:
    password = DEFAULT_PASSWORD

  metrics = retrieve_metrics(database, user, host, password)
  print_metrics(metrics)

main()
