#!/usr/bin/python
#
#                  _<_< > 
#      ____________/_/ _/
#    _/ turkey.py _/  /_
#   / custom    /     \ >
#  (   plugin   \_____//
#   \________________/ 
# 
#  First used with a Backwoods smoker to monitor
#  the temp of a turkey during cook time. You will
#  need to adjust the temp thresholds to match your
#  specific cooking requirements. Enjoy! 
#
#  ~Team Cloudkick, Thanksgiving 2010

import time
import struct
import sys

ldusb = file("/dev/ldusb0")

time.sleep(0.5)

# This reads the payload off of the Go!Temp USB drive
pkt = ldusb.read(8)
parsed_pkt = list(struct.unpack("<BBHHH", pkt))
num_samples = parsed_pkt.pop(0)
seqno = parsed_pkt.pop(0)
for sample in range(num_samples):
  c =  parsed_pkt[sample]/128.0

  # Convert to Fahrenheit since this is for Thanksgiving
  f = 9.0 / 5.0 * c + 32

# This is the actual alerting threshold,
# tweak as needed
if f > 200 and f < 300:
  status = 'ok'
else:
  status = 'err'
print 'status %s temp at %d' % (status, f)
print 'metric temp int %d' % (f)
