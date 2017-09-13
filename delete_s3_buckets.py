#!/usr/bin/env python
"""
This script deletes s3 buckets used in the lab and thier contents
It also moves the zappa and bucket config files to a backup dir
"""

import json, os, boto3, datetime, shutil

# Config Settings
zappa_settings='zappa_settings.json'
bucket_config='bucketConfig.py'
backupDir='./backups'

# Make sure a zappa_settings.json file exists
if not os.path.isfile(zappa_settings):
    print "Required file: %s doesnt exist. quitting" % zappa_settings
    print "Try restoring copy from %s: or running 'zappa init'" % backupDir
    exit(1)

# Read the zappa_settings file
with open(zappa_settings) as data_file:
	data = json.load(data_file)
# Get the first stage name defined in the config file
stage=data.keys()[0]

# set the bucket name pattern
bucketStr = "flasklambdalab-%s-" %stage

# connect to s3
client = boto3.client('s3')

# list all the buckets
for bucket in client.list_buckets()['Buckets']:
    # see if bucket name matches our name pattern
    if bucketStr in bucket['Name']:
        # we have a match, but we have to delete the contents first
        print "deleting objects in bucket: %s" % bucket['Name']
        if client.list_objects(Bucket=bucket['Name']).has_key('Contents'):
            # List all the objects in the bucket
            for obj in client.list_objects(Bucket=bucket['Name'])['Contents']:
                # Delete each object
                print "  deleting object: %s" % obj['Key']
                client.delete_object(Bucket=bucket['Name'], Key=obj['Key'])
        # Now we can delete the bucket
        print "deleting bucket: %s" % bucket['Name']
        client.delete_bucket(Bucket=bucket['Name'])

# Make sure the backup directory exists
if not os.path.exists(backupDir):
    os.mkdir(backupDir)

# Backup the zappa_settings and bucket_config file
datestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
for f in (zappa_settings, bucket_config):
    backupFile = "%s/%s.%s" %(backupDir, f, datestamp)
    if os.path.isfile(f):
        print "Moving %s to %s" %(f, backupFile)
        shutil.move( f, backupFile )
