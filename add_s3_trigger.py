#!/bin/env python
import json, datetime, os, bucketConfig
from pprint import pprint
from shutil import copyfile

# Parameters
zappa_settings = 'zappa_settings.json'
# Name of the function that we will call with trigger
triggerFunction = "app.events.s3_uploadTrigger"

# Create backup dir
backupDir = 'backup'
if not os.path.exists(backupDir):
    os.mkdir(backupDir)

# Backup the zappa settings file
datestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
backupFile = "%s/%s.%s.json" %(backupDir, zappa_settings[:-5], datestamp)
print "Backing up zappa_settings to %s " %backupFile
copyfile( zappa_settings, backupFile )

# Read the zappa setting json file
with open(zappa_settings) as data_file:
    data = json.load(data_file)

# Isert our event trigger into the zappa json config
data["dev"]["events"] = [{
            "function": "%s" % triggerFunction,
            "event_source": {
                  "arn":  "arn:aws:s3:::%s" %bucketConfig.UPLOAD_BUCKET,
                  "events": [
                    "s3:ObjectCreated:*"
                  ]
               }
            }]

# Write th json to the zappa config file
print "Writing up zappa_settings to %s " % zappa_settings
data_file = open(zappa_settings,'w')
data_file.write(json.dumps(data, indent=4))
data_file.close()
