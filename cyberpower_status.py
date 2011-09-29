#!/usr/bin/python -tt

import commands
import os
import sys

def getInfo():
   """
   Get all pertinent information from our CyberPower UPS
   """
   status, out = commands.getstatusoutput('pwrstat -status')
   if status is not 0:
       msg = "Unable to find PowerPanel software.\n"
       msg += "Please install the required software and try again.\n"
       msg += status
       sys.stderr.write(msg)
       sys.exit(1)

   results = {}
   for line in out.split('\n'):
       if '.' in line:
           option = line.split('.')[0].strip()
           value = line.split('.')[-1].strip()
           # Rename the following options and pull our integers as well.
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
           # The rest are all much easier. =)
           elif option == 'Utility Voltage':
               value = int(value.split()[0])
           elif option == 'Output Voltage':
               value = int(value.split()[0])
           elif option == 'Rating Voltage':
               value = int(value.split()[0])

           results[option] = value
   
   return results

def makeMetric(ourName, ourValue, gauge=False):
    """
    Build a metric string per the documentation here:
    https://support.cloudkick.com/Creating_a_plugin
    """

    if type(ourValue) is str:
        ourType = 'string'
    elif type(ourValue) is int:
        ourType = 'int'
        if gauge is True:
            ourType = 'gauge'
    elif type(ourValue) is float:
        ourType = 'float'
    else:
        msg = 'Invalid value passed to makeMetric. Exiting.\n'
        sys.stderr.write(msg)
        sys.exit(1)

    ourName = ourName.replace(' ', '_')

    return 'metric %s %s %s\n' % (ourName, ourType, ourValue)

# Do the damn thing.
if __name__ == '__main__':
    if os.getuid() != 0:
        msg = 'This script must be run as root.\n'
        sys.stderr.write(msg)
        sys.exit(1)

    info = getInfo()
    if info:
        if info['State'] == 'Normal':
            state = 'ok'
        else:
            state = 'warn'

        # First our status message
        msg = "status %s Our %s UPS is in a '%s' state.\n" % (state, info['Model Name'], info['State'])
        # Then, metrics.
        # First, metrics where we rename the value
        #msg += makeMetric('Load Wattage',  info['Load Wattage'])
        #msg += makeMetric('Rating Wattage',  info['Rating Wattage'])
        #msg += makeMetric('Battery Percentage', info['Battery Percentage'])
        # And lastly, the boring ones.

        # Maybe we should iterate like this:
        for key, value in info.items():
            msg += makeMetric(key, value)
        # And have makeMetric decide if it's an int, float or a string.

        # Send it all to stdout and we are done.
        sys.stdout.write(msg)
        sys.exit(0)
    else:
        print 'something went wrong.'

