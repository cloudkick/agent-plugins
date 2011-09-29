#!/usr/bin/python -tt

import commands
import os
import sys

def getInfo():
   """
   Get all pertinent information from our CyberPower UPS
   """
   
   # Ensure pwrstat is present. If not, abort.
   status, out = commands.getstatusoutput('pwrstat -status')
   if status is not 0:
       msg = "Unable to find PowerPanel software.\n"
       msg += "Please install the required software and try again.\n"
       msg += status
       sys.stderr.write(msg)
       sys.exit(1)

   # Build our results into key: value pairs.
   results = {}
   # All values are separated by a line of periods. Get the items on either side.
   for line in out.split('\n'):
       if '.' in line:
           option = line.split('.')[0].strip()
           value = line.split('.')[-1].strip()
           # Start setting our numbers as integers.
           # Rename the following options as well.
           if option == 'Load':
               option = 'Load Wattage'
               value = int(value.split()[0]) 
                # Might as well pull out the percentage while we are here.
               results['Watt Percentage'] = int(line.split()[-2].split('(')[1])
           elif option == 'Rating Power':
               option = 'Rating Wattage'
               value = int(value.split()[0])
           elif option == 'Battery Capacity':
               option = 'Battery Percentage'
               value = int(value.split()[0])
           # The rest are all much easier. =) Int only.
           elif option == 'Utility Voltage':
               value = int(value.split()[0])
           elif option == 'Output Voltage':
               value = int(value.split()[0])
           elif option == 'Rating Voltage':
               value = int(value.split()[0])

           # Add our new key
           results[option] = value

      # Send the results
   return results

def makeMetric(ourName, ourValue, gauge=False):
    """
    Build a metric string per the documentation here:
    https://support.cloudkick.com/Creating_a_plugin
    """

    # Check if string, int or float.
    if type(ourValue) is str:
        ourType = 'string'
    elif type(ourValue) is int:
        ourType = 'int'
        # If an int, see if we need this as a gauge.
        if gauge is True:
            ourType = 'gauge'
    elif type(ourValue) is float:
        ourType = 'float'
    # If not a supported type, abort.
    else:
        msg = 'Invalid value passed to makeMetric. Exiting.\n'
        sys.stderr.write(msg)
        sys.exit(1)

    # Cannot have spaces in our name, so replace_with_underscores.
    ourName = ourName.replace(' ', '_')

    # Send our metric.
    return 'metric %s %s %s\n' % (ourName, ourType, ourValue)

# MAIN
if __name__ == '__main__':
    # pwrstat requires root to poll UPS
    if os.getuid() != 0:
        msg = 'This script must be run as root.\n'
        sys.stderr.write(msg)
        sys.exit(1)

    # Get our info from the UPS
    info = getInfo()
    # If we have the info, check it's state
    if info:
        if info['State'] == 'Normal':
            status = 'ok'
        else:
            status = 'warn'

        # First, build our status message based on state.
        msg = "status %s Our %s UPS is in a '%s' state.\n" % (status, info['Model Name'], info['State'])
        
        # Then, iterate through our keys
        for k, v in info.items():
            msg += makeMetric(k, v)

        # Send it all to stdout and we are done.
        sys.stdout.write(msg)
        sys.exit(0)

    # If we got here, something went wrong.
    else:
        sys.stdout.write('status err Unable to get our UPS information.\n')
        sys.exit(1)
