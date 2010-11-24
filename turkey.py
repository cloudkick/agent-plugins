#!/usr/bin/python
import time
import struct
import sys

ldusb = file("/dev/ldusb0")

time.sleep(0.5)
#beep_temp = int(sys.argv[1])


# for n in range(10):
    # time.sleep(0.5)
pkt = ldusb.read(8)
parsed_pkt = list(struct.unpack("<BBHHH", pkt))
num_samples = parsed_pkt.pop(0)
seqno = parsed_pkt.pop(0)
for sample in range(num_samples):
  c =  parsed_pkt[sample]/128.0
  f = 9.0 / 5.0 * c + 32
#print "%2.2f C, %2.2f F" % (c, f)   
#if f < beep_temp:
#  print "\a",
#    time.sleep(0.5)
if f > 200 and f < 300:
  status = 'ok'
else:
  status = 'err'
print 'status %s temp at %d' % (status, f)
print 'metric temp int %d' % (f)

