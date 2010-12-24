#!/usr/bin/env python
"""
Count the number of IPs that were banned in the last minute.

Usage:
  fail2ban.py [warn_count] [alert_count]

LICENSE: http://www.opensource.org/licenses/mit-license.php
AUTHOR:  Caleb Groom <http://github.com/calebgroom>
"""

import sys
import glob
import os.path
import ConfigParser
import socket
from datetime import datetime, timedelta

WARN_COUNT = 2
ALERT_COUNT = 5
now = datetime.now() - timedelta(minutes=1)

# The alerting thresholds can be overridden via command line arguments
limits = [WARN_COUNT, ALERT_COUNT]
for i in [2,3]:
    if len(sys.argv) >= i:
      try:
          limits[i-2] = int(sys.argv[i-1])
      except ValueError:
          print 'status err argument "%s" is not a valid integer' % sys.argv[i-1]
          sys.exit(1)

# Discover 'logtarget' setting in configuration file
paths = ['/etc/fail2ban.conf', '/etc/fail2ban/*.conf']
config_files = []
for p in paths:
    files = glob.glob(p)
    for f in files:
        if os.path.isfile(f):
            config_files.append(f)

config = ConfigParser.ConfigParser()
config.read(config_files)
try:
    logfile = config.get("Definition", "logtarget")
except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
    print 'status err "logtarget" is not defined in', ', ' .join(config_files)
    sys.exit(1)

if not os.path.isfile(logfile):
    print 'status err log file', logfile, 'is not a file'
    sys.exit(1)

# Drop the seconds from the timestam and look for ban entries.
# Sample ban message:
#     2010-10-21 18:01:08,099 fail2ban.actions: WARNING [ssh-iptables] Ban 1.2.3.4
timestamp = now.isoformat(' ')[:17]
count = 0
ips = []

try:
    f = open(logfile, 'r')
except IOError:
    print 'status err Unable to open log file', logfile
    sys.exit(1)

needle = ' Ban '
for line in f:
    if line.startswith(timestamp):
        i = line.rfind(needle)
        if i == -1:
            continue
        ip = line[i+len(needle):len(line)-1]
        try:
            socket.inet_aton(ip)
            # Matching timestamp, 'Ban' and valid IP
            count += 1
            ips.append(ip)
        except socket.error:
            pass

try:
    f.close()
except Exception:
  pass

print 'metric bans int', count

if count == 0:
    ips = ""

if count >= limits[1]:
    print 'status err', count, 'IPs banned', ips
elif count >= limits[0]:
    print 'status warn', count, 'IPs banned', ips
else:
    print 'status ok', count, 'IPs banned', ips
