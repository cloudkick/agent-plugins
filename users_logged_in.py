#!/usr/bin/python -tt
# CloudKick Plugin to see who's logged into the system.
# 
# By default, assumes that no one should be logged into the system.
# 
# Can specify --min and --max to adjust the acceptable range.
# If number of users outside of the acceptable range, a warning
# is raised. If inside the acceptable range, an ok status is raised.
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

from optparse import OptionParser

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

def main():
    """
    Main function for users_logged_in.py
    """

    minUsers=0
    maxUsers=0

    parser = OptionParser()

    parser.add_option("-m", "--min",
                      action="store", type="int",
                      help="Minimum number of users", metavar="N")
    parser.add_option("-M", "--max",
                      action="store", type="int",
                      help="Maximum number of users", metavar="N")

    (options, args) = parser.parse_args()

    # Overwrite default values if they exist
    # Specify "not None" since 0 will return False
    if options.min is not None:
        minUsers = options.min
    if options.max is not None:
        maxUsers = options.max

    # If only min users is passed, make them match.
    # If both are passed, then this is a user error.
    if minUsers > maxUsers:
        if options.min is not None and options.max is not None:
            msg = "Error: --min cannot exceed --max\n"
            sys.stderr.write(msg)
            sys.exit(1)
        else:
            maxUsers = minUsers

    # Find our users
    users = getUsersLoggedIn()

    # If object is None, no users logged in.
    if users is None:
        userMsg="No users logged in."
        userNum = 0
    # Anything else, we have users
    else:
        # Find out the number of users and
        #if we're saying "user" or "users"
        userNum = len(users)
        if userNum == 1:
            userWord = 'user'
        else:
            userWord = 'users'

        # Build our users logged in message.
        userMsg = "%d %s logged in: " % (userNum, userWord)
        userMsg += ", ".join(users)

        # Plugin spec limits status string to 48 chars.
        #
        # I have tested with over 100 chars and CloudKick
        # works just fine. Adjust/remove as you see fit, but
        # for the sake of being "correct", this line is here.
        userMsg = userMsg[:48]

    # Now, find out if we are in error or not
    if userNum < minUsers or userNum > maxUsers:
        statusMsg = 'status warn'
    else:
        statusMsg = 'status ok'

    # All done, build our strings and repot the data
    ourStatus = '%s %s\n' % (statusMsg, userMsg)
    # And build our number of users
    ourMetric = "metric users_logged_in int %d\n" % (userNum,)

    # All done.
    sys.stdout.write(ourStatus + ourMetric)
    sys.exit(0)

# Let's do this
if __name__ == '__main__':
    main()
