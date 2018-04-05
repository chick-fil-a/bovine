""" BOVI(n)E getusers endpoint. """
from multiprocessing.dummy import Pool
import time
import json

import boto3
from lib import rolesession
from lib.awsaccounts import AwsAccounts


def invoke_get_users(account):
    """ Invoke lambda function to get users for a specific
        account.
    :param account: AWS account
    """
    client = boto3.client('lambda')
    payload = {
        "queryStringParameters": {
            "account": account['accountNum']
        }
    }
    response = client.invoke(
        FunctionName=account['function_name'],
        Payload=json.dumps(payload),
        InvocationType='RequestResponse'
    )
    data = json.loads(response['Payload'].read())
    users = json.loads(data.get('body')).get('Users')
    return users


def get_users(function_name, account):
    """ Get users for all accounts.
    :param account: AWS account
    """
    start = time.time()
    user_data = []
    aws_accounts = AwsAccounts()
    if not account:
        # running for all accounts, fan out Lambdas to make it faster
        account_list = aws_accounts.all(attr=['accountNum', 'alias'])
        pool = Pool(10)
        account_map = []
        for acc in account_list:
            acc['function_name'] = function_name
            account_map.append(acc)
        results = pool.map(invoke_get_users, account_map)
        pool.close()
        pool.join()
        user_data = [item for sublist in results for item in sublist]
        end = time.time()
        return user_data, (end - start)
    else:
        # running for a single account
        end = time.time()
        account_data = aws_accounts.with_number(account)
        data = get_users_for_account(account_data)
        return data, (end - start)


def get_users_for_account(account):
    """ Get all users for a specific AWS account.
    :param account: AWS account
    """
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
        print "[X] Assume failed."

    data = []
    for user in users_info:
        data.append(
            dict(
                Username=user.get('UserName'),
                CreateDate=user['CreateDate'].isoformat(),
                PasswordSet=bool(user.get('PasswordLastUsed')),
                AccountNum=account['accountNum'],
                AccountAlias=account['alias']))
    return data


def lambda_handler(*kwargs):
    """ Getusers lambda function.
    :param event: Lambda event
    :param context: Lambda context
    """
    function_name = kwargs[1].function_name
    account = None
    query_params = kwargs[0].get('queryStringParameters')
    if query_params:
        account = query_params.get('account')
        if account == 'all':
            account = None
    results, run_time = get_users(function_name, account)
    body = dict(Users=results, Time=run_time)
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response
