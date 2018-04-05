""" BOVI(n)E getroles endpoint. """
from multiprocessing.dummy import Pool
import time
import json

import boto3

from lib import rolesession
from lib.awsaccounts import AwsAccounts


def invoke_get_roles(account):
    """ Invoke lambda function to get roles from a
        specific AWS account.
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
    roles = json.loads(data.get('body')).get('Roles')
    return roles


def get_roles(function_name, account):
    """ Get IAM roles for all accounts.
    :param account: AWS account
    """
    start = time.time()
    aws_accounts = AwsAccounts()
    if not account:
        # running for all accounts, fan out Lambdas to make it faster
        account_list = aws_accounts.all(attr=['accountNum', 'alias'])
        pool = Pool(10)
        account_map = []
        for acc in account_list:
            acc['function_name'] = function_name
            account_map.append(acc)
        results = pool.map(invoke_get_roles, account_map)
        pool.close()
        pool.join()
        role_data = [item for sublist in results for item in sublist]
        end = time.time()
    else:
        # running for a single account
        end = time.time()
        account_data = aws_accounts.with_number(account)
        role_data = get_roles_for_account(account_data)
    return role_data, (end - start)


def get_roles_for_account(account):
    """ Get IAM roles for a specific account.
    :param account: AWS account
    """
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


def lambda_handler(*kwargs):
    """ Lambda handler function.
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
    results, run_time = get_roles(function_name, account)
    body = dict(Roles=results, Time=run_time)
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response
