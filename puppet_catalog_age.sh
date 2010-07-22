#!/bin/bash

# puppet_catalog_age.sh: Check how old the puppet catalog is. If the puppet 
# catalog on a machine hasn't been updated in a while, you likely have an 
# error in your puppet config.

# Different versions of puppet keep their catalog files in different places. 0.25+ seems to use this path.
CATALOG_TIME=`stat -c %Y /var/lib/puppet/client_yaml/catalog/\`hostname\`.yaml`
CURRENT_TIME=`date +%s`
CATALOG_AGE=$((CURRENT_TIME - CATALOG_TIME))

# Puppet catalog should be updated every 30 minutes. If it's been three hours, something is wrong.
if [ "$CATALOG_AGE" -gt "10800" ]
then
  echo "status err Puppet catalog age is $CATALOG_AGE seconds"
elif [ "$CATALOG_AGE" -gt "7200" ]
then
  echo "status warn Puppet catalog age is $CATALOG_AGE seconds"
else
  echo "status ok Puppet catalog age is $CATALOG_AGE seconds"
fi

echo "metric puppet_catalog_age int $CATALOG_AGE"
