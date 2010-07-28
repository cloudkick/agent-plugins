#!/usr/bin/env python

import sys, os, time

DEFAULT_AGE=600

def check_logs(*logs):
  out = []
  total = 0
  status = 'ok'
  msg = 'everything looks good'
  n = time.time()
  for l in logs:
    if isinstance(l, (list, tuple)):
      limit, l = l
    else:
      limit = DEFAULT_AGE
    try:
      s = os.stat(l)
    except Exception:
      status = 'err'
      msg = "file not found '%s'" % l
    else:
      diff = n - (s.st_mtime)
      msg = 'everything looks good, modified %d seconds ago' % diff
      if diff > limit:
        status = 'err'
        msg = '%s not modified in %d seconds' % (l, diff)

  out.insert(0, "status %s %s" % (status, msg))
  print '\n'.join(out)
