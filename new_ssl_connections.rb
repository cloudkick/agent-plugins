#!/usr/bin/env ruby
#################
#
# This script is a wrapper around openssl s_time to ensure
# clients can make new connections to a resource, as well
# as time those connections.
#
# OpenSSL is licensed under the OpenSSL license.
#
# This script was written by carlo@borderstylo.com and is released
# under a modified BeerWare license:  You are free to share or modify
# this script as your needs require!  There is no warranty, but if
# we ever meet, let's have beer.
#
#################

if ( ARGV.length != 1 || ARGV[0] =~ /help/ )
	puts "usage: #{$0} host:port
	checks if new ssl connections can be made to host:port
		where host can be a fqdn, ip, localhost, etc
	critical if there is a tcp error
	statistics for number of successful connections"
	exit
end

host = ARGV[0]

# seconds to test for
time = 10

openssl = `which openssl`

unless openssl =~ /\w+/
	raise("status critical #{$0} needs openssl in the \$PATH")
end

openssl=openssl.chomp

# pick one of the ciphers
cipher = `#{openssl} ciphers HIGH`.grep /:.+?:/

results = `#{openssl} s_time -connect #{host} -time #{time} -new -cipher #{cipher} 2>&1` || raise("status critical cannot test #{host}!")

# how openssl displays new connections
if results.grep /tttttttttttttttttttttttttttttttttt/ 
 	results.each do |line|
		if line =~ /^(\d+) connections in (.+)?\; (.+)? connections\/user/
			conn        = $1
			initialtime = $2
			connrate    = $3
			puts "status ok ok 
metric connections int #{conn}
metric connections_initial_time float #{initialtime}
metric connections_rate float #{connrate}"
		end
	end
else
	puts "status critical unexpected results!  try running #{openssl} s_client -connect #{host} manually"

end
