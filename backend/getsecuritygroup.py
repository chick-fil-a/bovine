""" BOVI(n)E getsecuritygroup endpoint """
import json

import boto3
from botocore.exceptions import ClientError

from lib import rolesession


def get_instance_info(session, account, sg_id):
    """ Get EC2 instance info for a specific security group.
    :param session: AWS boto3 session
    :param account: AWS account
    :param sg_id: AWS Security group id
    """
    ec2 = session.client('ec2')
    instance_data = []
    instance_info = ec2.describe_instances(Filters=[dict(
        Name='instance.group-id',
        Values=[sg_id])])
    instances = instance_info['Reservations']
    for res in instances:
        instance_name = None
        for instance in res['Instances']:
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    instance_name = tag.get('Value', None)
                    break
            instance_data.append(dict(
                Name=instance_name,
                InstanceId=instance['InstanceId'],
                AccountNum=account))
    return instance_data


def format_outbound_rules(rules):
    """ Format security group egress rules.
    :param rules: Security group rules
    """
    formatted_rules = []
    for rule in rules:
        print rule
        from_port = rule.get('FromPort')
        to_port = rule.get('ToPort')
        if from_port and to_port:
            ports = str(from_port) + "-" + str(to_port)
        else:
            ports = 'all'

        if rule['IpProtocol'] == '-1':
            protocol = 'all'
        else:
            protocol = rule['IpProtocol']
        for ip_addr in rule['IpRanges']:
            destination = ip_addr['CidrIp']
            formatted_rules.append(
                {"Destination": destination, "Ports": ports,
                 "Protocol": protocol})
        prefixlist = rule.get('PrefixListIds')
        if prefixlist:
            for ip_prefix in prefixlist:
                destination = ip_prefix['GroupId']
                formatted_rules.append(
                    {"Destination": destination, "Ports": ports,
                     "Protocol": protocol})

        for sg_group in rule['UserIdGroupPairs']:
            destination = sg_group['GroupId']
            formatted_rules.append(
                {"Destination": destination, "Ports": ports,
                 "Protocol": protocol})
    print formatted_rules
    return formatted_rules


def format_inbound_rules(rules):
    """ Format security group ingress rules.
    :param rules: security group rules
    """
    formatted_rules = []
    for rule in rules:
        from_port = rule.get('FromPort')
        to_port = rule.get('ToPort')
        if from_port and to_port:
            ports = str(from_port) + "-" + str(to_port)
        else:
            ports = 'all'

        if rule['IpProtocol'] == '-1':
            protocol = 'all'
        else:
            protocol = rule['IpProtocol']
        for ip_addr in rule['IpRanges']:
            source = ip_addr['CidrIp']
            formatted_rules.append(
                {"Source": source, "Ports": ports, "Protocol": protocol})
        for ip_prefix in rule['PrefixListIds']:
            source = ip_prefix['GroupId']
            formatted_rules.append(
                {"Source": source, "Ports": ports, "Protocol": protocol})
        for sg_group in rule['UserIdGroupPairs']:
            source = sg_group['GroupId']
            formatted_rules.append(
                {"Source": source, "Ports": ports, "Protocol": protocol})
    return formatted_rules


def get_security_group(account, group, region):
    """ Get security group details.
    :param account: AWS account
    :param group: security group id
    :param region: AWS region
    """
    session = boto3.session.Session(region_name=region)
    assume = rolesession.assume_crossact_audit_role(
        session, account, region)
    if assume:
        ec2 = assume.client('ec2')
        try:
            sg_info = ec2.describe_security_groups(
                GroupIds=[group])['SecurityGroups'][0]
        except ClientError:
            print "Security group not found"
            return dict(Account=dict(accountNum=account),
                        Instance=dict(message='Security group not found'))
        instance_data = get_instance_info(assume, account, sg_info['GroupId'])
        client = assume.client('elb')
        elb_data = []

        for elb in client.describe_load_balancers()['LoadBalancerDescriptions']:
            for sec_group in elb['SecurityGroups']:
                if sec_group == sg_info['GroupId']:
                    elb_data.append(dict(
                        Name=elb['LoadBalancerName'],
                        AccountNum=account))

        return dict(
            Account=dict(accountNum=account),
            SecurityGroup=dict(
                GroupName=sg_info['GroupName'],
                GroupId=sg_info['GroupId'],
                Description=sg_info['Description'],
                Tags=sg_info.get('Tags', None),
                InboundRules=format_inbound_rules(sg_info['IpPermissions']),
                OutboundRules=format_outbound_rules(sg_info['IpPermissionsEgress']),
                VpcId=sg_info['VpcId'],
                Region=region),
            Instances=instance_data,
            ELB=elb_data)
    else:
        print '{"message":"Account not assumable"}'
        return dict(Account=dict(accountNum=account),
                    Message='Account not assumable')


def lambda_handler(*kwargs):
    """ Lambda handler function.
    :param event: Lambda event
    :param context: Lambda context
    """
    account = None
    region = None
    query_params = kwargs[0].get('queryStringParameters')
    if query_params:
        account = query_params.get('account')
        group = query_params.get('group')
        region = query_params.get('region')
        results = get_security_group(account, group, region)
        body = results
    else:
        body = {"Message": "Security Group not found."}
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response
