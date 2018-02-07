import datetime
from multiprocessing.dummy import Pool
from time import mktime
import time
import json

import boto3
from lib import rolesession
from lib.awsaccounts import AwsAccounts

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))
        return json.JSONEncoder.default(self, obj)

def invoke_get_roles(account):
    final_data = []
    client = boto3.client('lambda')
    payload = {
        "queryStringParameters":{
            "account": account['accountNum']
        }
    }
    response = client.invoke(
        FunctionName=function_name,
        Payload=json.dumps(payload),
        InvocationType='RequestResponse'
    )
    data = json.loads(response['Payload'].read())
    roles = json.loads(data.get('body')).get('Roles')
    return roles

def get_roles(account):
    start = time.time()
    user_data = []
    aws_accounts = AwsAccounts()
    if not account:
        # running for all accounts, fan out Lambdas to make it faster
        account_list = aws_accounts.all(attr=['accountNum','alias'])
        client = boto3.client('lambda')
        user_count = 0
        pool = Pool(10)
        account_map = []
        for account in account_list:
            account_map.append(account)
        results = pool.map(invoke_get_roles, account_map)
        pool.close()
        pool.join()
        role_data = [item for sublist in results for item in sublist]
        end = time.time()
        return role_data,(end-start)
    else:
        # running for a single account
        end = time.time()
        account_data = aws_accounts.with_number(account)
        data = get_roles_for_account(account_data)
        return data,(end-start)


def get_roles_for_account(account):
    session = boto3.session.Session()  # create session for Thread Safety
    assume = rolesession.assume_crossact_audit_role(
        session, account['accountNum'], 'us-east-1')
    role_data = []
    if assume:
        iam = assume.client('iam')
        for role in iam.list_roles().get('Roles'):
            role_data.append(
                dict(Name=(role['RoleName']),
                 CreateDate=(role['CreateDate'].isoformat()),
                 Id=(role['RoleId']),
                 Arn=(role['Arn']),
                 AssumePolicy=(role['AssumeRolePolicyDocument']),
                 AccountNum=account['accountNum'],
                 AccountAlias=account['alias']))
    return role_data

def lambda_handler(event,context):
    global function_name
    function_name = context.function_name
    account = None
    query_params = event.get('queryStringParameters')
    if query_params:    
        account = query_params.get('account')
        if account == 'all':
            account = None    
    results,run_time = get_roles(account)
    body = dict(Roles=results,Time=run_time)
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response

if __name__ == "__main__":
    resp = lambda_handler(None,None)
    print resp