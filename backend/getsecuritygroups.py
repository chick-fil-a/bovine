
import boto3
from lib import rolesession
from lib.awsaccounts import AwsAccounts
import json

def get_security_groups(account, region='us-east-1'):
    sg_data = []

    aws_accounts = AwsAccounts()
    accounts = aws_accounts.all()
    session = boto3.session.Session(region_name=region)

    if not account:
        for acc in accounts:
            if acc['accountNum']:
                assume = rolesession.assume_crossact_audit_role(
                    session, acc['accountNum'], region)
                if assume:
                    ec2 = assume.client('ec2')
                    security_groups = ec2.describe_security_groups()[
                        'SecurityGroups']

                    for group in security_groups:
                        sg_name = None
                        try:
                            for tag in group['Tags']:
                                if tag['Key'] == 'Name':
                                    sg_name = tag['Value']
                        except:
                            sg_name = None

                        sg_data.append(
                            dict(Region=region,
                                 GroupName=sg_name,
                                 GroupId=(group['GroupId']),
                                 AccountNum=acc['accountNum'],
                                 AccountAlias=acc['alias']))
    elif account.isdigit() and len(account) == 12:
        assume = rolesession.assume_crossact_audit_role(session, account,
                                                        region)
        alias = aws_accounts.with_number(account)['alias']
        if assume:
            ec2 = assume.client('ec2')
            security_groups = ec2.describe_security_groups()['SecurityGroups']

            for group in security_groups:
                sg_name = None
                for tag in group['Tags']:
                    if tag['Key'] == 'Name':
                        sg_name = tag['Value']
                sg_id = group['GroupId']
                sg_data.append(dict(
                    GroupName=sg_name,
                    GroupId=sg_id,
                    AccountNum=account,
                    AccountAlias=alias))
    else:
        return(dict(Message='Account not found'),404)
    # print(sg_data)
    return dict(SecurityGroups=sg_data),200

def lambda_handler(event,context):
    account = None
    region = None
    query_params = event.get('queryStringParameters')
    if query_params:    
        account = query_params.get('account')
        region = query_params.get('region')
    results = get_security_groups(account,region)
    body,status = results
    response = {
        "statusCode": status,
        "body": json.dumps(body)
    }
    return response

if __name__ == "__main__":
    resp = lambda_handler(None,None)
    print resp