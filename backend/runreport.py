
import boto3
import json
import os

REPORTS_BUCKET = os.environ['REPORTS_BUCKET']
STAGE = os.environ['STAGE']
AUDIT_LAMBDA = os.environ['AUDIT_LAMBDA']

def run_report(report=None):
    print "Running report..."
    lamb = boto3.client('lambda')
    resp = lamb.invoke(FunctionName=AUDIT_LAMBDA,InvocationType='Event')['StatusCode']
    print resp
    return dict(Response=resp)
    
def lambda_handler(event,context):
    print event
    report = None
    params = event.get('queryStringParameters')
    if params:
        report = params.get('report')
        print report
    results = run_report(report)
    body = results
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response

if __name__ == "__main__":
    resp = lambda_handler(None,None)
    print resp

