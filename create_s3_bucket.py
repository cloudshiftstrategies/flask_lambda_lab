#!/bin/env python
import boto3, uuid

bucketPrefix = 'flasklambdalab-uploads-'
bucketName = None
bucketAcl = 'public-read'
bucketConfig = 'bucketConfig.py'

# Create an s3 client object
client = boto3.client('s3')

# Get a listing of all buckets for this AWS acct
for bucket in client.list_buckets()['Buckets']:
    # Check to see if the bucket has our Name pattern
    if bucketPrefix in bucket['Name']:
        # We foudn one... get the name
        bucketName = bucket['Name']
        print "Found existing bucket: '%s'" % bucketName
# Check to see if the previous loop found a bucket
if not bucketName:
    # It did not.. need to create one
    # Set the new bucket name
    bucketName = bucketPrefix + str(uuid.uuid1())[:8]
    # And create the bucket
    print "Creating bucekt: '%s'" % bucketName
    client.create_bucket(Bucket=bucketName)

# Set the ACLs for the bucket (new or existing)
print "Setting bucket ACL: '%s'" % bucketAcl
client.put_bucket_acl(Bucket=bucketName, ACL=bucketAcl)

# Create a webserver for the bucket
bucketWebSite = 'http://%s.s3.amazonaws.com/' % bucketName
webConfig = { "IndexDocument": { "Suffix": "index.html" } }
print "Creating bucket Website: '%s'" % bucketWebSite
client.put_bucket_website(Bucket=bucketName, WebsiteConfiguration=webConfig)

# Enable CORS for the s3 Bucket
corsConfig = { 'CORSRules':[ {
                'AllowedOrigins': [ '*' ],
                'AllowedMethods': [ 'GET', 'POST' ],
            } ] }
print "Enabling CORS on bucket"
client.put_bucket_cors(Bucket=bucketName, CORSConfiguration=corsConfig)

# Write the bucket name to the config file for use in application
print "Writing config file: '%s'" % bucketConfig
cfgFile = open(bucketConfig, 'w')
cfgFile.write("BUCKET_NAME = '%s'" % bucketName)
