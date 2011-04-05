#!/usr/bin/env python
#
# License: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
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

if len(sys.argv) < 2:
  sys.exit('Usage: %s <log file to check>' % sys.argv[0])

if not os.path.exists(sys.argv[1]):
  sys.exit('ERROR: file not found!' % sys.argv[1])
else:
  check_logs(sys.argv[1])
