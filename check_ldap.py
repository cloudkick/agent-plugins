#!/usr/bin/env python
#
# This Cloudkick Agent plugin attempts to bind to the specified LDAP server
# and will report an error if it is unable to do so.
#
# It depends on the 'python-ldap' library from http://www.python-ldap.org/
#
# In most cases you will only need to specify the server name
#

import ldap


SERVER = 'localhost'
USER = ''
PASS = ''
NETWORK_TIMEOUT = 5

try:
  l = ldap.open(SERVER)
  l.set_option(ldap.OPT_NETWORK_TIMEOUT, NETWORK_TIMEOUT)
  l.simple_bind(USER, PASS)
  print "status ok LDAP Bind Successful"
except ldap.LDAPError, e:
  # Error messages must be truncated to 48 characters
  print "status err %s" % str(e)[:48]
except Exception, e:
  print "status err Unknown Bind Error"
