# config.py

import os
basedir = os.path.abspath(os.path.dirname(__file__))

SITE_TITLE = "Flask Lambda Lab"
SITE_ICON = "https://s3-us-west-2.amazonaws.com/flasklambdalab-static/lambda_icon.png"
LAB_BLOG_URL = "http://www.cloudshiftstrategies.com/flasklambdalab.html"

PAGES=[
    {"title":"Lab Blog","url":LAB_BLOG_URL},
    ]


# Bootstrap CSS files to include in each page included in ./app/templates/base.html
CSS_INCLUDES=[
    'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css',
    'https://maxcdn.bootstrapcdn.com/bootswatch/3.3.7/cerulean/bootstrap.min.css',
    'https://cdn.datatables.net/1.10.15/css/dataTables.bootstrap.min.css',
    ]

# Bootstrap JS files to include in each page included in ./app/templates/base.html
JS_INCLUDES=[
    'https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js',
    'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js',
    'https://cdn.datatables.net/1.10.15/js/dataTables.bootstrap.min.js',
    'https://cdn.datatables.net/1.10.15/js/jquery.dataTables.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/jquery.form/4.2.1/jquery.form.min.js',
    ]
