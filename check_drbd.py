#!/usr/bin/env python

# Cloudkick plugin that monitors various DRBD parameters.
#
# Plugin arguments:
# 1. Minor device number of the DRBD device to monitor
#
# Author: Andrew Miklas / PagerDuty
# Copyright (c) 2011 PagerDuty, Inc. <andrew@pagerduty.com>
#
# MIT License:
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

import sys
import re

def parse_line(line):
    d = {}

    # Extract everything that looks line a k/v pair
    for kv_pair in line.split():
        l = kv_pair.split(':', 1)
        if len(l) < 2:
            continue
        d[l[0]] = l[1]

    return d


def read_proc_drbd(filename, device_num):
    try:
        info_fd = open(filename, "r")
    except IOError:
        print 'status err drbd device (%s) not found' % (filename)
        sys.exit(1)

    device_num = str(device_num)
    dev_stats = {}

    while True:
        line = info_fd.readline()
        if not line: break

        match = re.search(r'^\s*(\d+):\s+(.*)$', line)
        if not match:
            continue
        if match.groups()[0] == device_num:
            # Device stat lines come in pairs.  We've already got the
            # first one, so read in the second.
            for l in [match.groups()[1], info_fd.readline()]:
                dev_stats.update(parse_line(l))
            return dev_stats

    # Device not found
    return None


fmt_string = str
fmt_count = str

def fmt_size(val):
    # DRBD sizes are in KiBytes
    return str(int(val) * 1024)


METRICS = (
    ("connection_state", "cs", "string", fmt_string),
    ("disk_state", "ds", "string", fmt_string),
    ("roles", "ro", "string", fmt_string),

    ("network_send", "ns", "int", fmt_size),
    ("network_send_rate", "ns", "gauge", fmt_size),
    ("network_receive", "nr", "int", fmt_size),
    ("network_receive_rate", "nr", "gauge", fmt_size),
    ("disk_write", "dw", "int", fmt_size),
    ("disk_write_rate", "dw", "gauge", fmt_size),
    ("disk_read", "dr", "int", fmt_size),
    ("disk_read_rate", "dr", "gauge", fmt_size),
    ("out_of_sync", "oos", "int", fmt_size),
    ("out_of_sync_rate", "oos", "gauge", fmt_size),

    ("activity_log", "al", "int", fmt_count),
    ("activity_log_rate", "al", "gauge", fmt_count),
    ("bit_map", "bm", "int", fmt_count),
    ("bit_map_rate", "bm", "gauge", fmt_count),

    ("local_count", "lo", "int", fmt_count),
    ("pending", "pe", "int", fmt_count),
    ("unacknowledged", "ua", "int", fmt_count),
    ("application_pending", "ap", "int", fmt_count),
    ("epochs", "ep", "int", fmt_count)
)

OK_CONN_STATES = ("Connected", "VerifyS", "VerifyT")
WARN_CONN_STATES = ("StandAlone", "Disconnecting", "StartingSyncS", "StartingSyncT", "WFBitMapS", "WFBitMapT", "WFSyncUUID", "SyncSource", "SyncTarget", "PausedSyncS", "PausedSyncT")


if len(sys.argv) < 2:
    print >>sys.stderr, "Usage: check_drbd.py drbd_dev_num"
    exit(2)

device_num = sys.argv[1]
dev_stats = read_proc_drbd("/proc/drbd", device_num)

if dev_stats is None:
    print >>sys.stderr, "Couldn't find DRBD device number %s" % device_num
    sys.exit(1)

conn_state = dev_stats.get("cs")
if conn_state is None:
    print >>sys.stderr, "Connection state can't be found!"
    sys.exit(1)

if conn_state in OK_CONN_STATES:
    print 'status ok Connection is in an OK state'
elif conn_state in WARN_CONN_STATES:
    print 'status warn Connection is in a WARN state'
else:
    print 'status err Connection is in a ERR state'

for m in METRICS:
    if m[1] in dev_stats:
        print "metric %s %s %s" % (m[0], m[2], m[3](dev_stats.get(m[1])))

sys.exit(0)
