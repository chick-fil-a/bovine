""" BOVI(n)E instancecount endpoint. """
from multiprocessing.dummy import Pool
import time
import json

import boto3

from lib import rolesession
from lib.awsaccounts import AwsAccounts


def ec2_count(function_name, account=None, region='us-east-1'):
    """ EC2 Instance count in an AWS account
    :param account: AWS account
    :param region: AWS region
    """
    start = time.time()
    instance_data = []
    if not account:
        aws_accounts = AwsAccounts()
        # running for all accounts, fan out Lambdas to make it faster
        account_list = aws_accounts.all(attr=['accountNum', 'alias'])
        account_map = []
        for acc in account_list:
            acc['region'] = region
            acc['function_name'] = function_name
            account_map.append(acc)
        pool = Pool(10)
        results = pool.map(invoke_instance_count, account_map)
        pool.close()
        pool.join()
        # Flatten the result
        instance_data = [item for sublist in results for item in sublist]
        end = time.time()
        return instance_data, (end - start)
    else:
        # running for a single account
        end = time.time()
        data = get_instance_count_for_account(account)
        return data, (end - start)


def invoke_instance_count(account):
    """ Invoke the instance count lambda for a specific account. """
    client = boto3.client('lambda')
    response = client.invoke(
        FunctionName=account['function_name'],
        Payload=json.dumps({"account": account}),
        InvocationType='RequestResponse'
    )
    data = json.loads(response['Payload'].read())
    summary = json.loads(data.get('body')).get('Summary')
    return summary


def get_instance_count_for_account(account):
    """ Get EC2 instance count for a specific account.
    :param account: AWS account
    """
    regions = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']
    data = []
    instance_count = 0
    session = boto3.session.Session()  # create session for Thread Safety
    for region in regions:
        assume = rolesession.assume_crossact_audit_role(
            session, account['accountNum'], region)
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


def lambda_handler(*kwargs):
    """ BOVI(n)E instancecount endpoint lambda function. """
    print kwargs[0].get('account')
    function_name = kwargs[1].function_name
    account = kwargs[0].get('account')
    region = kwargs[0].get('region')
    results, run_time = ec2_count(function_name, account, region)
    body = dict(Summary=results, Time=run_time)
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response
