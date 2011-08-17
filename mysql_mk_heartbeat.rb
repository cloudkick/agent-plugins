#!/usr/bin/env ruby

# Cloudkick plugin that monitors mysql replication slave delay using maatkit's
# mk-heartbeat. It is assumed that mk-heartbeat is running as a daemon on your master host.
#
# Plugin arguments:
# 1. Location of config file for connecting to mysql.
#    ie: /etc/maatkit/mk-heartbeat.conf
#    File should look something like this:
#     ---------------
#     user=maatkit
#     password=P@ssw0rd
#     database=maatkit
#     ---------------
#
# 2. Number of seconds of replication lag before Cloudkick should report an error.
#
# Author: Ian Enders / PagerDuty
# Copyright (c) 2011 PagerDuty, Inc. <ian@pagerduty.com>
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

if ARGV.length != 2
  puts "Usage: #{$0} [mk-config-file] [max-lag-in-seconds]"
  puts "Example: #{$0} /etc/maatkit/mk-heartbeat.conf 30"
  puts "  Would load the mysql config from /etc/maatkit/mk-heartbeat.conf and consider 30"
  puts "  or more seconds of replication lag to be an error."
  exit 1
end

mk_config = ARGV[0]
max_lag_in_seconds = ARGV[1].to_i

begin
  val = `mk-heartbeat --config #{mk_config} --check`
  lag = val.to_i
  if lag >= max_lag_in_seconds
    puts "status err Mysql slave is #{lag} seconds behind master."
  else
    puts "status ok Mysql slave is tracking master."
  end
  puts "metric slave_replication_delay int #{lag}"
rescue => e
  puts "status err Problem running mk-heartbeat plugin: #{e.message}"
end
