""" BOVI(n)E number of accounts endpoint. """
import json

from lib.awsaccounts import AwsAccounts


def account_count():
    """ Get count of accounts """
    accounts = AwsAccounts()
    accounts_count = accounts.count()
    cred = dict(AccountsCount=accounts_count)
    final = dict(Summary=cred)
    print final
    return final


def lambda_handler(*kwargs):
    """ Lambda handler """
    print kwargs
    results = account_count()
    body = results
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response
