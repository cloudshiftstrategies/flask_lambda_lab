#!/usr/bin/env python
"""
This script creates (or updates) 2 s3 buckets. One for uploads and the
other bucket is to store thumbnails. We then write the bucket names
tothe bucketConfig file.

The buckets must be created in the same region that the lambda function
lives becuase we will later create a trigger between the s3 uploads bucket
and the s3_eventTrigger function. We get the region name from the
zappa_settings file
"""

import boto3, json, uuid

bucketConfig = 'bucketConfig.py'
bucketAcl = 'public-read'
uploadBucket = None
thumbBucket = None

# Determine the region that we published the function
# Becuase s3 triggers must be in same region as function
zappa_settings = 'zappa_settings.json'
with open(zappa_settings) as data_file:
   data = json.load(data_file)
stage=data.keys()[0]
region=data[stage]['aws_region']

print "Using aws region: %s" % region

uploadPrefix = "flasklambdalab-%s-uploads-" %stage
thumbPrefix = "flasklambdalab-%s-thumbnails-" %stage

# Create location constraint dict. 
# NOTE: with AWS boto3 API, if you dont provide a location (region) 
# contraint, it will put the bucket in the primary region (us-east-1). 
# If you want the bucket to be created in any other region, you must 
# supply a region location constraint. 
# The odd behavior is that if you specifiy 'us-east-1' as a region via
# the location constraint, it will error out. Go figure. 

# Create an s3 client object
client = boto3.client('s3')

# Get a listing of all buckets for this AWS acct
for bucket in client.list_buckets()['Buckets']:
    # Check to see if the bucket has our upload pattern
    if uploadPrefix in bucket['Name']:
        # We found one... make sure its in the correct region
        bucketRegion = client.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint']
        if bucketRegion == None: bucketRegion = 'us-east-1'
        if bucketRegion == region:
            #its in the right region, get the bucket name
            uploadBucket = bucket['Name']
            print "Found existing upload bucket: '%s'" % uploadBucket

    # Check to see if the bucket has our thumb pattern
    if thumbPrefix in bucket['Name']:
        # We found one... make sure its in the correct region
        bucketRegion = client.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint']
        if bucketRegion == None: bucketRegion = 'us-east-1'
        if bucketRegion == region:
            #its in the right region, get the bucket name
            thumbBucket = bucket['Name']
            print "Found existing thumb bucket: '%s'" % thumbBucket

# Check to see if the previous loop found an upload bucket
if not uploadBucket:
    # It did not.. need to create one
    # Set the new bucket name
    uploadBucket = uploadPrefix + str(uuid.uuid1())[:8]
    # And create the bucket
    print "Creating upload bucket: '%s'" % uploadBucket
    if region == 'us-east-1':
        client.create_bucket(Bucket=uploadBucket)
    else:
        client.create_bucket(Bucket=uploadBucket,
                CreateBucketConfiguration = {'LocationConstraint': region})

# Check to see if the previous loop found a thumb bucket
if not thumbBucket:
    # It did not.. need to create one
    # Set the new bucket name
    thumbBucket = thumbPrefix + str(uuid.uuid1())[:8]
    # And create the bucket
    print "Creating thumb bucket: '%s'" % thumbBucket
    if region == 'us-east-1':
        client.create_bucket(Bucket=thumbBucket)
    else:
        client.create_bucket(Bucket=thumbBucket,
                CreateBucketConfiguration = {'LocationConstraint': region})

# Set the ACLs for the bucket (new or existing)
print "Setting bucket ACLs: '%s'" % bucketAcl
client.put_bucket_acl(Bucket=uploadBucket, ACL=bucketAcl)
client.put_bucket_acl(Bucket=thumbBucket, ACL=bucketAcl)

# Create a webserver for the bucket
webConfig = { "IndexDocument": { "Suffix": "index.html" } }
print "Creating bucket Websites"
client.put_bucket_website(Bucket=uploadBucket, WebsiteConfiguration=webConfig)
client.put_bucket_website(Bucket=thumbBucket, WebsiteConfiguration=webConfig)

# Enable CORS for the s3 Bucket
corsConfig = { 'CORSRules':[ {
                'AllowedOrigins': [ '*' ],
                'AllowedMethods': [ 'GET', 'POST' ],
            } ] }
print "Enabling CORS on buckets"
client.put_bucket_cors(Bucket=uploadBucket, CORSConfiguration=corsConfig)
client.put_bucket_cors(Bucket=thumbBucket, CORSConfiguration=corsConfig)

# Write the bucket name to the config file for use in application
print "Writing config file: '%s'" % bucketConfig
cfgFile = open(bucketConfig, 'w')
cfgFile.write("UPLOAD_BUCKET = '%s'\n" % uploadBucket)
cfgFile.write("THUMB_BUCKET = '%s'\n" % thumbBucket)
