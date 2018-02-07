from __future__ import print_function
import json
import urllib
import os
import base64

import boto3


print('Loading function')
S3_BUCKET = os.environ['S3_BUCKET']
STAGE = os.environ['STAGE']
AUTH_URL = os.environ['AUTH_URL']
URL = os.environ['URL']

def build_config():
    config = {
        "auth_url": AUTH_URL,
        "url": URL
    }
    return config

def lambda_handler(event, context):
    print(event)
    try:
        print(urllib.unquote(event['headers']['Cookie']))
        session_cookie = urllib.unquote(event['headers']['Cookie']).split('=')[1]
        print(session_cookie)
        if session_cookie == 'undefined':
            # WARNING: this is not secure. Cookie should be validated as well...TODO
            body = {"msg": "No session cookie present"}
            location = AUTH_URL
            headers = {"Location": location}
            response = {
                "statusCode": 302,
                "body": json.dumps(body),
                "headers": headers
            }
            return response
    except Exception as e:
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

    path = event['requestContext']['path']
    s3 = boto3.client('s3')
    s3_key = path[1:]
    print("S3 key: %s" % s3_key)
    encoded = False

    if path == '/' or path == '':
        s3_key = "index.html"
        ct = s3.get_object(Bucket=S3_BUCKET, Key=s3_key)['Body'].read()
    elif path == '/config.json':
        config = build_config()
        ct = json.dumps(config)
    elif path == '/favicon.ico':
        #s3_key = 'favicon.ico'
        headers = {
            "Content-Type": "image/x-icon"
        }
        encoded = True
        ct = base64.b64encode(s3.get_object(Bucket=S3_BUCKET, Key=s3_key)['Body'].read())
    elif '.png' in path:
        #s3_key = 'favicon.png'
        headers = {
            "Content-Type": "image/png"
        }
        encoded = True
        ct = base64.b64encode(s3.get_object(Bucket=S3_BUCKET, Key=s3_key)['Body'].read())
    elif '.css' in path:
        #s3_key = event['requestContext']['path'][1:]
        headers = {
            "Content-Type": "text/css"
        }
        ct = s3.get_object(Bucket=S3_BUCKET, Key=s3_key)['Body'].read()
    elif path.endswith(".js"):
        headers = {
            "Content-Type": "text/javascript"
        }
        print(s3_key)
        ct = s3.get_object(Bucket=S3_BUCKET, Key=s3_key)['Body'].read()
    elif path.endswith(".woff2") or path.endswith(".woff") or path.endswith(".ttf"):
        headers = {
            "Content-Type": "binary/octet-stream",
        }
        encoded = True
        ct = base64.b64encode(s3.get_object(Bucket=S3_BUCKET, Key=s3_key)['Body'].read())
    else:
        print("ELSE: %s" % s3_key)
        ct = s3.get_object(Bucket=S3_BUCKET, Key=s3_key)['Body'].read()
    print(s3_key)

    response = {
        "statusCode": 200,
        "body": ct,
        "headers": headers,
        "isBase64Encoded": encoded
    }
    return response
