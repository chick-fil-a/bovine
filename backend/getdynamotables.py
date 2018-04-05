""" BOVI(n)E getdynamotables endpoint """
import json

import boto3
from lib import rolesession
from lib.awsaccounts import AwsAccounts


def get_dynamo_tables(account, region):
    """Provide an event that contains the following keys:
        -account: account to look in or all for all security groups
        -region: region to pull from
    """
    dynamo_data = []

    aws_accounts = AwsAccounts()
    if not account:
        accounts = aws_accounts.all()
        session = boto3.session.Session()
        for acc in accounts:
            assume = rolesession.assume_crossact_audit_role(
                session,
                acc['accountNum'],
                region)
            if assume:
                client = assume.client('dynamodb')
                dynamo_list = client.list_tables()['TableNames']
                for table in dynamo_list:
                    dynamo_data.append(dict(Region=region,
                                            TableName=table,
                                            AccountNum=acc['accountNum'],
                                            AccountAlias=acc['alias']))
            else:
                pass
    elif account.isdigit() and len(account) == 12:
        account_number = account
        session = boto3.session.Session()
        assume = rolesession.assume_crossact_audit_role(session,
                                                        account_number,
                                                        region)
        if assume:
            account = aws_accounts.with_number(account_number)
            client = assume.client('dynamodb')
            dynamo_list = client.list_tables()['TableNames']
            for table in dynamo_list:
                dynamo_data.append(dict(Region=region,
                                        TableName=table,
                                        AccountNum=account['accountNum'],
                                        AccountAlias=account['alias']))
        else:
            return {"Error": "Unable to assume role"}, 500
    else:
        return dict(Error='Account not found.'), 404
    return dict(Tables=dynamo_data), 200


def lambda_handler(*kwargs):
    """ Lambda handler """
    account = None
    region = None
    query_params = kwargs[0].get('queryStringParameters')
    if query_params:
        account = query_params.get('account')
        region = query_params.get('region')
    results = get_dynamo_tables(account, region)
    body, status = results
    response = {
        "statusCode": status,
        "body": json.dumps(body)
    }
    return response
