""" BOVI(n)E getaccounts endpoint """
import json

import boto3


def get_accounts():
    """ Get all AWS accounts from DynamoDB """
    dynamo = boto3.resource('dynamodb').Table('AWS-Accounts-Table')
    response = dynamo.scan(
        AttributesToGet=['accountNum',
                         'alias',
                         'email',
                         'AccountOwner',
                         'remediate'])
    return response['Items']


def lambda_handler(*kwargs):
    """ Lambda handler """
    print kwargs
    results = get_accounts()
    body = results
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response
