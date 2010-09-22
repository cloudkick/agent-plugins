#!/usr/bin/env python
#
# Cloudkick plugin for monitoring a Solr core.
#
# Plugin takes the following arguments:
#
# 1 - URL to the Solr core stats.jsp page,
# 2. realm,
# 3. username,
# 4. password
#
# Arguments 2, 3 and 4 are optional and should only be specified if your Solr page is protected with a HTTP basic auth.
#

import sys
import socket
import urllib2
import xml.dom.minidom as minidom

DEFAULT_URL = 'http://localhost:8983/solr/core0/admin/stats.jsp'
DEFAULT_TIMEOUT = 4

METRICS = {
              'org.apache.solr.search.SolrIndexSearcher': ['numDocs', 'maxDocs'],
              'org.apache.solr.handler.ReplicationHandler': ['indexSize'],
              'org.apache.solr.handler.XmlUpdateRequestHandler': ['requests', 'errors', 'timeouts'],
}

METRIC_MAPPINGS = {
                  'numDocs': {'type': 'int', 'display_name': 'documents_number'},
                  'maxDocs': {'type': 'int', 'display_name': 'maximum_documents'},
                  'indexSize': {'type': 'float', 'display_name': 'index_size'},
                  'requests': {'type': 'gaugae', 'display_name': 'update_handler_requests'},
                  'errors':  {'type': 'gaugae', 'display_name': 'update_handler_errors'},
                  'timeouts': {'type': 'gaugae', 'display_name': 'update_handler_timeouts'}
}

def main():
  arg_len = len(sys.argv)

  if arg_len >= 2:
    solr_url = sys.argv[1]
  else:
    solr_url = DEFAULT_URL

  if arg_len == 5:
    realm = sys.argv[2]
    username = sys.argv[3]
    password = sys.argv[4]

    auth_handler = urllib2.HTTPBasicAuthHandler()
    auth_handler.add_password(realm = realm, uri = solr_url, user = username, passwd = password)
    opener = urllib2.build_opener(auth_handler)

    urllib2.install_opener(opener)

  socket.setdefaulttimeout(DEFAULT_TIMEOUT)
  try:
    response = urllib2.urlopen(solr_url)
    body = response.read()
  except  urllib2.HTTPError, e:
    print 'status err Failed to retrieve stats - status code: %s' % (e.code)
    sys.exit(1)
  except (urllib2.URLError, Exception), e:
    print 'status err Failed to retrieve stats: %s' % (str(e)[:23])
    sys.exit(1)

  try:
    metric_values = parse_response(body)
  except Exception, e:
    print 'status err Failed to parse metrics: %s' % (str(e)[:23])
    sys.exit(1)

  if not metric_values:
    print 'status err Failed to retrieve metrics %s' % (', ' .join(METRIC_MAPPINGS.keys())[:21])
    sys.exit(1)

  print_METRICS(metric_values)

def parse_response(response):
  root = minidom.parseString(response)
  stat_elements = root.getElementsByTagName('stat');

  metric_values = {}
  for element in stat_elements:
    class_name = element.parentNode.parentNode.getElementsByTagName('class')[0].childNodes[0].data.strip()

    if class_name in METRICS.keys():
      child_nodes = element.childNodes
      if child_nodes and child_nodes[0].nodeType == element.TEXT_NODE:
        name = element.getAttribute('name')
        value = child_nodes[0].data.strip()

        if name in METRICS[class_name]:
          metric_values[name] = string_value_to_mb(value)

  return metric_values

def print_METRICS(metric_values):
  print 'status ok successfully retrieved metrics'
  for key, value in metric_values.items():
    type = METRIC_MAPPINGS.get(key).get('type')
    display_name = METRIC_MAPPINGS.get(key).get('display_name')
    print 'metric %s %s %s' % (display_name, METRIC_MAPPINGS.get(key).get('type'), value)

def string_value_to_mb(value):
  units = [('b', (1 / 1024.0 / 1024.0)), ('kb', (1 / 1024.0)), ('mb', 1), ('gb', 1024), ('tb', 1024 * 1024)]

  value = value.lower()
  for (unit, factor) in units:
    if value.find(' %s' % (unit)) != -1:
      value = value.replace(unit, '').strip()
      value = int(float(value))
      value = value * factor
      break

  return value

main()
