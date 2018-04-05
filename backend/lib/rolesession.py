""" AWS IAM Role session wrapper. """
import os

import boto3
from botocore.exceptions import ClientError


ASSUME_ROLE = os.environ['ASSUME_ROLE']


def assume_crossact_audit_role(session, account_num, region, role=None):
    """ AssumeRole into account to audit

    :param session: Current Session
    :param account_num: Account number to assume into
    :param region: Region for the session
    :param role: Role to assume into
    :return: The resulting session from boto3
    """
    if not role:
        assume_role = ASSUME_ROLE
    else:
        assume_role = role

    assume_arn = 'arn:aws:iam::%s:role/%s' % (account_num, assume_role)
    client = session.client('sts')
    try:
        response = client.assume_role(RoleArn=assume_arn,
                                      RoleSessionName=assume_role)
    except ClientError:
        # raise Exception(
        #    "[X] Unable to assume role %s: %s." % (assume_role, e.message))
        # Not sure how to handle this. Needs to return None so the upstream
        # calls will continue gracefully.
        # Ex: when trying to call this function across all accounts and one
        # account is broken, the entire call fails
        return None
    creds = response['Credentials']
    access_key = creds['AccessKeyId']
    secret_key = creds['SecretAccessKey']
    sec_token = creds['SessionToken']
    session = boto3.session.Session(region_name=region,
                                    aws_access_key_id=access_key,
                                    aws_secret_access_key=secret_key,
                                    aws_session_token=sec_token)
    return session
