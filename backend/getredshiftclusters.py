
import datetime
from time import mktime

import boto3
from lib import rolesession
from lib.awsaccounts import AwsAccounts
from lib import mp_wrappers
import json

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))
        return json.JSONEncoder.default(self, obj)


def get_redshift_clusters(account, region):
    redshift_data = []
    aws_accounts = AwsAccounts()
    accounts = aws_accounts.all()

    if not account:
        session = boto3.session.Session()
        for account in accounts:
            alias = None
            assume = rolesession.assume_crossact_audit_role(
                session,
                account['accountNum'],
                region)

            if assume:
                client = assume.client('redshift')
                #redshift_list = client.describe_clusters()['Clusters']
                redshift_list = mp_wrappers.describe_clusters(client)['Clusters']
                try:
                    alias = account['alias']
                except:
                    pass
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
                             AccountNum=account['accountNum'],
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
            #redshift_list = client.describe_clusters()['Clusters']
            redshift_list = mp_wrappers.describe_clusters(client)['Clusters']
            try:
                alias = account['alias']
            except:
                pass
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
        return dict(Error='Account not found'),404
    return dict(Clusters=redshift_data),200

def lambda_handler(event,context):
    account = None
    region = None
    query_params = event.get('queryStringParameters')
    if query_params:    
        account = query_params.get('account')
        region = query_params.get('region')
    results = get_redshift_clusters(account,region)
    body = results
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response

if __name__ == "__main__":
    resp = lambda_handler(None,None)
    print resp
