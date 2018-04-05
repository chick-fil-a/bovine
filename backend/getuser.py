"""Lambda function to gather IAM user information."""

import json

import boto3

from lib import rolesession
from lib.awsaccounts import AwsAccounts
from lib import mp_wrappers


def user_exists(client, user):
    """ Checks to see if a requested IAM user exists
        in a given account.
    :param client: Boto3 IAM client
    :param user: IAM username
    """
    try:
        if client.get_user(UserName=user):
            return True
    except client.exceptions.NoSuchEntityException:
        return False
    return False


def user_create_date(client, user):
    """ IAM user creation date."""
    try:
        create_date = mp_wrappers.get_user(client, user)['User'][
            'CreateDate'].isoformat()
    except AttributeError as err:
        print err
        create_date = None
    return create_date


def get_user_policies(client, user):
    """ Gather IAM user policy information"""
    policies = []
    # Create an assumed session and IAM client in single call
    for pol_name in mp_wrappers.list_user_policies(client, user)['PolicyNames']:
        policy = client.get_user_policy(UserName=user,
                                        PolicyName=pol_name)
        policies.append(policy['PolicyDocument'])
        print policies
    return policies


def get_user(account, user):
    """ Grab metadata about a particular AWS user in an AWS account.

    :param account: AWS account
    :param user: AWS user to get
    """
    aws_accounts = AwsAccounts()
    if not(account.isdigit() and len(account) == 12):
        account = aws_accounts.with_alias(account)

    if account:
        print "Account " + str(account)
        policies = []

        # Create an assumed session and IAM client in single call
        session = boto3.session.Session()
        iam = rolesession.assume_crossact_audit_role(
            session, account, 'us-east-1').client('iam')
        try:
            if not user_exists(iam, user):
                final_data = dict(Account=dict(accountNum=account),
                                  User=dict(Username=user),
                                  Message='User not found')
                return final_data

            user_info = mp_wrappers.list_attached_user_policies(iam, user)[
                'AttachedPolicies']
            for pol_name in user_info:
                policies.append({"ManagedPolicy": pol_name['PolicyName']})

            access_keys = []
            access_key_info = iam.list_access_keys(UserName=user)[
                'AccessKeyMetadata']
            for access_key in access_key_info:
                last_used = iam.get_access_key_last_used(
                    AccessKeyId=access_key['AccessKeyId'])[
                        'AccessKeyLastUsed']
                try:
                    last_used_date = last_used['LastUsedDate'].isoformat()
                except AttributeError:
                    last_used_date = None
                access_keys.append(dict(
                    KeyId=access_key['AccessKeyId'],
                    Status=access_key['Status'],
                    CreateDate=access_key['CreateDate'].isoformat(),
                    LastUsed=last_used_date,
                    LastService=last_used['ServiceName'],
                    LastRegion=last_used['Region']))
        except AttributeError as err:
            print "Exception: %s" % err
            final_data = dict(Account=dict(accountNum=account),
                              Exception=dict(message=str(err)))
            return final_data

        final_data = dict(Account=dict(accountNum=account),
                          User=dict(
                              Username=user,
                              CreateDate=user_create_date(iam, user),
                              PasswordSet=bool(mp_wrappers.get_user(
                                  iam, user)['User'].get('PasswordLastUsed')),
                              Policies=policies),
                          AccessKeys=access_keys)
        return final_data
    else:
        # print('{"message":"Account not found"}')
        return [dict(Message='Account not found'), ]


def lambda_handler(*kwargs):
    """ Lambda handler for getuser API.

    :param event: Lambda handler event data
    :param context: Lambda context data
    """
    account = None
    query_params = kwargs[0].get('queryStringParameters')
    if query_params:
        account = query_params.get('account')
        user = query_params.get('user')
        body = get_user(account, user)
        print body
    else:
        body = {"Message": "User not found."}

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response
