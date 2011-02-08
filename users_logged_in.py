#!/usr/bin/python -tt
# CloudKick Plugin to see who's logged into the system.
# Alerts if anyone is logged in. Ideally used on production 
# systems where no one should be logged in and if they are, 
# you want to know about it.
#
# Copyright (C) 2011  James Bair <james.d.bair@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import commands
import sys

def getUsersLoggedIn():
    """
    Find all users that are logged 
    into the local system and return
    either a list or a None object.
    """
    
    # Best way I can find to find users logged in
    commStatus, userData = commands.getstatusoutput('who')

    # Make sure it exits gracefully
    if commStatus != 0:
        sys.stderr.write('status err Unable to execute "who" command.\n')
        sys.exit(1)
    
    # "who" returns an empty string if no one is logged in
    if userData == '':
        users = None
    else:
        # We're going to add each user we find to a list
        users = []
        # Split up our string by lines
        userLines = userData.split('\n')
        for line in userLines:
            # Username should be the first item on the line
            users.append(line.split()[0])

    return users

# Let's do this
if __name__ == '__main__':

    # Find our users
    users = getUsersLoggedIn()

    # If we have no users, we're done.
    if users is None:
        sys.stdout.write("status ok No users logged in.\n")
        sys.stdout.write("metric users_logged_in int 0\n")
        sys.exit(0)
    # Anything else, we have users
    else:
        # Find out if it's "user" or "users"
        if len(users) == 1:
            userWord = 'user'
        else:
            userWord = 'users'
        # Build our string and report the warning
        sys.stdout.write("status warn %d %s logged in: " % (userNum, userWord))
        sys.stdout.write(", ".join(users)[:48])
        sys.stdout.write('\n')
        sys.stdout.write("metric users_logged_in int %d\n" % (userNum,))
        sys.exit(0)
