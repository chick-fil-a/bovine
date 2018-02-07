
import boto3
import json
import os

RULES_BUCKET = os.environ['RULES_BUCKET']
STAGE = os.environ['STAGE']

def get_rules():
    s3 = boto3.client('s3')
    rules_data = []
    s3_objects = s3.list_objects(Bucket=RULES_BUCKET)['Contents']
    for obj in s3_objects:
        raw_rules = json.loads(s3.get_object(Bucket=RULES_BUCKET, Key=obj['Key'])['Body'].read())
        for rule in raw_rules:
            rule = json.loads(json.dumps(rule))
            #print rule
            if rule.get('enabled'):
                rule_info = {
                    'name':rule['actions'][0]['params']['name'],
                    'description':rule['actions'][0]['params']['description'],
                    'priority':rule['actions'][0]['params']['priority']
                }
                rules_data.append(dict(Service=obj['Key'].split('.')[0],Rule=rule_info))
    #print rules_data
    return dict(Rules=rules_data)
    
def lambda_handler(event,context):
    results = get_rules()
    body = results
    #print json.dumps(body,indent=4)
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response

if __name__ == "__main__":
    resp = lambda_handler(None,None)
    print resp

