#!/usr/bin/env ruby

# a) checks if postfix is running.  critical if it is not
# b) warns if there are messages in postfix's queue
# c) status ok if postfix is running and b) is 0

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <lo@petalphile.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return 
# ----------------------------------------------------------------------------

postqueue=`which postqueue`.chomp

running=`ps axf |grep postfix |grep -v grep`.chomp
if ( running =~ /^(\d+)\s+pts/ )
	pid=$1
	messages=`#{postqueue} -p |grep -v "Mail queue is empty" |wc -l`.chomp.to_i
	if ( messages > 0 )
		puts "status warn #{messages} messages in the postfix queue"
	else
		puts "status ok postfix running on pid #{pid} with no pending messages"
	end
else
	puts "status critical postfix not running!"
	exit 2
end

