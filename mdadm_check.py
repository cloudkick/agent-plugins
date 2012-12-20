#!/usr/bin/python
# CloudKick Plugin to check the status of any
# mdadm devices on a server.
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
import os
import re
import stat
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

def which(program):
    """
    Used to find a program in the system's PATH
    Shamelessly borrowed from stackoverflow here:
    http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    """

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def findMdDevices():
    """
    Finds all /dev/md* devices on the system.
    """

    results = []
    devPath = '/dev/'
    validation = devPath + 'md'
    for device in os.listdir(devPath):
        fullPath = devPath + device
        if validation not in fullPath:
            continue
        mode = os.stat(fullPath).st_mode
        if stat.S_ISBLK(mode):
            results.append(fullPath)

    # In case we have no /dev/md* devices
    if results == []:
        results = None

    return results

def makeMetric(ourName, ourValue, gauge=False):
    """
    Build a metric string per the documentation here:
    https://support.cloudkick.com/Creating_a_plugin
    """

    # Find our type
    ourType = type(ourValue)

    # Check if it's a string, int or float.
    if ourType not in ( str, int, float ):
        msg = 'status err Invalid value passed to makeMetric. Exiting.\n'
        sys.stderr.write(msg)
        sys.exit(1)

    # Set to gauge if needed, otherwise change our object to it's name.
    if gauge and ourType is int:
        ourType = 'gauge'
    # CloudKick wants string instead of str
    elif ourType is str:
        ourType = 'string'
    else:
        ourType = ourType.__name__

    # Cannot have spaces in our name, so replace_with_underscores.
    ourName = ourName.replace(' ', '_')

    # Send our metric.
    return 'metric %s %s %s\n' % (ourName, ourType, ourValue)


def main():
    """
    Main function for mdadm_check.py
    """

    # Make sure mdadm is installed
    prog = 'mdadm'
    if not which(prog):
        msg = 'status warn %s is not installed on this system.\n' % (prog,)
        sys.stdout.write(msg)
        sys.exit(0)

    # Find our devices; exit if none found.
    devices = findMdDevices()
    if not devices:
        msg = 'status warn No mdadm devices found on this system.\n'
        sys.stdout.write(msg)
        sys.exit(0)

    # Used in reporting
    devNum = len(devices)

    # Create a dict for each device
    comp = re.compile('^\s+(\w+\s*\w*)\s+\:\s+(.*)\s*$', re.MULTILINE)
    devStats = {}
    safeStates = ( 'clean', 'active' )
    for device in devices:
        raidInfo = systemCommand('mdadm --detail %s' % (device,))
        results = dict(comp.findall(raidInfo))

        # I have no idea why, but state holds a trailing space.
        # I just strip them all. Equality for all states!
        # Also, while we are here, we try to change them from
        # a string over to a int or a float.
        for result in results:
            results[result] = results[result].strip()
            # Try an integer first
            try:
                results[result] = int(results[result])
            except:
                # Then try floating point
                try:
                    results[result] = float(results[result])
                except:
                    pass
        # Check for failed arrays
        state = results['State']
        if state not in safeStates:
            msg = "status warn Array %s is in a '%s' state.\n" % (device, state) 
            sys.stdout.write(msg)
            sys.exit(1)
        devStats[device] = results

    # It's the little things.
    if devNum == 1:
        devStr = 'device'
    else:
        devStr = 'devices'

    # Build our metrics
    msg = ''
    for device in devStats:    
        devName = device.split('/')[-1] + '_'
        for stat in devStats[device]: 
            ourName = devName + stat
            ourValue = devStats[device][stat]
            msg += makeMetric(ourName, ourValue)

    # Send the all clear
    msg += "status ok Verified the following %d %s in a clean state: %s\n" % (devNum, devStr, ' '.join(devices))
    sys.stdout.write(msg)
    sys.exit(0)

if __name__ == '__main__':
    main()
