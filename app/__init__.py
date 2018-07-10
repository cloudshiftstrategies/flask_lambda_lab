from flask import Flask
from flask import render_template
app = Flask(__name__)

app.config.from_object('config')
app.config.from_object('bucketConfig')

@app.route("/")
def index():
    """
    The Home Page for our app
    """

    return render_template('index.html')

@app.route("/loadgen")
def loadgen():
    """
    A Web Page that generates load for perf testing
    """

    from time import time
    # Params to set up the workload
    iterations = 300000
    i = 0
    x = 2
    # Ready Set go (capture start time)
    start = time()
    # do the useless work to generate CPU load
    while i < iterations:
        x = x * 2
        i += 1
    # We're done
    end = time()
    # Figure out the elapsed Seconds
    seconds = end - start
    # Pass it all to the template for presentation
    return render_template('loadgen.html', iters=iterations,
            duration = seconds)

@app.route("/gallery")
def gallery():
    """
    A Page to show the image contents of a S3 bucket
    """

    from boto3 import resource, client
    # Not python 3 compatible
    #from urllib import quote
    from urllib.parse import quote

    # connect to s3
    s3 = resource('s3')
    s3client = client('s3')
    bucket = s3.Bucket(app.config['UPLOAD_BUCKET'])
    files = []

    # iterate through the filtered list of objects
    for object in bucket.objects.filter():
        file = {}
        file['name'] = object.key
        # Get object URL (could use signed URLs)
        object_url = 'http://' + object.bucket_name
        object_url += '.s3.amazonaws.com/'
        object_url += quote(object.key)
        file['url'] = object_url
        # Get the object size in KB
        object_size = round(float(object.size) / 1024, 1)
        file['size'] = object_size
        # Get the object last modified date & time (w/ out secs)
        object_date = str(object.last_modified).split("+")[0]
        file['date'] = object_date
        # Get thumburl if from object metadata
        metadata = s3client.head_object(
                Bucket = object.bucket_name,
                Key = object.key)['Metadata']
        file['thumburl'] = ''
        if 'thumburl' in metadata:
            file['thumburl'] = metadata['thumburl']
        # append file to list of files
        files.append(file)
    return render_template('gallery.html', files = files)

# Uploads Page
@app.route('/upload')
def upload():
    """
    A Really simple page to upload files to the S3 bucket
    """

    from boto3 import client
    s3 = client('s3')
    # Generate the POST URL & fields
    # This allows web clients to upload files to S3 without authenticating
    # to S3
    post = s3.generate_presigned_post(
        Bucket = app.config['UPLOAD_BUCKET'],
        Fields = {'acl': 'public-read', 'content-type': 'image/png'},
        Key =  '${filename}',
        Conditions = [{'acl': 'public-read'}, {'content-type': 'image/png'}]
    )
    return render_template('upload.html', post = post)
