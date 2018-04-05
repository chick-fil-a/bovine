""" BOVI(n)E getredshiftclusters endpoint """
import json

import boto3
from lib import rolesession
from lib.awsaccounts import AwsAccounts
from lib import mp_wrappers


def get_redshift_clusters(account, region):
    """ Get all redshift clusters from all accounts. """
    redshift_data = []
    aws_accounts = AwsAccounts()
    accounts = aws_accounts.all()

    if not account:
        session = boto3.session.Session()
        for acc in accounts:
            alias = None
            assume = rolesession.assume_crossact_audit_role(
                session,
                acc['accountNum'],
                region)

            if assume:
                client = assume.client('redshift')
                redshift_list = mp_wrappers.describe_clusters(client)[
                    'Clusters']
                alias = acc.get('alias')

                for cluster in redshift_list:
                    redshift_data.append(
                        dict(Region=region,
                             ClusterId=(cluster['ClusterIdentifier']),
                             Username=(cluster['MasterUsername']),
                             DBName=(cluster['DBName']),
                             Endpoint=(cluster['Endpoint']),
                             PubliclyAccessible=(
                                 cluster['PubliclyAccessible']),
                             Encrypted=(cluster['Encrypted']),
                             AccountNum=acc['accountNum'],
                             AccountAlias=alias))
            else:
                pass
    elif account.isdigit() and len(account) == 12:
        session = boto3.session.Session()
        assume = rolesession.assume_crossact_audit_role(
            session,
            account,
            region)
        alias = None
        if assume:
            client = assume.client('redshift')
            redshift_list = mp_wrappers.describe_clusters(client)['Clusters']
            alias = account.get('alias')
            for cluster in redshift_list:
                redshift_data.append(
                    dict(Region=region,
                         ClusterId=(cluster['ClusterIdentifier']),
                         Username=(cluster['MasterUsername']),
                         DBName=(cluster['DBName']),
                         Endpoint=(cluster['Endpoint']),
                         PubliclyAccessible=(cluster['PubliclyAccessible']),
                         Encrypted=(cluster['Encrypted']),
                         AccountNum=account,
                         AccountAlias=alias))
    else:
        return dict(Error='Account not found'), 404
    return dict(Clusters=redshift_data), 200


def lambda_handler(*kwargs):
    """ Lambda handler """
    account = None
    region = None
    query_params = kwargs[0].get('queryStringParameters')
    if query_params:
        account = query_params.get('account')
        region = query_params.get('region')
    results = get_redshift_clusters(account, region)
    body = results
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response
