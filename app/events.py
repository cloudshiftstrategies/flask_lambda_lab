#!/usr/bin/env python
from __future__ import print_function
import boto3, urllib
from PIL import Image
from app import app

client = boto3.client('s3')

def s3_uploadTrigger(event, context):
    """
    Process a file upload.
    """
    # This is the size of thumbnails we will create 
    thumbSize = (200, 200)

    # Get the uploaded file's information passed to us in the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    # NOTE A bug in old version of boto3 (which lambda uses) converts
    # each space in key name to a '+', which cases downloads to break
    # It should work like this:
    #key = event['Records'][0]['s3']['object']['key']
    # But the fix is to urlencode the event string that contains key name
    #key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'].encode("utf8"))
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], )
    print("Trigger Bucket: '%s', Key: '%s'" %(bucket, key))

    # Download the uploaded file from S3 save to writable tmp space.
    filePath = '/tmp/' + key
    print("Downloading to: '%s'" %(filePath))
    client.download_file(bucket, key, filePath)

    # Create a name for the thumbnail (add "-thumb" prior to suffix)
    base = '.'.join(key.split('.')[:-1])
    ext = key.split('.')[-1]
    thumbKey = "%s-thumb.%s" % (base, ext)
    thumbPath = "/tmp/%s" % thumbKey

    # Create a thumbnail using Image library
    print("Creating Thumb size: '%s x %s'" % thumbSize)
    im = Image.open('/tmp/' + key)
    im.thumbnail(thumbSize, Image.ANTIALIAS)
    print("Saving Thumb to: '%s'" %(thumbPath))
    im.save(thumbPath)

    # Upload the thumbnail to s3 thumbnail bucket
    thumbBucket = app.config['THUMB_BUCKET']
    acl='public-read'
    print("Upload thumb: '%s' to Bucket: '%s', Key: '%s'" %(thumbPath, thumbBucket, thumbKey))
    client.put_object(Key=thumbKey, Bucket=thumbBucket,
            Body = open(thumbPath, 'rb'),
            ContentType = 'image/jpg',
            ACL = acl)

    # Get the url of the thumbnail 
    thumbUrl = '%s/%s/%s' % (client.meta.endpoint_url, thumbBucket,
            thumbKey)
    metaData={'thumburl': thumbUrl}
    # Put the thumbnail URL in the original image's metadata

    # NOTE: in reality, we'd use a database for this. But to keep
    # This lab simple, we are storing the attribute to the file
    # itself as metadata

    # Also NOTE: you can't update metadata using API. You need to 
    # do a copy operation and include the metatdata. This means
    # that we need to be careful that the S3 trigger only fires on
    # post (not * or Copy events)
    print("Storing thumbUrl: '%s' to File: '%s'" % (thumbUrl, key))
    client.copy_object(Bucket = bucket, Key = key,
            CopySource = bucket + '/' + key,
            ACL = acl,
            ContentType = 'image/jpg',
            Metadata = metaData,
            MetadataDirective='REPLACE')
