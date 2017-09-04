#!/bin/env python
import boto3, json, uuid

uploadPrefix = 'flasklambdalab-uploads-'
thumbPrefix = 'flasklambdalab-thumbnails-'

bucketConfig = 'bucketConfig.py'
bucketAcl = 'public-read'
uploadBucket = None
thumbBucket = None

# Determine the region that we published the function
# Becuase s3 triggers must be in same region as function
zappa_settings = 'zappa_settings.json'
with open(zappa_settings) as data_file:
   data = json.load(data_file)
region=data['dev']['aws_region']
print "Using aws region: %s" % region
locationConstraint = {'LocationConstraint': region }

# Create an s3 client object
client = boto3.client('s3')

# Get a listing of all buckets for this AWS acct
for bucket in client.list_buckets()['Buckets']:
    # Check to see if the bucket has our upload pattern
    if uploadPrefix in bucket['Name']:
        # We found one... make sure its in the correct region
        bucketRegion = client.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint']
        if bucketRegion == region:
            #its in the right region, get the bucket name
            uploadBucket = bucket['Name']
            print "Found existing upload bucket: '%s'" % uploadBucket

    # Check to see if the bucket has our thumb pattern
    if thumbPrefix in bucket['Name']:
        # We found one... make sure its in the correct region
        bucketRegion = client.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint']
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
    client.create_bucket(Bucket=uploadBucket,
            CreateBucketConfiguration = locationConstraint)

# Check to see if the previous loop found a thumb bucket
if not thumbBucket:
    # It did not.. need to create one
    # Set the new bucket name
    thumbBucket = thumbPrefix + str(uuid.uuid1())[:8]
    # And create the bucket
    print "Creating thumb bucket: '%s'" % thumbBucket
    client.create_bucket(Bucket=thumbBucket,
            CreateBucketConfiguration = locationConstraint)

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
