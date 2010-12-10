#!/usr/bin/env python
"""
Cloudkick open files plugin
Developed by Daniel Benamy at WNYC
Based on the Varnish plugin developed by Christopher Groskopf for The Chicago
Tribune News Applications Team

Source released under the MIT license.

Description:

Determines how many files a user has open using lsof.

Error reporting:

Outputs an error if a user wasn't specified as an argument or if lsof didn't
execute properly.

Warn reporting:

Never outputs a warning.
"""

from subprocess import Popen, PIPE
import sys
import time

if len(sys.argv) == 1:
    print 'status err User must be specified as a command line argument.'
    sys.exit()
user = sys.argv[1]

# If I take out this line, result winds up as None when run by cloudkick-agent
# but not when run manually. What the hell???!!!
f = open('/tmp/some-junk-so-the-open-files-check-works', 'w')

proc = Popen(['lsof', '-u', user, '-F', 'f'], stdout=PIPE)
result = proc.communicate()[0]
if not result:
    print 'status err lsof failed to run.'
    sys.exit()

lines = result.split('\n')
fds = filter(lambda line: line.startswith('f'), lines)

print 'status ok Got open file count.'
print 'metric open_files int %d' % len(fds)
