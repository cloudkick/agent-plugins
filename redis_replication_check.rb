#!/usr/bin/env ruby

###############
#
# Checks redis replication status.
# Can be used with master or slave.
#
# Copyright C. Flores github@petalphile.com
# Released under the MIT License:
#  no warranty but you should feel free to 
#  do whatever you want with it.
#
###############

require 'optparse'
 
options = {}

optparse = OptionParser.new do|opts|
	opts.banner = "Checks redis replication status.  Usage: #{$0} -r <master|slave> <options>"
 
	options[:host] = "localhost"
	opts.on( '-h', '--host <host>', 'connect to redis running on <host>.  defaults to localhost' ) do |host|
		options[:host] = host.to_s
	end
	options[:port] = 6379
	opts.on( '-p', '--port <port>', 'connect to redis running on <port>.  defaults to 6379' ) do |port|
		options[:port] = port.to_i
	end
	options[:role] = nil
	opts.on( '-r', '--role <master|slave>', 'redis should be master or slave' ) do |role|
		options[:role] = role.to_s
	end
	options[:connected_slaves] = nil
	opts.on( '-c', '--connected_slaves <int>', 'master should have <int> slaves.  must be used with -r/--role master.  defaults to 1' ) do |int|
		options[:connected_slaves] = int.to_i
	end
	options[:slave_lag] = nil
	opts.on( '-l', '--replication_lag <int>', 'master io cannot be more than <int> seconds behind.  used with -r/--role slave.  default is 0' ) do |int|
		options[:slave_lag] = int.to_i
	end
	opts.on( '--help', 'Display this screen' ) do
		puts opts
		exit
	end
end
 
begin
	optparse.parse!
	if options[:role] == "slave"
		if options[:connected_slaves]
			puts "Error: -c/--connected_slaves cannot be used with -r/--role slave."
			puts optparse
			exit 2
		end
	elsif options[:role] == "master"
		if options[:slave_lag]
			puts "Error: -l/--slave_lag cannot be used with -r/--role master."
			puts optparse
			exit 2
		end
	else
		puts "Error: must set -r/--role"
		puts optparse
		exit 2
	end
rescue OptionParser::InvalidOption
	puts "Error: unknown option"
	puts optparse
	exit 2
end

# the actual check

redis_info	= `redis-cli -h #{options[:host]} -p #{options[:port]} info`

if $? != 0
	puts "status err could not connect to redis on #{options[:host]}:#{options[:port]}"
	exit 1
end

status = Hash.new
redis_info.each do |line|
	key,value =  line.chomp.split(':')
	status[key] = value
end

if options[:role] == "slave"
	expectedlag = options[:slave_lag].to_i || 0
	if status["role"] =~ /slave/ \
		&& status["master_link_status"] =~ /up/ \
		&& status["master_last_io_seconds_ago"].to_i <= expectedlag
			
		puts "status ok ok"
	else
		puts "status err redis thinks it is #{status["role"]}, master is #{status["master_link_status"]} and last io was #{status["master_last_io_seconds_ago"]}s."
	end
	puts "metric master_last_io_seconds_ago int #{status["master_last_io_seconds_ago"]}"	
else
	expectedslaves = options[:connected_slaves] || 1
	actualslaves = status["connected_slaves"].to_i
	if status["role"] =~ /master/ && actualslaves == expectedslaves
			
		puts "status ok ok"
	else
		puts "status err redis thinks it is #{status["role"]} with #{actualslaves} slaves."
	end
end

