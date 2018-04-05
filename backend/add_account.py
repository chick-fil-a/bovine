
""" BOVI(n)E add account endpoint"""
import json

from lib.awsaccounts import AwsAccounts


def add_account(account_info):
    """ Add an acount to the AWS accounts table
    :param account_info: AWS account metadata - id, alias, owner, etc
    """
    if account_info['accountNum'].isdigit() and len(account_info['accountNum']) == 12:
        aws_accounts = AwsAccounts()
        return {"response": aws_accounts.add(account_info)}, 200
    return {"response:": "Incorrect account number given"}, 500


def lambda_handler(*kwargs):
    """ Lambda handler """
    body = kwargs[0].get('body')
    print body
    if body:
        resp, status_code = add_account(json.loads(body))
    else:
        resp = {"Message": "Account not added."}
        status_code = 500
    response = {
        "statusCode": status_code,
        "body": json.dumps(resp)
    }
    return response
