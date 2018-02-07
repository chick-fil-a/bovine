from lib.awsaccounts import AwsAccounts
import json


def account_count():
    accounts = AwsAccounts()
    accounts_count = accounts.count()
    cred = dict(AccountsCount=accounts_count)
    final = dict(Summary=cred)
    print final
    return final

def lambda_handler(context,event):
    results = account_count()
    body = results
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response

if __name__ == "__main__":
    resp = lambda_handler(None,None)
    print resp