""" BOVI(n)E getdbs endpoint """
import datetime
from time import mktime
import json


import boto3
from lib import rolesession
from lib.awsaccounts import AwsAccounts


class MyEncoder(json.JSONEncoder):
    """ JSON encoder for datetime """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))
        return json.JSONEncoder.default(self, obj)


def get_dbs(account, region):
    """ Get all databases from AWS account. """
    rds_data = []
    aws_accounts = AwsAccounts()
    if not account:
        accounts = aws_accounts.all()
        session = boto3.session.Session()
        for cur_account in accounts:
            assume = rolesession.assume_crossact_audit_role(
                session,
                cur_account['accountNum'],
                region)
            if assume:
                db_instance_response = obtain_db_list(assume)
                rds_list = db_instance_response['DBInstances']

                for rds in rds_list:
                    rds_data.append(
                        dict(Region=region,
                             DBName=(rds.get('DBName')),
                             DBId=(rds['DBInstanceIdentifier']),
                             Engine=(rds['Engine']),
                             Version=(rds['EngineVersion']),
                             DBUser=(rds['MasterUsername']),
                             Endpoint=(rds.get('Endpoint')),
                             CreateDate=json.dumps(rds['InstanceCreateTime'],
                                                   cls=MyEncoder),
                             PublicAccess=(rds['PubliclyAccessible']),
                             AccountNum=cur_account['accountNum'],
                             AccountAlias=(cur_account.get('alias'))))
            else:
                pass
    elif account.isdigit() and len(account) == 12:
        account_number = account
        accounts_matching = aws_accounts.with_number(account_number)
        alias = accounts_matching['alias']
        session = boto3.session.Session()
        assume = rolesession.assume_crossact_audit_role(session,
                                                        account_number,
                                                        region)

        if assume:
            db_instance_response = obtain_db_list(assume)
            rds_list = db_instance_response['DBInstances']
            for rds in rds_list:
                rds_data.append(
                    dict(Region=region,
                         DBName=(rds.get('DBName')),
                         DBId=(rds['DBInstanceIdentifier']),
                         Engine=(rds['Engine']),
                         Version=(rds['EngineVersion']),
                         DBUser=(rds['MasterUsername']),
                         Endpoint=(rds.get('Endpoint')),
                         CreateDate=json.dumps(rds['InstanceCreateTime'],
                                               cls=MyEncoder),
                         PublicAccess=(rds['PubliclyAccessible']),
                         AccountNum=account_number,
                         AccountAlias=alias))
    else:
        return dict(Error="Account not found."), 404
    return dict(Databases=rds_data), 200


def obtain_db_list(session):
    """ List all RDS instances """
    client = session.client('rds')
    db_instance_response = client.describe_db_instances()
    return db_instance_response


def lambda_handler(*kwargs):
    """ Lambda handler """
    account = None
    region = None
    query_params = kwargs[0].get('queryStringParameters')
    if query_params:
        account = query_params.get('account')
        region = query_params.get('region')
    results = get_dbs(account, region)
    body, status = results
    response = {
        "statusCode": status,
        "body": json.dumps(body)
    }
    return response
