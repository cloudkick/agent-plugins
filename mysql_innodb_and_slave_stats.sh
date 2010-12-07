#!/bin/bash

# just grabs innodb, lock tables, and slave lag for trending/graphing via cloudkick
# expects a cloudkick user with the ability to show slave and global status

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <lo@petalphile.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return 
# ----------------------------------------------------------------------------


echo "status ok ok"
mysql -ucloudkick -e 'show global status' |ruby -a -ne 'puts "metric " + $F[0] + " int " + $F[1] if $_ =~ /[^b]lock|innodb/i'
mysql -ucloudkick -e 'show slave status \G' |ruby -a -ne 'puts "metric slave_lag int " + $F[1] if $_ =~ /Seconds_Behind/'
