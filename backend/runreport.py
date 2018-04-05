""" BOVI(n)E run report lambda """
import os
import json

import boto3


REPORTS_BUCKET = os.environ['REPORTS_BUCKET']
STAGE = os.environ['STAGE']
AUDIT_LAMBDA = os.environ['AUDIT_LAMBDA']


def run_report():
    """ Run BOVI(n)E audit report. """
    print "Running report..."
    lamb = boto3.client('lambda')
    lambda_resp = lamb.invoke(FunctionName=AUDIT_LAMBDA,
                              InvocationType='Event')['StatusCode']
    print lambda_resp
    return dict(Response=lambda_resp)


def lambda_handler(*kwargs):
    """ BOVI(n)E audit report lambda
    :param event: Lambda event
    :param context: Lambda context
    """
    print kwargs
    results = run_report()
    body = results
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response
