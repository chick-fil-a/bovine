from multiprocessing.dummy import Pool
import time
import json
import boto3

from lib import rolesession
from lib.awsaccounts import AwsAccounts
from lib import mp_wrappers


def get_user_count(account=None):
    start = time.time()
    user_data = []
    if not account:
        aws_accounts = AwsAccounts()
        # running for all accounts, fan out Lambdas to make it faster
        account_list = aws_accounts.all(attr=['accountNum', 'alias'])
        pool = Pool(10)
        results = pool.map(invoke_user_count, account_list)
        pool.close()
        pool.join()
        user_data = [item for sublist in results for item in sublist]
        end = time.time()
        final = dict(Summary=user_data, Time=(end-start))
        return final
    else:
        # running for a single account
        data = get_usercount_for_account(account)
        return data

def invoke_user_count(account):
    client = boto3.client('lambda')
    response = client.invoke(
        FunctionName=function_name,
        Payload=json.dumps({"account": account}),
        InvocationType='RequestResponse'
    )
    data = json.loads(response['Payload'].read())
    return data

def get_usercount_for_account(account):
    data = []
    user_count = 0
    session = boto3.session.Session()
    #user_info = []
    try:
        assume = rolesession.assume_crossact_audit_role(
            session, account['accountNum'], 'us-east-1')
    except:
        assume = None
    if assume:
        iam = assume.client('iam')
        users_info = mp_wrappers.list_users(iam)
        user_count += len(users_info)
        data.append(dict(
            Account=account.get('accountNum'),
            Alias=(account.get('alias')),
            UserCount=user_count))
    return data

def lambda_handler(event, context):
    print event.get('account')
    global function_name
    function_name = context.function_name
    account = event.get('account')
    results = get_user_count(account)
    body = results
    if not account:
        response = {
            "statusCode": 200,
            "body": json.dumps(body)
        }
    else:
        response = body
    return response

if __name__ == "__main__":
    resp = lambda_handler(None, None)
    print resp
