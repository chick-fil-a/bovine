""" BOVI(n)E main lambda function. """

import json
import urllib
import os
import base64

import boto3


S3_BUCKET = os.environ['S3_BUCKET']
STAGE = os.environ['STAGE']
AUTH_URL = os.environ['AUTH_URL']
URL = os.environ['URL']
AUDIT_ROLE = os.environ['AUDIT_ROLE']


def build_config():
    """ Build BOVI(n)E auth config. """
    config = {
        "auth_url": AUTH_URL,
        "url": URL,
        "audit_role": AUDIT_ROLE
    }
    return config


def lambda_handler(*kwargs):
    """ BOVI(n)E main lambda"""
    headers = kwargs[0]['headers']
    cookies = headers.get('Cookie')
    if cookies:
        session_cookie = urllib.unquote(cookies).split('=')[1]
    else:
        session_cookie = 'undefined'

    if session_cookie == 'undefined':
        # WARNING: this is not secure. Cookie should be validated as
        # well...TODO
        body = {"msg": "No session cookie present"}
        location = AUTH_URL
        headers = {"Location": location}
        response = {
            "statusCode": 302,
            "body": json.dumps(body),
            "headers": headers
        }
        return response

    headers = {
        "Content-Type": "text/html"
    }

    path = kwargs[0]['requestContext']['path']
    s3_client = boto3.client('s3')
    s3_key = path[1:]
    print "S3 key: %s" % s3_key
    encoded = False

    if path == '/' or path == '':
        s3_key = "index.html"
        content = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)['Body'].read()
    elif path == '/config.json':
        config = build_config()
        content = json.dumps(config)
    elif path == '/favicon.ico':
        headers = {
            "Content-Type": "image/x-icon"
        }
        encoded = True
        content = base64.b64encode(s3_client.get_object(
            Bucket=S3_BUCKET, Key=s3_key)['Body'].read())
    elif '.png' in path:
        headers = {
            "Content-Type": "image/png"
        }
        encoded = True
        content = base64.b64encode(s3_client.get_object(
            Bucket=S3_BUCKET, Key=s3_key)['Body'].read())
    elif '.css' in path:
        headers = {
            "Content-Type": "text/css"
        }
        content = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)['Body'].read()
    elif path.endswith(".js"):
        headers = {
            "Content-Type": "text/javascript"
        }
        print s3_key
        content = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)['Body'].read()
    elif path.endswith(".woff2") or path.endswith(".woff") or path.endswith(".ttf"):
        headers = {
            "Content-Type": "binary/octet-stream",
        }
        encoded = True
        content = base64.b64encode(s3_client.get_object(
            Bucket=S3_BUCKET, Key=s3_key)['Body'].read())
    else:
        print "ELSE: %s" % s3_key
        content = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)['Body'].read()
    print s3_key

    response = {
        "statusCode": 200,
        "body": content,
        "headers": headers,
        "isBase64Encoded": encoded
    }
    return response
