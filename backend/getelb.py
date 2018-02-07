
import datetime
from time import mktime

import boto3
from lib import rolesession
from lib.awsaccounts import AwsAccounts
import json

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))
        return json.JSONEncoder.default(self, obj)


def get_elb(account, elb, region):
    aws_accounts = AwsAccounts()
    if account.isdigit() and len(account) == 12:
        account = account
    else:
        alias = account
        account = aws_accounts.with_alias(alias)['accountNum']

    if not (account.isdigit() and len(account) == 12):
        return dict(Error='Account not found'), 404

    session = boto3.session.Session(region_name=region)
    assume = rolesession.assume_crossact_audit_role(session, account,
                                                    region)
    client = assume.client('elb')
    try:
        elb_info = client.describe_load_balancers(
            LoadBalancerNames=[elb])['LoadBalancerDescriptions'][0]
    except:
        return dict(Account=dict(accountNum=account),
                       LoadBalancer=dict(message='ELB not found')), 404

    elb_dns = elb_info['DNSName']
    # elb_listeners = elb_info['ListenerDescriptions']
    elb_subnets = elb_info['Subnets']
    elb_vpc = elb_info['VPCId']
    elb_instances = elb_info['Instances']
    elb_sg = elb_info['SecurityGroups']
    ec2 = assume.client('ec2')
    try:
        route_info = ec2.describe_route_tables(
            Filters=[dict(
                Name='association.subnet-id',
                Values=elb_subnets)])['RouteTables']
        gatewayid = None
        nat_gatewayid = None
        print(route_info)
        for route_table in route_info:
            routes = route_table['Routes']
            for route in routes:
                try:
                    if route['DestinationCidrBlock'] == '0.0.0.0/0':
                        try:
                            gatewayid = route['GatewayId']
                        except:
                            nat_gatewayid = route['NatGatewayId']
                except Exception:
                    pass
    except Exception as e:
        print(e)
        gatewayid = None
        nat_gatewayid = None
        route_info = ec2.describe_route_tables()['RouteTables'][0]
        # todo: This follow code is definitely wrong - check route_table
        for route_table in route_info:
            routes = route_info['Routes']
            for route in routes:
                try:
                    if route['DestinationCidrBlock'] == '0.0.0.0/0':
                        try:
                            gatewayid = route['GatewayId']
                        except:
                            nat_gatewayid = route['NatGatewayId']
                except Exception as e:
                    pass
    if gatewayid:
        if gatewayid.startswith("igw-"):
            internet_facing = True
        else:
            internet_facing = False
    else:
        gatewayid = nat_gatewayid
        internet_facing = False

    return dict(
        Account=dict(AccountNum=account),
        LoadBalancer=dict(
            ELBName=elb,
            DNSName=elb_dns,
            Subnets=elb_subnets,
            VpcId=elb_vpc,
            InternetFacing=internet_facing,
            SecurityGroups=elb_sg,
            Region=region),
        Routes=dict(GatewayId=gatewayid), Instances=elb_instances)

def lambda_handler(event,context):
    account = None
    instance = None
    region = None
    query_params = event.get('queryStringParameters')
    if query_params:    
        account = query_params.get('account')
        elb = query_params.get('elb')
        region = query_params.get('region')
        results = get_elb(account,elb,region)
        body = results
    else:
        body = {"Message":"Security Group not found."}
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response

if __name__ == "__main__":
    resp = lambda_handler(None,None)
    print resp