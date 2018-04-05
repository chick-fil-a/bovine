""" BOVI(n)E getaccount endpoint. """
import json

from lib.awsaccounts import AwsAccounts


def get_account(account):
    """ Get AWS account metadata.
    :param account: AWS account
    """
    if account.isdigit() and len(account) == 12:
        mode = 'account'
    else:
        mode = 'alias'

    aws_accounts = AwsAccounts()
    if mode == 'account':
        response = aws_accounts.with_number(account)
        print "[D] alias/account: %s" % str(account)
        if response is None:
            return "", 404
        return extract_data_from_item(response)
    else:
        alias = account
        response = aws_accounts.with_alias(alias)
        if response is None:
            return "", 404
        return extract_data_from_item(response)


def extract_data_from_item(current_item):
    """ Extract data from dynamodb item.
    :param current_item: DynamoDB item
    """
    bastion = current_item.get('bastion', None)
    alias = current_item.get('alias', None)
    account_num = current_item.get('accountNum', None)
    admins = len(current_item.get('adgroup-Admin', []))
    admins = admins + len(current_item.get('adgroup-admin', []))
    email = current_item.get('email', None)
    owner = current_item.get('AccountOwner', None)
    risky_sg = len(current_item.get('RiskySecGroups', []))
    unused_sg = len(current_item.get('UnusedSecGroups', []))
    iam_users = len(current_item.get('IAMUsers', []))
    public_ips = len(current_item.get('PublicIP', []))

    score = -1
    data = dict(Account=dict(accountNum=account_num, owner=owner, alias=alias,
                             email=email,
                             iam=iam_users, publicIP=public_ips,
                             riskysg=risky_sg,
                             unusedsg=unused_sg, bastion=bastion,
                             risk_score=score, admins=admins))
    return data


def lambda_handler(*kwargs):
    """ Lambda handler """
    account = None
    query_params = kwargs[0].get('queryStringParameters')
    if query_params:
        account = query_params.get('account')
        results = get_account(account)
        body = results
    else:
        body = {"Message": "Account not found."}
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response
