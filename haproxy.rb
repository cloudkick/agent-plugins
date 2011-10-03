#!/usr/bin/env ruby

# because CloudKick wants a license to merge...
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <lo@petalphile.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return 
# ----------------------------------------------------------------------------

### the script:

# takes HAProxy stats and grabs connections, rate, and check time
# for every listener and every backend server, using a format like
# "metric groupname_servername_request_rate int 10

# variables you may actually need to change

# change this if the file is elsewhere
config	= "/etc/haproxy/haproxy.cfg" || raise("Expecting haproxy configuration file in /etc/haproxy/haproxy.cfg")

# grab the statistics socket from above
socket	= `awk '/stats socket/ {print $3}' #{config}`.chomp || raise("Expecting \'stats socket <UNIX_socket_path>\' in #{config}")

# where haproxy lives and pid (either in conf or static location)
exec    = `which haproxy`.chomp || raise("Where the F is haproxy?")
pid	= `pidof haproxy`.chomp.to_i || nil



if ( pid )
	puts "status ok haproxy is running"
	conn = `lsof -ln -i |grep -c #{pid}`.chomp.to_i
# removes the listener and stats socket
	conn = conn - 2
	puts "metric connections int #{conn}"
# grab statistics from the socket

	require 'socket'

	ctl=UNIXSocket.new(socket)
	ctl.puts "show stat"

	while (line = ctl.gets) do
		if (line =~ /^[^#]\w+/)
			line = line.split(",")
			host = "#{line[0]}_#{line[1]}"
			puts "metric #{host}_request_rate int #{line[47]}" if line[47].to_i > 0
			puts "metric #{host}_total_requests gauge #{line[49]}" if line[49].to_i > 0
			puts "metric #{host}_health_check_duration int #{line[35]}" if line[35].to_i > 0
			puts "metric ${host}_current_queue int #{line[3]}" if line[3].to_i > 0
		end
	end

	ctl.close

else
	puts "status err haproxy is not running!"
end
