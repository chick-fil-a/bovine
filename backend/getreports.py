""" BOVI(n)E getreports endpoint. """
import json
import os

import boto3


REPORTS_BUCKET = os.environ['REPORTS_BUCKET']
STAGE = os.environ['STAGE']


def get_reports(report=None):
    """ Get compliance reports """
    s3_client = boto3.client('s3')
    print "Report: %s" % report
    if not report:
        # print REPORTS_BUCKET
        report_data = []
        s3_objects = s3_client.list_objects(Bucket=REPORTS_BUCKET)['Contents']
        for obj in s3_objects:
            if 'compliance-audit-report' in obj['Key']:
                report_data.append(dict(Report=obj['Key'].split(
                    '/')[0], LastModified=str(obj['LastModified'])))
    else:
        # print REPORTS_BUCKET
        s3_key = report + '/compliance-audit-report.json'
        report_data = s3_client.get_object(Bucket=REPORTS_BUCKET, Key=s3_key)[
            'Body'].read()
        return json.loads(report_data)
    return report_data


def lambda_handler(*kwargs):
    """ Lambda handler """
    print kwargs[0]
    report = None
    params = kwargs[0].get('queryStringParameters')
    if params:
        report = params.get('report')
        print report
    results = get_reports(report)
    body = results
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response
