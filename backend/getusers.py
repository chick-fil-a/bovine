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

def invoke_get_users(account):
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
    users = json.loads(data.get('body')).get('Users')
    return users

def get_users(account):
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
        results = pool.map(invoke_get_users, account_map)
        pool.close()
        pool.join()
        user_data = [item for sublist in results for item in sublist]
        end = time.time()
        return user_data,(end-start)
    else:
        # running for a single account
        end = time.time()
        account_data = aws_accounts.with_number(account)
        data = get_users_for_account(account_data)
        return data,(end-start)

def get_users_for_account(account):
    session = boto3.session.Session()  # create session for Thread Safety
    assume = rolesession.assume_crossact_audit_role(
        session, account['accountNum'], 'us-east-1')
    users_info = []
    if assume:
        iam = assume.client('iam')
        users_info = iam.list_users().get('Users')
        if users_info is None:
            return dict(
                Account=dict(accountNum=account),
                Instance=dict(message='Error'))
    else:
        print("[X] Assume failed.")
        
    data = []
    for user in users_info:
        if user.get('PasswordLastUsed'):
            password_set = True
        else:
            password_set = False
        data.append(
            dict(
                Username=user.get('UserName'),
                CreateDate=user['CreateDate'].isoformat(),
                PasswordSet=password_set,
                AccountNum=account['accountNum'],
                AccountAlias=account['alias']))
    return data

def lambda_handler(event,context):
    global function_name
    function_name = context.function_name
    account = None
    query_params = event.get('queryStringParameters')
    if query_params:    
        account = query_params.get('account')
        if account == 'all':
            account = None    
    results,run_time = get_users(account)
    body = dict(Users=results,Time=run_time)
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response

if __name__ == "__main__":
    resp = lambda_handler(None,None)
    print resp