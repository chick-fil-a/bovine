
import datetime
from time import mktime
from multiprocessing.dummy import Pool
import time
import itertools
import boto3
import json

from lib import rolesession
from lib.awsaccounts import AwsAccounts


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))
        return json.JSONEncoder.default(self, obj)


def get_public_ips(account, region='us-east-1'):
    if not region:
        region = 'us-east-1'
    start = time.time()
    aws_accounts = AwsAccounts()
    ip_data = []
    #session = boto3.session.Session()
    if not account:
        # running for all accounts, fan out Lambdas to make it faster
        account_list = aws_accounts.all(attr=['accountNum','alias'])
        client = boto3.client('lambda')
        user_count = 0
        pool = Pool(10)
        account_map = []
        for account in account_list:
            account['region'] = region
            account_map.append(account)
        results = pool.map(invoke_get_public_ips, account_map)
        pool.close()
        pool.join()
        address_data = [item for sublist in results for item in sublist]
        end = time.time()
        return address_data,(end-start)
    else:
        # running for a single account
        end = time.time()
        account_data = aws_accounts.with_number(account)
        data = query_for_account(account_data,region)
        return data,(end-start)

def invoke_get_public_ips(account):
    #print "invoke_get_instances: %s" % account
    final_data = []
    client = boto3.client('lambda')
    payload = {
        "queryStringParameters":{
            "account": account['accountNum'],
            "region": account['region']
        }
    }
    response = client.invoke(
        FunctionName=function_name,
        #Payload=json.dumps({"account":account,"region":account['region']}),
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
        for ip in assume.client('ec2').describe_addresses()['Addresses']:
            ip_data.append(
                dict(PublicIP=(ip.get('PublicIp')),
                     InstanceId=(ip.get('InstanceId')),  # Prevents a crash
                     PrivateIP=(ip.get('PrivateIpAddress')),
                     NetworkInterface=(ip.get('NetworkInterfaceId')),
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

def lambda_handler(event,context):
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

    results,run_time = get_public_ips(account,region)
    body = dict(Addresses=results,Time=run_time)    
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response

if __name__ == "__main__":
    resp = lambda_handler(None,None)
    print resp