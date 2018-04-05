
""" BOVI(n)E getinstance endpoint """
import datetime
from time import mktime
import json

import boto3
from botocore.exceptions import ClientError

from lib import rolesession


class MyEncoder(json.JSONEncoder):
    """ JSON encoder for datetime """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))
        return json.JSONEncoder.default(self, obj)


def get_elb_associations(session, instance):
    """ Get ELB associations for a particular EC2 instance
    :param session: AWS session
    :param instance: EC2 instance id
    """
    elb = session.client('elb')
    load_balancers = elb.describe_load_balancers()[
        'LoadBalancerDescriptions']
    instance_elb = []
    for balancer in load_balancers:
        for elb_instance in balancer['Instances']:
            if elb_instance['InstanceId'] == instance:
                instance_elb.append(balancer['LoadBalancerName'])
    return instance_elb


def get_instance_info(session, instance):
    """ Get EC2 instance info.
    :param session: AWS session
    :param instance: EC2 instance
    """
    ec2 = session.client('ec2')
    instance_info = None
    try:
        instance_description = ec2.describe_instances(
            InstanceIds=[instance])
        instance_info = instance_description['Reservations'][0]['Instances'][0]
    except ClientError as err:
        print "[X] Exception: %s" % err
    return instance_info


def get_instance(account, instance, region='us-east-1'):
    """ Get specific instance information.
    :param account: AWS account
    :param instance: AWS EC2 instance id
    :param region: AWS region
    """
    if account:
        session = boto3.session.Session(region_name=region)
        assume = rolesession.assume_crossact_audit_role(
            session, account, region)
        ec2 = assume.client('ec2')
        instance_info = get_instance_info(assume, instance)
        if not instance_info:
            return dict(
                Account=dict(accountNum=account),
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
            gateway_id = get_gateway_id(routes)
        except (ClientError, IndexError) as err:
            print "[X] No explicit route table found: %s" % err
            gateway_id = None

            data_vpcid = instance_info.get('VpcId')
            route_filter = [dict(Name='association.main', Values=['true'])]
            if data_vpcid:
                route_filter.append(dict(Name='vpc-id', Values=[data_vpcid]))

            route_table_description = ec2.describe_route_tables(
                Filters=route_filter)
            if route_table_description.get('RouteTables'):
                route_info = route_table_description['RouteTables'][0]
                route_tags = route_info['Tags']
                routes = route_info['Routes']
                gateway_id = get_gateway_id(routes)

        internet_facing = bool(gateway_id.startswith("igw-"))
        instance_elb = get_elb_associations(assume, instance)
        try:
            image_name = ec2.describe_images(
                ImageIds=[instance_info['ImageId']])['Images'][0]['Name']
        except (ClientError, IndexError):
            image_name = None

        try:
            net_acl = ec2.describe_network_acls(Filters=[
                dict(Name='association.subnet-id',
                     Values=[subnet_id])])['NetworkAcls'][0]['NetworkAclId']
        except ClientError:
            net_acl = None

        return dict(
            Account=dict(accountNum=account),
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
        print '{"message":"Account not found"}'
        return dict(Message='Account not found'), 404


def get_gateway_id(routes):
    """ Get route gateway id.
    :param routes: AWS route table
    """
    gateway_id = ""
    for route in routes:
        if route['DestinationCidrBlock'] == '0.0.0.0/0':
            gateway_id = route.get('GatewayId')
            if gateway_id is None:
                gateway_id = route.get('InstanceId')
                if gateway_id is None:
                    gateway_id = route.get('NatGatewayId')
                    if gateway_id is None:
                        print "[X] Error route_table"
    return gateway_id


def lambda_handler(*kwargs):
    """ Lambda handler """
    account = None
    instance = None
    region = None
    query_params = kwargs[0].get('queryStringParameters')
    if query_params:
        account = query_params.get('account')
        instance = query_params.get('instance')
        region = query_params.get('region')
        print account, instance, region
        results = get_instance(account, instance, region)
        body = results
    else:
        body = {"Message": "Instance not found."}
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response
