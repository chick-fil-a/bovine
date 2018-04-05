""" BOVI(n)E getpublicips endpoint """
from multiprocessing.dummy import Pool
import time
import json

import boto3

from lib import rolesession
from lib.awsaccounts import AwsAccounts


def get_public_ips(function_name, account, region='us-east-1'):
    """ Get all public IP addresses from an AWS account
    :param account: AWS account
    :param region: AWS region
    """
    if not region:
        region = 'us-east-1'
    start = time.time()
    aws_accounts = AwsAccounts()
    if not account:
        # running for all accounts, fan out Lambdas to make it faster
        account_list = aws_accounts.all(attr=['accountNum', 'alias'])
        pool = Pool(10)
        account_map = []
        for acc in account_list:
            acc['region'] = region
            acc['function_name'] = function_name
            account_map.append(acc)
        results = pool.map(invoke_get_public_ips, account_map)
        pool.close()
        pool.join()
        address_data = [item for sublist in results for item in sublist]
        end = time.time()
    else:
        # running for a single account
        end = time.time()
        account_data = aws_accounts.with_number(account)
        address_data = query_for_account(account_data, region)
    return address_data, (end - start)


def invoke_get_public_ips(account):
    """ Invoke lambda to get public IP addresses of
        a specific account.
    :param account: AWS account
    """
    client = boto3.client('lambda')
    payload = {
        "queryStringParameters": {
            "account": account['accountNum'],
            "region": account['region']
        }
    }
    response = client.invoke(
        FunctionName=account['function_name'],
        # Payload=json.dumps({"account":account,"region":account['region']}),
        Payload=json.dumps(payload),
        InvocationType='RequestResponse'
    )
    data = json.loads(response['Payload'].read())
    public_ips = json.loads(data.get('body')).get('Addresses')
    return public_ips


def query_for_account(account_rec, region):
    """  Performs the public ip query for the given account

    :param account: Account number to query
    :param session: Initial session
    :param region: Region to query
    :param ip_data: Initial list.  Appended to and returned
    :return: update ip_data list
    """
    ip_data = []
    session = boto3.session.Session(region_name=region)
    assume = rolesession.assume_crossact_audit_role(
        session, account_rec['accountNum'], region)
    if assume:
        for ip_addr in assume.client('ec2').describe_addresses()['Addresses']:
            ip_data.append(
                dict(PublicIP=(ip_addr.get('PublicIp')),
                     InstanceId=(ip_addr.get('InstanceId')),  # Prevents a crash
                     PrivateIP=(ip_addr.get('PrivateIpAddress')),
                     NetworkInterface=(ip_addr.get('NetworkInterfaceId')),
                     AccountNum=account_rec['accountNum'],
                     AccountAlias=(account_rec['alias'])))

        for instance in assume.resource('ec2').instances.filter():
            if instance.public_ip_address:
                ip_data.append(
                    dict(InstanceId=(instance.instance_id),
                         PublicIP=(instance.public_ip_address),
                         PrivateIP=(instance.private_ip_address),
                         AccountNum=account_rec['accountNum'],
                         AccountAlias=(account_rec['alias'])))
            else:
                pass
    return ip_data


def lambda_handler(*kwargs):
    """ Lambda handler """
    function_name = kwargs[1].function_name
    account = None
    region = None
    query_params = kwargs[0].get('queryStringParameters')
    if query_params:
        account = query_params.get('account')
        if account == 'all':
            account = None
        region = query_params.get('region', 'us-east-1')

    results, run_time = get_public_ips(function_name, account, region)
    body = dict(Addresses=results, Time=run_time)
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response
