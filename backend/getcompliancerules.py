""" BOVI(n)E getcompliancerules endpoint """
import json
import os

import boto3


RULES_BUCKET = os.environ['RULES_BUCKET']
STAGE = os.environ['STAGE']


def get_rules():
    """ Get all compliance rules """
    s3_client = boto3.client('s3')
    rules_data = []
    s3_objects = s3_client.list_objects(Bucket=RULES_BUCKET)['Contents']
    for obj in s3_objects:
        raw_rules = json.loads(s3_client.get_object(
            Bucket=RULES_BUCKET, Key=obj['Key'])['Body'].read())
        for rule in raw_rules:
            rule = json.loads(json.dumps(rule))
            # print rule
            if rule.get('enabled'):
                rule_info = {
                    'name': rule['actions'][0]['params']['name'],
                    'description': rule['actions'][0]['params']['description'],
                    'priority': rule['actions'][0]['params']['priority']
                }
                rules_data.append(
                    dict(Service=obj['Key'].split('.')[0], Rule=rule_info))
    # print rules_data
    return dict(Rules=rules_data)


def lambda_handler(*kwargs):
    """ Lambda handler """
    print kwargs
    results = get_rules()
    body = results
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response
