
import boto3
from boto3.dynamodb.conditions import Key
import json


def get_accounts():
    dynamo = boto3.resource('dynamodb').Table('AWS-Accounts-Table')
    response = dynamo.scan(
        AttributesToGet=['accountNum',
                         'alias',
                         'email',
                         'AccountOwner',
                         'remediate'])
    #for i in response['Items']:
    #    print(i)
    return response['Items']
    
def lambda_handler(context,event):
    results = get_accounts()
    body = results
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response

if __name__ == "__main__":
    resp = lambda_handler(None,None)
    print resp

