#!/usr/bin/env python

'''
Node statuses: grabs node statuses from the Cloudkick API, then returns metrics on how many have checks in good/warning/error state.
'''

from oauth import oauth
import urllib
try:
    import simplejson as json
except ImportError:
    import json

# TODO: automatically read these from /etc/cloudkick.conf
OAUTH_KEY    = 'xxxxxxxxxxxxxxxx'
OAUTH_SECRET = 'xxxxxxxxxxxxxxxx'

FAILURE_THRESHOLD = 0.5 # fraction of nodes that must be in bad state for this check to fail
NODE_QUERY = 'tag:cassandra tag:prod'

# You probably never need to change these
API_SERVER = 'api.cloudkick.com'
API_VERSION = '2.0'
BASE_URL = 'https://%s/%s/' % (API_SERVER, API_VERSION)

# Enabling debug will break this script's functionality as a plugin
DEBUG = False

def oauth_request(url, method, parameters):
    signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
    consumer = oauth.OAuthConsumer(OAUTH_KEY, OAUTH_SECRET)

    oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer,
                                                               http_url=url,
                                                               http_method=method,
                                                               parameters=parameters)
    oauth_request.sign_request(signature_method, consumer, None)
    url = oauth_request.to_url()
    if DEBUG: print 'url:', url

    request = urllib.urlopen(url)
    response = request.read()
    if DEBUG: print 'response:', response
    return response

def get_node_ids(query):
    node_ids = []

    response = oauth_request(BASE_URL + 'nodes', 'GET', {'query': query})

    node_json = json.loads(response)
    if not node_json:
        raise Exception('Query \"%s\" matches no nodes' % query)
    for node in node_json.values()[0]:
        node_ids.append(str(node['id']))
    return node_ids

def get_statuses(node_ids):
    statuses = []
    for node_id in node_ids:
        response = oauth_request(BASE_URL + 'status/nodes', 'GET', {'node_ids': node_id})
        status_json = json.loads(response)
        statuses.append((node_id, status_json.items()[0][1]['overall_check_statuses']))
    return statuses


node_ids = get_node_ids(NODE_QUERY)
if DEBUG: print 'node ids:', node_ids

statuses = get_statuses(node_ids)

totals = {}
for node_id, status in statuses:
    if totals.get(status) == None:
        totals[status] = 1
    else:
        totals[status] += 1

for status, total in totals.items():
    print 'metric %s_total int %s' % (status, total)

total_bad = totals.get('Error', 0) + totals.get('Warning', 0)
total_ok = totals.get('Ok', 0)
total_nodes = total_bad + total_ok
failure_ratio = total_bad / float(total_nodes)
print 'metric failure_ratio float %s' % failure_ratio

overall_status = 'err'
if failure_ratio < FAILURE_THRESHOLD:
    overall_status = 'ok'

print 'status %s %s bad, %s ok out of %s nodes' % (overall_status, total_bad, total_ok, total_nodes)
