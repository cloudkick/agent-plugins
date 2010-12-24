#!/usr/bin/python
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
