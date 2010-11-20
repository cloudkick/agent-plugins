#!/usr/bin/env python
"""
CloudKick Varnish plugin
Developed by Christopher Groskopf for The Chicago Tribune News Applications Team
http://apps.chicagotribune.com
https://github.com/newsapps

Source released under the MIT license.

Description:

This plugin will pipe all output from the command "varnishstat -1"
up to CloudKick.  In addition, it will store the cache_hit and cache_miss stats
in a tmp file on each execution so that it can compute a hit_rate stat, which will
also be reported to CloudKick.

Error reporting:

This plugin will report an error only if varnishstat fails to
execute (generally this would only be the case if Varnish is not running).

Warn reporting:

This plugin will report a warning anytime that it fails to parse
varnishstat's output.

TODO:

Support custom warnings and errors when the hit_rate stat falls below a
specified threshold.
"""

import os
import re
import subprocess
import sys

HIT_RATE_FILE = '/tmp/cloudkick-agent-varnish.tmp'

result = subprocess.Popen(['varnishstat', '-1'], stdout=subprocess.PIPE).communicate()[0]

if not result:
	print 'status error Varnish is not running.'
	sys.exit()

data = []
hits = None
misses = None

try:
	for r in result.split('\n'):
		if not r:
			continue

		parts = re.split('\s+', r.strip())

		data.append('metric %s int %s' % (parts[0], parts[1]))

		if parts[0] == 'cache_hit':
			hits = int(parts[1])
		elif parts[0] == 'cache_miss':
			misses = int(parts[1])

	if hits and misses:
		if os.path.exists(HIT_RATE_FILE):
			with open(HIT_RATE_FILE, 'r') as f:
				parts = f.read().split(',')
				last_hits = int(parts[0])
				last_misses = int(parts[1])
			
			delta_hits = hits - last_hits
			delta_misses = misses - last_misses

			if delta_misses == 0:
				hit_rate = float(1.0)
			else:
				hit_rate = float(delta_hits) / (delta_hits + delta_misses)

			data.append('metric hit_rate float %1.3f' % hit_rate)

           	with open(HIT_RATE_FILE, 'w') as f:
                        f.write('%i,%i' % (hits, misses))
except Exception, e:
	print e
	print 'status warn Error parsing varnishstat output.'
	sys.exit()

print 'status ok Varnish is running.'

for  d in data:
	print d
