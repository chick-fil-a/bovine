
""" BOVI(n)E getelb endpoint """
import json

import boto3
from botocore.exceptions import ClientError

from lib import rolesession


def get_gateway_ids(session, elb_subnets):
    """ Get gateway ids for elb subnets
    :param session: AWS session
    :param elb_subnets: ELB subnets to look up route tables
    """
    ec2 = session.client('ec2')
    try:
        route_info = ec2.describe_route_tables(
            Filters=[dict(
                Name='association.subnet-id',
                Values=elb_subnets)])['RouteTables']
        gatewayid = None
        nat_gatewayid = None
        print route_info
        for route_table in route_info:
            routes = route_table['Routes']
            for route in routes:
                if route['DestinationCidrBlock'] == '0.0.0.0/0':
                    gatewayid = route.get('GatewayId')
                    nat_gatewayid = route.get('NatGatewayId')
    except ClientError as err:
        print err
        gatewayid = None
        nat_gatewayid = None
        route_info = ec2.describe_route_tables()['RouteTables'][0]
        # todo: This follow code is definitely wrong - check route_table
        for route_table in route_info:
            routes = route_info['Routes']
            for route in routes:
                if route.get('DestinationCidrBlock') == '0.0.0.0/0':
                    gatewayid = route.get('GatewayId')
                    nat_gatewayid = route.get('NatGatewayId')
    return gatewayid, nat_gatewayid


def get_elb(account, elb, region):
    """ Get elastic loadbalancer info. """
    # aws_accounts = AwsAccounts()

    session = boto3.session.Session(region_name=region)
    assume = rolesession.assume_crossact_audit_role(session, account,
                                                    region)
    client = assume.client('elb')
    try:
        elb_info = client.describe_load_balancers(
            LoadBalancerNames=[elb])['LoadBalancerDescriptions'][0]
    except ClientError:
        return dict(Account=dict(accountNum=account),
                    LoadBalancer=dict(message='ELB not found')), 404

    elb_dns = elb_info['DNSName']
    elb_subnets = elb_info['Subnets']
    elb_vpc = elb_info['VPCId']
    elb_instances = elb_info['Instances']
    elb_sg = elb_info['SecurityGroups']
    gatewayid, nat_gatewayid = get_gateway_ids(assume, elb_subnets)
    if gatewayid:
        internet_facing = bool(gatewayid.startswith("igw-"))
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


def lambda_handler(*kwargs):
    """ Lambda handler """
    account = None
    region = None
    query_params = kwargs[0].get('queryStringParameters')
    if query_params:
        account = query_params.get('account')
        elb = query_params.get('elb')
        region = query_params.get('region')
        results = get_elb(account, elb, region)
        body = results
    else:
        body = {"Message": "Security Group not found."}
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response
