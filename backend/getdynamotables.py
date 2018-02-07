
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
        for account in accounts:
            assume = rolesession.assume_crossact_audit_role(
                session,
                account['accountNum'],
                region)
            if assume:
                client = assume.client('dynamodb')
                dynamo_list = client.list_tables()['TableNames']

                for table in dynamo_list:
                    dynamo_data.append(dict(Region=region,
                                            TableName=table,
                                            AccountNum=account['accountNum'],
                                            AccountAlias=account['alias']))
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
            account = aws_accounts.with_number(account_number)
            client = assume.client('dynamodb')
            dynamo_list = client.list_tables()['TableNames']
            for table in dynamo_list:
                dynamo_data.append(dict(Region=region,
                                        TableName=table,
                                        AccountNum=account['accountNum'],
                                        AccountAlias=account['alias']))
        else:
            print("[D] Assume: %s" % assume)
            return {"Error": "Unable to assume role"}, 500
    else:
        return dict(Error='Account not found.'), 404
    return dict(Tables=dynamo_data),200

def lambda_handler(event,context):
    account = None
    region = None
    query_params = event.get('queryStringParameters')
    if query_params:    
        account = query_params.get('account')
        region = query_params.get('region')
    results = get_dynamo_tables(account,region)
    body,status = results
    response = {
        "statusCode": status,
        "body": json.dumps(body)
    }
    return response

if __name__ == "__main__":
    resp = lambda_handler(None,None)
    print resp

