""" BOVI(n)E gets3buckets endpoint. """
import json
from multiprocessing.dummy import Pool
import time

import boto3
from botocore.exceptions import ClientError

from lib import rolesession
from lib.awsaccounts import AwsAccounts


def invoke_get_s3_buckets(account):
    """ Invoke lambda function to get S3 info for a
        specific account.
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
        Payload=json.dumps(payload),
        InvocationType='RequestResponse'
    )
    data = json.loads(response['Payload'].read())
    s3_buckets = json.loads(data.get('body')).get('Buckets')
    return s3_buckets


def get_s3_buckets(function_name, account, region):
    """ Get s3 buckets for all AWS accounts.
    :param account: AWS account
    :param region: AWS region
    """
    if not region:
        region = 'us-east-1'
    start = time.time()
    s3_data = []
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
        results = pool.map(invoke_get_s3_buckets, account_map)
        pool.close()
        pool.join()
        s3_data = [item for sublist in results for item in sublist]
        end = time.time()
    else:
        # running for a single account
        end = time.time()
        account_data = aws_accounts.with_number(account)
        s3_data = get_s3_buckets_for_account(account_data, region)
    return s3_data, (end - start)


def is_s3_bucket_global(session, bucket):
    """ Return bool for S3 bucket global accessibility
    :param session: AWS session
    :param bucket: S3 bucket
    """
    s3_client = session.client('s3')
    try:
        s3_acls = s3_client.get_bucket_acl(Bucket=bucket).get('Grants')
        if s3_acls:
            for acl in s3_acls:
                s3_global = s3_acl_is_global(acl)
    except (ClientError, TypeError) as err:
        print "[X] Exception: %s" % err
        s3_global = False
    return s3_global


def get_s3_buckets_for_account(account, region='us-east-1'):
    """ Get S3 buckets for a specific account.
    :param account: AWS account
    :param region: AWS region
    """
    session = boto3.session.Session()  # create session for Thread Safety
    assume = rolesession.assume_crossact_audit_role(
        session, account['accountNum'], region)
    s3_data = []
    if assume:
        s3_client = assume.client('s3')
        s3_info = s3_client.list_buckets().get('Buckets')
        if s3_info:
            for bucket in s3_info:
                s3_global = is_s3_bucket_global(assume, bucket)
                s3_data.append(
                    dict(BucketName=bucket['Name'],
                         AccountNum=account['accountNum'],
                         AccountAlias=account.get('alias'),
                         GlobalAccess=s3_global))
    return s3_data


def s3_acl_is_global(acl):
    """ Return bool if S3 has global ACL.
    :param acl: S3 ACL
    """
    global_uri = 'http://acs.amazonaws.com/groups/global/AllUsers'
    grantee = acl.get('Grantee')
    if grantee:
        return grantee.get('URI') == global_uri
    else:
        return False


def lambda_handler(*kwargs):
    """ AWS Lambda handler function.
    :param event: Lambda event
    :param context: Lambda context
    """
    function_name = kwargs[1].function_name
    account = None
    region = None
    query_params = kwargs[0].get('queryStringParameters')
    if query_params:
        account = query_params.get('account')
        if account == 'all':
            account = None
        region = query_params.get('region')
    if not region:
        region = 'us-east-1'

    results, run_time = get_s3_buckets(function_name, account, region)
    body = dict(Buckets=results, Time=run_time)
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response
