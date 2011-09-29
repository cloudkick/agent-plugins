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
   if status:
       msg = "Unable to find PowerPanel software.\n"
       msg += "Please install the required software and try again.\n"
       msg += status
       sys.stderr.write(msg)
       sys.exit(1)

   # Build our results into key: value pairs.
   results = {}
   # All values are separated by a line of periods.
   # Get the items on either side.
   for line in out.split('\n'):
       if '.' in line:
           option = line.split('.')[0].strip()
           value = line.split('.')[-1].strip()
           # Rename a few options to make them more clear.
           # Also, in making numbers ints, we lose the Volt/Watt label.
           if option == 'Load':
               option = 'Load Wattage'
                # Might as well pull out the percentage while we are here.
               results['Watt Percentage'] = int(line.split()[-2].split('(')[1])
           elif option == 'Rating Power':
               option = 'Rating Wattage'
           elif option == 'Battery Capacity':
               option = 'Battery Percentage'
           elif option == 'Remaining Runtime':
               option = 'Minutes Remaining'
               # A period after "Min" requires a different split
               value = int(line.split('.')[-2].strip().split()[0])

           # Pull the options we want as integers.
           if option in ( 'Rating Wattage', 'Battery Percentage',
                          'Utility Voltage', 'Output Voltage', 
                          'Rating Voltage', 'Load Wattage', ):
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

    # Find our type
    ourType = type(ourValue)

    # Check if it's a string, int or float.
    if ourType not in ( str, int, float ):
        msg = 'Invalid value passed to makeMetric. Exiting.\n'
        sys.stderr.write(msg)
        sys.exit(1)

    # Set to gauge if needed, otherwise change our object to it's name.
    if gauge and ourType is int:
        ourType = 'gauge'
    else:
        ourType = ourType.__name__

    # Cannot have spaces in our name, so replace_with_underscores.
    ourName = ourName.replace(' ', '_')

    # Send our metric.
    return 'metric %s %s %s\n' % (ourName, ourType, ourValue)

# MAIN
if __name__ == '__main__':
    # pwrstat requires root to poll UPS
    if os.getuid():
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
        msg = "status %s Our %s UPS is in a '%s' state.\n" % (status, 
                                                              info['Model Name'],
                                                              info['State'])
        
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
