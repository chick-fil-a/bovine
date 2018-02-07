
from lib.awsaccounts import AwsAccounts
import json
import os
import sys

def add_account(account_info):
    if account_info['accountNum'].isdigit() and len(account_info['accountNum']) == 12:
        aws_accounts = AwsAccounts()
        return {"response":aws_accounts.add(account_info)},200
    else:
        return {"response:":"Incorrect account number given"},500

def lambda_handler(event,context):
    account = None
    body = event.get('body')
    print body
    if body:
        resp,status_code = add_account(json.loads(body))
    else:
        resp = {"Message":"Account not added."}
        status_code = 500
    response = {
        "statusCode": status_code,
        "body": json.dumps(resp)
    }
    return response

if __name__ == "__main__":
    event = json.loads(sys.argv[1])
    resp = lambda_handler(event,None)
    print resp
