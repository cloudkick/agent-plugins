#!/usr/bin/ruby

##################
#
# This is all sorts of dirty, but we've all been in situations where
# some software spits errors into a logfile, and if we had looked for
# and caught such errors, we'd have avoided pain.
#
# This script was written by lo@petalphile.com.  You can do whatever
# you want with it, but there is no warranty and you should feel 
# free to send a thank you along with *tasty* whiskey.
#
##################

if (ARGV.length < 2 || ARGV[0] !~ /\w+/ || ARGV[1] !~ /\w+/)
	puts "Searches for an error in the last 100 lines of a log file.
usage: #{$0} <file> <warning> <optional:number of lines to parse>
	where <file> is the full path to the log file we're checking
	and <warning> is the string we should alert on.  
	and the optional third field is number of lines of <file> to read.  If empty, this is 100 lines."
	exit 1
end

lines = ARGV[2]
if ( lines =~ /^\d+$/ )
	lines = lines.to_i
elsif ( lines == '' || lines == nil )
	lines = 100
else
	puts "the optional third argument must be an integer!"
	exit
end
	

file = ARGV[0]
warning = ARGV[1]

logentries = []
logentries=`/usr/bin/tail -#{lines} #{file} |grep -e "#{warning}"`

if (logentries.size > 0)
	puts "status err bad entires for \"#{warning}\" in #{file}"
else
	puts "status ok ok"
end

