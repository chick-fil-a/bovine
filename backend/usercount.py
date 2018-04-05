""" Usercount lambda function for BOVI(n)E.
    Fronted by API GW.
"""

from multiprocessing.dummy import Pool
import time
import json

import boto3

from lib import rolesession
from lib.awsaccounts import AwsAccounts
from lib import mp_wrappers


def get_user_count(function_name, account=None):
    """ Get user count for all accounts or a specific account.
    :param account: Account to get user count
    """
    start = time.time()
    user_data = []
    if not account:
        aws_accounts = AwsAccounts()
        # running for all accounts, fan out Lambdas to make it faster
        account_list = aws_accounts.all(attr=['accountNum', 'alias'])
        new_acc_list = []
        for acc in account_list:
            acc['function_name'] = function_name
            new_acc_list.append(acc)
        print new_acc_list
        pool = Pool(10)
        results = pool.map(invoke_user_count, new_acc_list)
        pool.close()
        pool.join()
        user_data = [item for sublist in results for item in sublist]
        end = time.time()
        final_data = dict(Summary=user_data, Time=(end-start))
        return final_data
    # running for a single account
    acc_data = get_usercount_for_account(account)
    return acc_data


def invoke_user_count(account):
    """ Invocation function for Lambda.
    :param account: Account to run Lambda against
    """
    client = boto3.client('lambda')
    response = client.invoke(
        FunctionName=account['function_name'],
        Payload=json.dumps({"account": account}),
        InvocationType='RequestResponse'
    )
    data = json.loads(response['Payload'].read())
    return data


def get_usercount_for_account(account):
    """ Get user count for specific AWS account.
    :param account: Get usercount for a specific account
    """
    data = []
    user_count = 0
    session = boto3.session.Session()
    assume = rolesession.assume_crossact_audit_role(
        session, account['accountNum'], 'us-east-1')
    if assume:
        iam = assume.client('iam')
        users_info = mp_wrappers.list_users(iam)
        user_count += len(users_info)
        data.append(dict(
            Account=account.get('accountNum'),
            Alias=(account.get('alias')),
            UserCount=user_count))
    return data


def lambda_handler(*kwargs):
    """ Lambda handler for usercount
    :param event: Lambda event
    :param context: Lambda context
    """
    print kwargs[0].get('account')
    function_name = kwargs[1].function_name
    account = kwargs[0].get('account')
    results = get_user_count(function_name, account)
    body = results
    if not account:
        response = {
            "statusCode": 200,
            "body": json.dumps(body)
        }
    else:
        response = body
    return response
