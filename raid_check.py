#!/usr/bin/python
# CloudKick Plugin to check the status of any
# and all RAID devices on a server. Looks for
# degraded/broken arrays.
#
# Supported/Tested Devices:
# 3ware 7506
#
# Contribs welcome! If you have a RAID device you want supported,
# feel free to add support or email me and I'll be glad to add support.
# I wrote this plugin a bit "overkill" specifically to be able to
# add support for other cards/vendors easily.
#
# Copyright (C) 2011 James Bair <james.d.bair@gmail.com>
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
import re
import sys

def systemCommand(command):
    """
    Wrapper for executing a system command. Reports error to CloudKick
    as well as to standard error.
    """

    commStatus, commOut = commands.getstatusoutput(command)
    # If our command fails, abort entirely and notify CloudKick
    if commStatus != 0:
        sys.stderr.write('Error: Failure when executing the following ')
        sys.stderr.write("command: '%s'\n" % (command,))
        sys.stderr.write("Exit status: %d\n" % (commStatus,))
        sys.stderr.write("Output: %s\n\n" % (commOut,))
        sys.stderr.write('status err System command failure: ')
        sys.stderr.write('%s\n' % (command,))
        sys.exit(1)
    # If we get a 0 exit code, all is well. Return the data.
    else:
        return commOut

def ourRaidVendors():
    """
    Find if the server has RAID at all.
    If it does, return our types (lsi or 3ware).
    """

    adapters = []
    results = []
    # Put spaces around vendors to avoid accidental detection.
    vendors = (' 3ware ',)

    # Pull our info from lspci
    lspciData = systemCommand('lspci')
    for line in lspciData.split('\n'):
        if 'RAID' in line:
            adapters.append(line)

    # If we find no RAID, we are done.
    if adapters == []:
        return None

    # Find out which vendors we have
    # RAID with
    for adapter in adapters:
        for vendor in vendors:
            # Don't want double vendor entries
            if vendor in results:
                continue
            # Add our vendor in, without the spaces
            if vendor in adapter:
                results.append(vendor.strip())

    # In case we find no vendors
    if results == []:
        return None

    # Check if we have the ability to audit 3ware controllers
    # This should exit cleanly if all is well. Run outside of systemCommand()
    # so we can return a specific error message.
    if '3ware' in results:
        commStatus, commOut = commands.getstatusoutput('tw_cli show')
        if commStatus != 0:
            sys.stderr.write('status err Missing required ')
            sys.stderr.write('3ware RAID utility "tw_cli".\n')
            sys.exit(1)

    return results

def get3wareControllers():
    """
    Find all 3ware controllers on the system.
    """

    # All 3ware controllers should be c0, c1, c2 etc.
    #Ctl   Model        (V)Ports  Drives   Units   NotOpt  RRate   VRate  BBU
    #------------------------------------------------------------------------
    #c2    7506-4LP     4         4        1       0       2       -      -
    raidData = systemCommand('tw_cli show')
    results = re.findall('(c[0-9*]) ', raidData)
    return results

def get3wareStatus(controller):
    """
    Check the status of all RAID arrays on the given controller.
    """

    # Looking for the OK portion of this line:
    #Unit  UnitType  Status         %RCmpl  %V/I/M  Stripe  Size(GB)  Cache  AVrfy
    #------------------------------------------------------------------------------
    #u0    RAID-5    OK             -       -       64K     569.766   W      -
    raidData = systemCommand('tw_cli /%s show' % (controller,))
    results = re.findall('u[0-9]\s*RAID-[0-9]*\s*(\w*)', raidData)
    return results

def main():
    """
    Main function for raid_check.py
    """

    # Supported vendors - would love to extend this!
    supportedVendors = ('3ware',)

    # See if we have any RAID at all
    vendors = ourRaidVendors()

    # Make sure we have what we need
    if vendors is None:
        sys.stdout.write('status warn No RAID devices found on this system.\n')
        sys.exit(0)
    # If we have RAID, let's see if everything is okay
    else:
        # Validate it's supported
        for vendor in vendors:
            if vendor not in supportedVendors:
                sys.stdout.write("status warn Unsupported RAID vendor ")
                sys.stdout.write("'%s' found.\n" % (vendor,))
                sys.exit(0)

            # 3Ware support. Works with lists of controllers.
            if vendor == '3ware':
                controllers = get3wareControllers()
                for controller in controllers:
                    # Find the statuses
                    statuses = get3wareStatus(controller)
                    for status in statuses:
                        if status == 'OK':
                            # We print an all good if no exceptions are caught
                            # on any arrays on any controllers.
                            continue
                        else:
                            sys.stdout.write('status warn ')
                            sys.stdout.write("Failed status ")
                            sys.stdout.write("%s found on " % (status,))
                            sys.stdout.write("controller %s\n" % (controller,))
                            sys.exit(0)

            # If we are here, it's listed as supported in main(),
            # but no logic is in place.
            else:
                sys.stderr.write("status err Supported vendor ")
                sys.stderr.write("'%s' missing support.\n" % (vendor,))
                sys.exit(1)

            # If all of our controllers and RAID arrays pass without fail
            # we are good to go!
            contNum = len(controllers)
            if contNum == 1:
                contStr = 'controller'
            else:
                contStr = 'controllers'

            sys.stdout.write('status ok ')
            sys.stdout.write('Checked %d %s: ' % (contNum, contStr))
            sys.stdout.write(', '.join(controllers))
            sys.stdout.write('\n')
            sys.exit(0)

if __name__ == '__main__':
    main()
