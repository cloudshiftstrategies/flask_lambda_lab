#!/usr/bin/env python
"""
This script adds a trigger to the zappa_settings file
The Trigger is for the UPLOAD_BUCKET defined in the bucket_config file
And calls our app/events.py s3_uploadTrigger() function
"""

import json, datetime, os, bucketConfig
from pprint import pprint
from shutil import copyfile

# Parameters
zappa_settings = 'zappa_settings.json'
# Name of the function that we will call with trigger
triggerFunction = "app.events.s3_uploadTrigger"
# Name of the event on s3 bucket
s3event = 's3:ObjectCreated:Post'
# set the Upload bucket's ARN
bucketArn = "arn:aws:s3:::%s" % bucketConfig.UPLOAD_BUCKET

# Create backup dir
backupDir = './backups'
if not os.path.exists(backupDir):
    os.mkdir(backupDir)

# Make sure that the zappa_settings file exists
if not os.path.isfile(zappa_settings):
    print "Required file: %s doesnt exist. quitting" % zappa_settings
    print "Try running 'zappa init' or get a copy from: %s" %backupDir
    exit(1)

# Backup the zappa settings file
datestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
backupFile = "%s/%s.%s" %(backupDir, zappa_settings, datestamp)
print "Backing up zappa_settings to %s" %backupFile
copyfile( zappa_settings, backupFile )

# Read the zappa setting json file
with open(zappa_settings) as data_file:
    data = json.load(data_file)

stage = data.keys()[0]

# Insert our event trigger into the zappa json config
data[stage]["events"] = [{
            "function": "%s" % triggerFunction,
            "event_source": {
                  "arn":  "%s" %bucketArn,
                  "events": [
                    "%s" % s3event
                  ]
               }
            }]

# Tell the user what we are doing
print "Configurting s3 event: '%s'" %s3event
print " On s3 bucket: '%s'" %bucketArn
print " That triggers function: '%s'" %triggerFunction

# Write the json to the zappa config file
print "Writing these settings to %s" % zappa_settings
data_file = open(zappa_settings,'w')
data_file.write(json.dumps(data, indent=4))
data_file.close()
