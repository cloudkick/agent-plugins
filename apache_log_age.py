#!/usr/bin/env python
from log_freshness import check_logs

# Apache log age: alert if the apache access log hasn't been modified in over 
# 2 hours. This script is really more of an example of how to use 
# log_freshness.py

# Alert if log hasn't been modified in over 2 hours
check_logs((60*60*2, '/var/log/apache/access.log'))
