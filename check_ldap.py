#!/usr/bin/env python
#
# License: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
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
