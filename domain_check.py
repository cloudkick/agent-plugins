#!/usr/bin/python
# A CloudKick plugin to monitor the status of a domain.
# If the domain is taken, an 'ok' status is returned.
# If the domain is free, a 'warn' status is returned.
#
# Verified working TLD types:
# com
# net
# org
# co.uk
# us
# tv
# info
#
# Used to watch for domains you want to purchase but are
# taken. =) Sure, you can pay for this service, but I'd
# rather get an SMS and jump on GoDaddy personally.
#
# Accepts multiple domains to avoid having to use multiple
# plugin rules.
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
import sys

def domainIsTaken(domain):
   """
   Checks to see if a domain is taken or if a domain is free.
   If domain is taken: True is returned
   If domain is free: False is returned
   """
   command = 'whois %s' % (domain,)
   status, out = commands.getstatusoutput(command)
   if status != 0:
       msg = "status err Unable to fetch whois for %s\n" % (domain,)
       sys.stderr.write(msg)
       sys.exit(1)

   if 'Registrar:' in out:
       return True
   else:
       return False

def main():
    # Remove our program name from sys args
    domains = sys.argv[1:]
    
    # If no domains found, raise an error.
    if len(domains) < 1:
        msg = 'status err no domains provided.\n'
        sys.stderr.write(msg)
        sys.exit(1)

    # Iterate through each domain
    for domain in domains:
        # If taken, skip to next domain.
        if domainIsTaken(domain):
            continue
        # If we find one not taken - alert.
        else:
            msg = "status warn %s is not registered.\n" % (domain,)
            sys.stdout.write(msg)
            sys.exit(0)

    # No domains are available
    msg = "status ok No domains available to register.\n"
    sys.stdout.write(msg)
    sys.exit(0)

# Main
if __name__ == '__main__':
    main()
