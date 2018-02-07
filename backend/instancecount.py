import boto3
import datetime
from multiprocessing.dummy import Pool
from time import mktime
import time
import json

from lib import rolesession
from lib.awsaccounts import AwsAccounts


def instance_count(account=None,region='us-east-1'):
    start = time.time()
    instance_data = []
    if not account:
        aws_accounts = AwsAccounts()
        # running for all accounts, fan out Lambdas to make it faster
        account_list = aws_accounts.all(attr=['accountNum','alias'])
        account_map = []
        for account in account_list:
            account['region'] = region
            account_map.append(account)
        client = boto3.client('lambda')
        instance_count = 0
        pool = Pool(10)
        results = pool.map(invoke_instance_count, account_map)
        pool.close()
        pool.join()
        # Flatten the result
        instance_data = [item for sublist in results for item in sublist]
        end = time.time()
        final = dict(Summary=instance_data,Time=(end-start))
        return instance_data,(end-start)
    else:
        # running for a single account
        end = time.time()
        data = get_instance_count_for_account(account)
        return data,(end-start)

def invoke_instance_count(account):
    final_data = []
    client = boto3.client('lambda')
    response = client.invoke(
        FunctionName=function_name,
        Payload=json.dumps({"account":account}),
        InvocationType='RequestResponse'
    )
    data = json.loads(response['Payload'].read())
    summary = json.loads(data.get('body')).get('Summary')
    return summary

def get_instance_count_for_account(account):
    regions = ['us-east-1','us-east-2','us-west-1','us-west-2']
    data = []
    instance_count = 0
    session = boto3.session.Session()  # create session for Thread Safety
    instance_info = []
    for region in regions:
        try:
            assume = rolesession.assume_crossact_audit_role(session, account['accountNum'], region)
        except Exception,e:
            print "[X] ERROR: %s" % e
            assume = None
        if assume:
            print "Assumed into %s" % str(account)
            ec2 = assume.client('ec2')
            instances = ec2.describe_instances()['Reservations']
            for res in instances:
                instance_count += len(res['Instances'])
    
    data.append(dict(
        Account=account.get('accountNum'),
        Alias=account.get('alias'),
        InstanceCount=instance_count))
    return data

def lambda_handler(event,context):
    print event.get('account')
    global function_name
    function_name = context.function_name
    account = event.get('account')
    region = event.get('region')
    results,run_time = instance_count(account,region)
    body = dict(Summary=results,Time=run_time)
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response

if __name__ == "__main__":
    resp = lambda_handler(None,None)
    print resp