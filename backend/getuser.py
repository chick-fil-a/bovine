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


def get_user(account, user):
    aws_accounts = AwsAccounts()
    if not(account.isdigit() and len(account) == 12):
        alias = account
        account = aws_accounts.with_alias(alias)

    if account:
        print("Account "+str(account))
        policies = []

        session = boto3.session.Session()
        assume = rolesession.assume_crossact_audit_role(
            session, account, 'us-east-1')
        iam = assume.client('iam')
        try:
            try:
                #user_info = iam.list_user_policies(UserName=user)[
                #    'PolicyNames']
                user_info = mp_wrappers.list_user_policies(iam, user)['PolicyNames']
            except Exception as e:
                print(e)
                final = dict(Account=dict(accountNum=account),
                    User=dict(Username=user),
                    Message='User not found'), 404
                return final

            for pol_name in user_info:
                policy = iam.get_user_policy(UserName=user,
                                             PolicyName=pol_name)
                policies.append(policy['PolicyDocument'])
                print(policies)
            #user_info = iam.list_attached_user_policies(UserName=user)[
             #   'AttachedPolicies']
            user_info = mp_wrappers.list_attached_user_policies(iam, user)['AttachedPolicies']
            for pol_name in user_info:
                policies.append({"ManagedPolicy": pol_name['PolicyName']})

            #create_date = iam.get_user(UserName=user)['User'][
            #    'CreateDate'].isoformat()

            create_date = mp_wrappers.get_user(iam, user)['User']['CreateDate'].isoformat()
            try:
                if user['PasswordLastUsed']:
                    password_set = True
                else:
                    password_set = False
            except:
                password_set = False
            access_keys = []
            access_key_info = iam.list_access_keys(UserName=user)[
                'AccessKeyMetadata']
            for access_key in access_key_info:
                last_used = iam.get_access_key_last_used(
                    AccessKeyId=access_key['AccessKeyId'])[
                    'AccessKeyLastUsed']
                try:
                    last_used_date = last_used['LastUsedDate'].isoformat()
                except:
                    last_used_date = None
                last_used_service = last_used['ServiceName']
                last_used_region = last_used['Region']
                access_keys.append(dict(
                    KeyId=access_key['AccessKeyId'],
                    Status=access_key['Status'],
                    CreateDate=access_key['CreateDate'].isoformat(),
                    LastUsed=last_used_date,
                    LastService=last_used_service,
                    LastRegion=last_used_region))
        except Exception as e:
            print("Exception: %s" % e)
            final = dict(Account=dict(accountNum=account),
                           Exception=dict(message=e))
            return final
        final = dict(Account=dict(accountNum=account),
            User=dict(
                Username=user,
                CreateDate=create_date,
                PasswordSet=password_set,
                Policies=policies),
            AccessKeys=access_keys)
        return final
    else:
        # print('{"message":"Account not found"}')
        return [dict(Message='Account not found'), ]

def lambda_handler(event,context):
    account = None
    query_params = event.get('queryStringParameters')
    if query_params:    
        account = query_params.get('account')
        user = query_params.get('user')
        results = get_user(account,user)
        body = results
    else:
        body = {"Message":"User not found."}
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response

if __name__ == "__main__":
    resp = lambda_handler(None,None)
    print resp