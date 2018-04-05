""" BOVI(n)E getsecuritygroups endpoint."""
import json

import boto3

from lib import rolesession
from lib.awsaccounts import AwsAccounts


def get_security_group_name(security_group):
    """ Get Name tag of security group
    :param security_group: AWS security group object
    """
    sg_name = None
    tags = security_group.get('Tags')
    if tags:
        for tag in tags:
            if tag.get('Key') == 'Name':
                sg_name = tag['Value']
    return sg_name


def get_security_groups(account, region='us-east-1'):
    """ Get security groups in all accounts.
    :param account: AWS account
    :param region: AWS region
    """
    sg_data = []

    aws_accounts = AwsAccounts()
    accounts = aws_accounts.all()
    session = boto3.session.Session(region_name=region)

    if not account:
        for acc in accounts:
            assume = rolesession.assume_crossact_audit_role(
                session, acc['accountNum'], region)
            if assume:
                ec2 = assume.client('ec2')
                security_groups = ec2.describe_security_groups()[
                    'SecurityGroups']

                for group in security_groups:
                    sg_name = get_security_group_name(group)
                    sg_data.append(
                        dict(Region=region,
                             GroupName=sg_name,
                             GroupId=(group['GroupId']),
                             AccountNum=acc['accountNum'],
                             AccountAlias=acc['alias']))
    elif account.isdigit() and len(account) == 12:
        assume = rolesession.assume_crossact_audit_role(session, account,
                                                        region)
        alias = aws_accounts.with_number(account)['alias']
        if assume:
            ec2 = assume.client('ec2')
            security_groups = ec2.describe_security_groups()['SecurityGroups']

            for group in security_groups:
                sg_name = None
                for tag in group['Tags']:
                    if tag['Key'] == 'Name':
                        sg_name = tag['Value']
                sg_id = group['GroupId']
                sg_data.append(dict(
                    GroupName=sg_name,
                    GroupId=sg_id,
                    AccountNum=account,
                    AccountAlias=alias))
    else:
        return(dict(Message='Account not found'), 404)
    return dict(SecurityGroups=sg_data), 200


def lambda_handler(*kwargs):
    """ BOVI(n)E getsecuritygroups lambda handler.
    :param event: Lambda event
    :param context: Lambda context
    """
    account = None
    region = None
    query_params = kwargs[0].get('queryStringParameters')
    if query_params:
        account = query_params.get('account')
        region = query_params.get('region')
    results = get_security_groups(account, region)
    body, status = results
    response = {
        "statusCode": status,
        "body": json.dumps(body)
    }
    return response
