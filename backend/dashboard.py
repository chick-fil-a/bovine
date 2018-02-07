
import time
from multiprocessing.dummy import Pool

import boto3
from lib import rolesession
from lib.awsaccounts import AwsAccounts
import json
import os

ASSUME_ROLE = os.environ['ASSUME_ROLE']

def get_account_stats(account_rec):
    session = boto3.session.Session()
    account = account_rec['accountNum']
    assume = rolesession.assume_crossact_audit_role(
        session, account, 'us-east-1', ASSUME_ROLE)
    instance_count = 0
    sg_count = 0
    user_count = 0
    elb_count = 0
    if assume:
        ec2 = assume.client('ec2')
        instances = ec2.describe_instances()['Reservations']
        for res in instances:
            instance_count += len(res['Instances'])
        sg_count += len(
            ec2.describe_security_groups()['SecurityGroups'])
        iam = assume.client('iam')
        user_count += len(iam.list_users()['Users'])
        elb = assume.client('elb')
        elb_count += len(elb.describe_load_balancers()[
                             'LoadBalancerDescriptions'])
    return dict(
        InstanceCount=instance_count,
        UserCount=user_count,
        SecurityGroupCount=sg_count,
        ELBCount=elb_count)


def dashboard(role=None):
    start = time.time()
    instance_count = 0
    user_count = 0
    sg_count = 0
    elb_count = 0

    aws_accounts = AwsAccounts()
    accounts = aws_accounts.all()

    pool = Pool(10)
    results = pool.map(get_account_stats, accounts)
    pool.close()
    pool.join()
    for x in results:
        instance_count += x['InstanceCount']
        user_count += x['UserCount']
        sg_count += x['SecurityGroupCount']
        elb_count += x['ELBCount']

    end = time.time()
    result = dict(
        Time=(end - start),
        Summary=dict(
            AccountsCount=len(accounts),
            InstanceCount=instance_count,
            UserCount=user_count,
            SecurityGroupCount=sg_count,
            ELBCount=elb_count))

    return result

def lambda_handler(context,event):
    results = dashboard()
    body = results['Summary']
    time = results['Time']
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    print "Time to complete: %s" % str(time)
    return response

if __name__ == "__main__":
    resp = lambda_handler(None,None)
    print resp
