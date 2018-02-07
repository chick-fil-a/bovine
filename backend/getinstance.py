
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


def get_instance(account, instance, region='us-east-1'):
    mode = 'account'
    if not (account.isdigit() and len(account) == 12):
        alias = account
        mode = 'alias'
    aws_accounts = AwsAccounts()

    if mode == 'alias':
        account_item = aws_accounts.with_alias(alias)
    elif mode == 'account':
        print("Account mode")
        account_item = aws_accounts.with_number(account)

    else:
        print("Error: Invalid option")
        raise Exception("Error: Invalid option")

    if account_item:
        session = boto3.session.Session(region_name=region)
        assume = rolesession.assume_crossact_audit_role(
            session, account_item['accountNum'], region)
        ec2 = assume.client('ec2')
        try:
            instance_description = ec2.describe_instances(
                InstanceIds=[instance])
            instance_info = \
                instance_description['Reservations'][0]['Instances'][0]
        except:
            print("Instance not found")
            return dict(
                Account=dict(accountNum=account_item['accountNum']),
                Instance=dict(message='Instance not found')), 404

        public_ip = instance_info.get('PublicIpAddress')
        subnet_id = instance_info.get('SubnetId')
        route_tags = None
        try:

            # todo: The following line bombs if their are no
            # explicit route tables.. Seems like a bug
            describe_route_table_filter = []
            if subnet_id:
                describe_route_table_filter.append(
                    dict(Name='association.subnet-id', Values=[subnet_id]))
            ec2_describe_route_tables = ec2.describe_route_tables(
                Filters=describe_route_table_filter)
            route_info = ec2_describe_route_tables['RouteTables'][0]
            route_tags = route_info['Tags']
            routes = route_info['Routes']
            gateway_id = get_geteway_id(routes)

        except Exception as e:
            print("[X] No explicit route table found: %s" % e)
            gateway_id = None

            data_vpcid = instance_info.get('VpcId')
            route_filter = [dict(Name='association.main', Values=['true'])]
            if (data_vpcid):
                route_filter.append(dict(Name='vpc-id', Values=[data_vpcid]))

            route_table_description = ec2.describe_route_tables(
                Filters=route_filter)
            if len(route_table_description['RouteTables']) > 0:
                route_info = route_table_description['RouteTables'][0]
                route_tags = route_info['Tags']
                routes = route_info['Routes']
                try:
                    gateway_id = get_geteway_id(routes)
                except:
                    gateway_id = ""

        if gateway_id.startswith("igw-"):
            internet_facing = True
        else:
            internet_facing = False

        elb = assume.client('elb')
        load_balancers = elb.describe_load_balancers()[
            'LoadBalancerDescriptions']
        instance_elb = []
        for balancer in load_balancers:
            for elb_instance in balancer['Instances']:
                if elb_instance['InstanceId'] == instance:
                    instance_elb.append(balancer['LoadBalancerName'])
        try:
            image_name = ec2.describe_images(
                ImageIds=[instance_info['ImageId']])['Images'][0]['Name']
        except:
            image_name = None

        try:
            net_acl = ec2.describe_network_acls(Filters=[
                dict(Name='association.subnet-id',
                     Values=[subnet_id])])['NetworkAcls'][0]['NetworkAclId']
        except:
            net_acl = None

        return dict(
            Account=dict(accountNum=account_item['accountNum']),
            Instance=dict(
                InstanceId=instance,
                ImageId=instance_info.get('ImageId'),
                ImageName=image_name,
                PublicDnsName=instance_info.get('PublicDnsName'),
                PublicIpAddress=public_ip,
                InternetFacing=internet_facing,
                ElasticLoadBalancer=instance_elb,
                PrivateIpAddress=instance_info.get('PrivateIpAddress'),
                InstanceType=instance_info['InstanceType'],
                SubnetId=subnet_id,
                SecurityGroups=instance_info.get('SecurityGroups'),
                Tags=(instance_info.get('Tags')),
                NetworkACL=net_acl,
                CreateDate=json.dumps(instance_info['LaunchTime'],
                                      cls=MyEncoder),
                Region=region),
            Routes=dict(
                GatewayId=gateway_id,
                Tags=route_tags))
    else:
        print('{"message":"Account not found"}')
        return dict(Message='Account not found'), 404


def get_geteway_id(routes):
    for route in routes:
        if route['DestinationCidrBlock'] == '0.0.0.0/0':
            gateway_id = route.get('GatewayId')
            if gateway_id is None:
                gateway_id = route.get('InstanceId')
                if gateway_id is None:
                    gateway_id = route.get('NatGatewayId')
                    if gateway_id is None:
                        print("[X] Error route_table")
    return gateway_id

def lambda_handler(event,context):
    account = None
    instance = None
    region = None
    query_params = event.get('queryStringParameters')
    if query_params:    
        account = query_params.get('account')
        instance = query_params.get('instance')
        region = query_params.get('region')
        results = get_instance(account,instance,region)
        body = results
    else:
        body = {"Message":"Instance not found."}
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response

if __name__ == "__main__":
    resp = lambda_handler(None,None)
    print resp