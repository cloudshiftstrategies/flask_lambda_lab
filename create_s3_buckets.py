#!/bin/env python
import boto3, uuid

uploadPrefix = 'flasklambdalab-uploads-'
thumbPrefix = 'flasklambdalab-thumbnails-'

bucketConfig = 'bucketConfig.py'
bucketAcl = 'public-read'
uploadBucket = None
thumbBucket = None

# Create an s3 client object
client = boto3.client('s3')

# Get a listing of all buckets for this AWS acct
for bucket in client.list_buckets()['Buckets']:
    # Check to see if the bucket has our upload pattern
    if uploadPrefix in bucket['Name']:
        # We found one... get the name
        uploadBucket = bucket['Name']
        print "Found existing upload bucket: '%s'" % uploadBucket
    # Check to see if the bucket has our thumb pattern
    if thumbPrefix in bucket['Name']:
        # We found one... get the name
        thumbBucket = bucket['Name']
        print "Found existing thumb bucket: '%s'" % thumbBucket

# Check to see if the previous loop found an upload bucket
if not uploadBucket:
    # It did not.. need to create one
    # Set the new bucket name
    uploadBucket = uploadPrefix + str(uuid.uuid1())[:8]
    # And create the bucket
    print "Creating upload bucket: '%s'" % uploadBucket
    client.create_bucket(Bucket=uploadBucket)

# Check to see if the previous loop found an thumb bucket
if not thumbBucket:
    # It did not.. need to create one
    # Set the new bucket name
    thumbBucket = thumbPrefix + str(uuid.uuid1())[:8]
    # And create the bucket
    print "Creating thumb bucket: '%s'" % thumbBucket
    client.create_bucket(Bucket=thumbBucket)

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
