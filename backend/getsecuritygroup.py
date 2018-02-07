
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


def format_outbound_rules(rules):
    formatted_rules = []
    for rule in rules:
        print(rule)
        try:
            from_port = rule['FromPort']
            to_port = rule['ToPort']
            ports = str(from_port) + "-" + str(to_port)
        except Exception as e:
            print("[X] Rule error: %s" % e)
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
        try:
            for ip_prefix in rule['PrefixListIds']:
                destination = ip_prefix['GroupId']
                formatted_rules.append(
                    {"Destination": destination, "Ports": ports,
                    "Protocol": protocol})
        except Exception as e:
            print("Key Not Found: {}".format(str(e)))
        for sg_group in rule['UserIdGroupPairs']:
            destination = sg_group['GroupId']
            formatted_rules.append(
                {"Destination": destination, "Ports": ports,
                 "Protocol": protocol})
    print(formatted_rules)
    return formatted_rules


def format_inbound_rules(rules):
    formatted_rules = []
    for rule in rules:
        try:
            from_port = rule['FromPort']
            to_port = rule['ToPort']
            ports = str(from_port) + "-" + str(to_port)
        except:
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
    if account.isdigit() and len(account) == 12:
        account = account
        mode = 'account'
    else:
        alias = account
        mode = 'alias'

    aws_accounts = AwsAccounts()
    #This should have error handling for cases when the
    #alias/account does not exist.
    if mode == 'alias':
        account = aws_accounts.by_alias(alias)['accountNum']
    elif mode == 'account':
        print("Account mode")

    else:
        print('Error: Invalid option')
        raise Exception('Error: Invalid option')

    if account:
        session = boto3.session.Session(region_name=region)
        assume = rolesession.assume_crossact_audit_role(session, account,
                                                        region)

        ec2 = assume.client('ec2')
        try:
            sg_info = ec2.describe_security_groups(
                GroupIds=[group])['SecurityGroups'][0]
        except Exception as e:
            print("Security group not found")
            return dict(
                Account=dict(
                    accountNum=account),
                Instance=dict(message='Security group not found'))

        print(sg_info)
        group_name = sg_info['GroupName']
        group_id = sg_info['GroupId']
        group_desc = sg_info['Description']
        group_tags = sg_info.get('Tags', None)

        group_ingress = format_inbound_rules(sg_info['IpPermissions'])
        group_egress = format_outbound_rules(sg_info['IpPermissionsEgress'])
        group_vpc = sg_info['VpcId']
        instance_data = []
        instance_info = ec2.describe_instances(Filters=[dict(
            Name='instance.group-id',
            Values=[group_id])])
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

        client = assume.client('elb')
        elb_data = []
        elb_info = client.describe_load_balancers()[
            'LoadBalancerDescriptions']
        for elb in elb_info:
            for sg in elb['SecurityGroups']:
                if sg == group_id:
                    elb_data.append(dict(
                        Name=elb['LoadBalancerName'],
                        AccountNum=account))

        return dict(
            Account=dict(accountNum=account),
            SecurityGroup=dict(
                GroupName=group_name,
                GroupId=group_id,
                Description=group_desc,
                Tags=group_tags,
                InboundRules=group_ingress,
                OutboundRules=group_egress,
                VpcId=group_vpc,
                Region=region),
            Instances=instance_data,
            ELB=elb_data)
    else:
        print('{"message":"Account not found"}')
        return [dict(Message='Account not found'), ]

def lambda_handler(event,context):
    account = None
    instance = None
    region = None
    query_params = event.get('queryStringParameters')
    if query_params:    
        account = query_params.get('account')
        group = query_params.get('group')
        region = query_params.get('region')
        results = get_security_group(account,group,region)
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