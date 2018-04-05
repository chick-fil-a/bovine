""" BOVI(n)E getelbs endpoint """
import json

import boto3
from lib import rolesession
from lib.awsaccounts import AwsAccounts


def get_elbs(account, region):
    """ Get elastic load balancers """
    elb_data = []
    aws_accounts = AwsAccounts()

    if not account:
        session = boto3.session.Session(region_name=region)
        for account_rec in aws_accounts.all():
            elb_data.extend(
                query_elbs_for_account(account_rec, region, session))
    elif account.isdigit() and len(account) == 12:
        session = boto3.session.Session()
        aws_account = aws_accounts.with_number(account)
        if aws_account:
            elb_data.append(
                query_elbs_for_account(
                    aws_account, region, session))
        else:
            return dict(Message="Account not found"), 404

    # print(elb_data)
    return dict(LoadBalancers=elb_data), 200


def query_elbs_for_account(account, region, session):
    """ Get elastic load balancers from a specific account """
    elb_list = []
    assume = rolesession.assume_crossact_audit_role(
        session,
        account['accountNum'],
        region)
    if assume:
        client = assume.client('elb')
        elbs = client.describe_load_balancers()[
            'LoadBalancerDescriptions']

        for elb in elbs:
            elb_name = elb['LoadBalancerName']
            elb_dns = elb['DNSName']
            elb_list.append(dict(Region=region,
                                 ELBName=elb_name,
                                 DNSName=elb_dns,
                                 AccountNum=account['accountNum'],
                                 AccountAlias=account['alias']))
    return elb_list


def lambda_handler(*kwargs):
    """ Lambda handler """
    account = None
    region = None
    query_params = kwargs[0].get('queryStringParameters')
    if query_params:
        account = query_params.get('account')
        region = query_params.get('region')
    results = get_elbs(account, region)
    body, status = results
    response = {
        "statusCode": status,
        "body": json.dumps(body)
    }
    return response
