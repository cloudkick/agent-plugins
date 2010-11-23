#!/usr/bin/env python

# Cloudkick plugin that monitors CloudWatch info for RDS instances.
# Parameters required are:
# DBInstanceIdentifier, AWS Access Key, and AWS Secret Access Key

# Requires boto library:
# # easy_install boto

import datetime
import sys
from optparse import OptionParser
from boto.ec2.cloudwatch import CloudWatchConnection

### Arguments
parser = OptionParser()
parser.add_option("-i", "--instance-id", dest="instance_id",
                help="DBInstanceIdentifier")
parser.add_option("-a", "--access-key", dest="access_key",
                help="AWS Access Key")
parser.add_option("-k", "--secret-key", dest="secret_key",
                help="AWS Secret Access Key")

(options, args) = parser.parse_args()

if (options.instance_id == None):
    parser.error("-i DBInstanceIdentifier is required")
if (options.access_key == None):
    parser.error("-a AWS Access Key is required")
if (options.secret_key == None):
    parser.error("-k AWS Secret Key is required")
###

### Real code
metrics = {"CPUUtilization":{"type":"float", "value":None},
    "ReadLatency":{"type":"float", "value":None},
    "DatabaseConnections":{"type":"int", "value":None},
    "FreeableMemory":{"type":"float", "value":None},
    "ReadIOPS":{"type":"int", "value":None},
    "WriteLatency":{"type":"float", "value":None},
    "WriteThroughput":{"type":"float", "value":None},
    "WriteIOPS":{"type":"int", "value":None},
    "SwapUsage":{"type":"float", "value":None},
    "ReadThroughput":{"type":"float", "value":None},
    "FreeStorageSpace":{"type":"float", "value":None}}
    
end = datetime.datetime.now()
start = end - datetime.timedelta(minutes=5)

conn = CloudWatchConnection(options.access_key, options.secret_key)
for k,vh in metrics.items():
    try:
        res = conn.get_metric_statistics(60, start, end, k, "AWS/RDS", "Average", {"DBInstanceIdentifier": options.instance_id})
    except Exception, e:
        print "status err Error running rds_stats: %s" % e.error_message
        sys.exit(1)
    average = res[-1]["Average"] # last item in result set
    if (k == "FreeStorageSpace" or k == "FreeableMemory"):
        average = average / 1024.0**3.0
    if vh["type"] == "float":
        metrics[k]["value"] = "%.4f" % average
    if vh["type"] == "int":
        metrics[k]["value"] = "%i" % average

# Iterating through the Array twice seems inelegant, but I don't know Python 
# well enough to do it the right way.
print "status ok rds success"
for k,vh in metrics.items():
    print "metric %s %s %s" % (k, vh["type"], vh["value"])