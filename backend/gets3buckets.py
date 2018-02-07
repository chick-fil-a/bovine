import json
import datetime
from time import mktime
from dateutil.tz import tzutc
import dateutil.parser
from multiprocessing.dummy import Pool
import time
import itertools

import boto3
from lib import rolesession
from lib.awsaccounts import AwsAccounts


class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))
        return json.JSONEncoder.default(self, obj)


def invoke_get_s3_buckets(account):
    final_data = []
    client = boto3.client('lambda')
    payload = {
        "queryStringParameters": {
            "account": account['accountNum'],
            "region": account['region']
        }
    }
    response = client.invoke(
        FunctionName=function_name,
        Payload=json.dumps(payload),
        InvocationType='RequestResponse'
    )
    data = json.loads(response['Payload'].read())
    s3_buckets = json.loads(data.get('body')).get('Buckets')
    return s3_buckets


def get_s3_buckets(account, region):
    if not region:
        region = 'us-east-1'
    start = time.time()
    s3_data = []
    aws_accounts = AwsAccounts()
    if not account:
        # running for all accounts, fan out Lambdas to make it faster
        account_list = aws_accounts.all(attr=['accountNum', 'alias'])
        client = boto3.client('lambda')
        pool = Pool(10)
        account_map = []
        for account in account_list:
            account['region'] = region
            account_map.append(account)
        results = pool.map(invoke_get_s3_buckets, account_map)
        pool.close()
        pool.join()
        s3_data = [item for sublist in results for item in sublist]
        end = time.time()
        return s3_data, (end - start)
    else:
        # running for a single account
        end = time.time()
        account_data = aws_accounts.with_number(account)
        data = get_s3_buckets_for_account(account_data, region)
        return data, (end - start)


def get_s3_buckets_for_account(account, region='us-east-1'):
    session = boto3.session.Session()  # create session for Thread Safety
    assume = rolesession.assume_crossact_audit_role(
        session, account['accountNum'], region)
    s3_data = []
    if assume:
        s3 = assume.client('s3')
        s3_info = s3.list_buckets()['Buckets']
        for bucket in s3_info:
            s3_global = False
            try:
                s3_acls = s3.get_bucket_acl(Bucket=bucket)['Grants']
                for acl in s3_acls:
                    try:
                        s3_global = s3_acl_is_global(acl)
                    except:
                        pass
            except Exception, e:
                print "[X] Exception: %s" % e
                pass
            s3_data.append(
                dict(BucketName=bucket['Name'],
                     AccountNum=account['accountNum'],
                     AccountAlias=account.get('alias'),
                     GlobalAccess=s3_global))
    else:
        return dict(Error='Account not found.'), 404
    return s3_data


def s3_acl_is_global(acl):
    global_uri = 'http://acs.amazonaws.com/groups/global/AllUsers'
    return acl['Grantee']['URI'] == global_uri


def lambda_handler(event, context):
    global function_name
    function_name = context.function_name
    account = None
    region = None
    query_params = event.get('queryStringParameters')
    if query_params:
        account = query_params.get('account')
        if account == 'all':
            account = None
        region = query_params.get('region')
    if not region:
        region = 'us-east-1'

    results, run_time = get_s3_buckets(account, region)
    body = dict(Buckets=results, Time=run_time)
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response

if __name__ == "__main__":
    resp = lambda_handler(None, None)
    print resp
