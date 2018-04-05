""" BOVI(n)E getinstances endpoint """
import json
import datetime
import time
from time import mktime
from multiprocessing.dummy import Pool
from dateutil.tz import tzutc
import dateutil.parser

import boto3

from lib import rolesession
from lib.awsaccounts import AwsAccounts


class MyEncoder(json.JSONEncoder):
    """ JSON encoder for datetime """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))
        return json.JSONEncoder.default(self, obj)


def lookup_ec2_to_cluster(session):
    """
    Takes a session argument and will return a map of instanceid to clusterarn
    :param session: boto 3 session for the account to query
    :return: map of ec2 instance id to cluster arn
    """
    ecs = session.client('ecs')
    result = dict()
    for cluster in ecs.list_clusters()['clusterArns']:
        instances = ecs.list_container_instances(
            cluster=cluster)['containerInstanceArns']
        if instances:
            ec2_to_cluster = [
                (x['ec2InstanceId'], cluster)
                for x in ecs.describe_container_instances(
                    cluster=cluster, containerInstances=instances)['containerInstances']
                ]
            result.update(ec2_to_cluster)
    return result


class LookupInstanceMembership(object):
    """ This class looks up EC2 to ECS membership """
    def __init__(self, session):
        self.ec2_to_ecs = lookup_ec2_to_cluster(session)
        self.session = session

    def lookup(self, instance, tags):
        """ Lookup EC2 instances service membership """
        in_ecs = self.ec2_to_ecs.get(instance)
        if in_ecs is not None:
            return "ECS"
        elif tags.get('elasticbeanstalk:environment-id') is not None:
            return "EBS"
        elif tags.get('aws:autoscaling:groupName') is not None:
            return "ASG"
        return None

    def get_session(self):
        """ Get AWS session """
        return self.session


class ImageAgeLookup(object):
    """
    This class looks up image age on demand but caches results
    """

    def __init__(self, session):
        self.image_age = dict()
        self.session = session

    def lookup(self, image_id):
        """ Lookup image age """
        # if image_id is None:
        #    self.image_age = 12
        # Check to see if its in the dictionary, if not, lookup
        if self.image_age.get(image_id) is None:
            ec2 = self.session.client('ec2')
            # print(image_id)
            image_info = ec2.describe_images(ImageIds=[image_id])['Images']
            if image_info:
                creation_date = dateutil.parser.parse(
                    image_info[0]['CreationDate'])
                create_d = datetime.datetime.now(tz=tzutc()) - creation_date
                age = create_d.days * 12 / 365
            else:
                age = 999  # Not sure what we do when the image doesn't look up properly
            self.image_age[image_id] = age
        return self.image_age.get(image_id)

    def get_session(self):
        """ Get AWS session """
        return self.session


def runtime(instance):
    """
    Basically difference from launch time to now in months
    """
    runtime_date = datetime.datetime.now(tz=tzutc()) - instance['LaunchTime']
    # print(d.days*12/365)
    return runtime_date.days * 12 / 365


def invoke_get_instances(account):
    """ Invoke lambda function to get instances for specific account
    :param account: AWS account
    """
    client = boto3.client('lambda')
    payload = {
        "queryStringParameters": {
            "account": account['accountNum'],
            "region": account['region']
        }
    }
    response = client.invoke(
        FunctionName=account['function_name'],
        Payload=json.dumps(payload),
        InvocationType='RequestResponse'
    )
    data = json.loads(response['Payload'].read())
    instances = json.loads(data.get('body')).get('Instances')
    return instances


def get_instances(function_name, account, region):
    """ Get all instances in a specific account.
    :param account: AWS account
    :param region: AWS region
    """
    if not region:
        region = 'us-east-1'
    start = time.time()
    instance_data = []
    aws_accounts = AwsAccounts()
    if not account:
        # running for all accounts, fan out Lambdas to make it faster
        account_list = aws_accounts.all(attr=['accountNum', 'alias'])
        pool = Pool(10)
        account_map = []
        for acc in account_list:
            acc['region'] = region
            acc['function_name'] = function_name
            account_map.append(acc)
        results = pool.map(invoke_get_instances, account_map)
        pool.close()
        pool.join()
        instance_data = [item for sublist in results for item in sublist]
        end = time.time()
    else:
        # running for a single account
        end = time.time()
        account_data = aws_accounts.with_number(account)
        instance_data = get_instances_for_account(account_data, region)
    return instance_data, (end - start)


def get_instances_for_account(account, region):
    """ Get instances for a specific account.
    :param account: AWS account
    """
    instance_data = []
    session = boto3.session.Session(region_name=region)
    assume = rolesession.assume_crossact_audit_role(
        session, account['accountNum'], region)
    if assume:
        age_lookup = ImageAgeLookup(assume)
        membership_lookup = LookupInstanceMembership(assume)
        ec2 = assume.client('ec2')
        instances = ec2.describe_instances().get('Reservations')
        if not instances:
            instances = []
        for res in instances:
            for instance in res['Instances']:
                tags = {x['Key']: x['Value']
                        for x in instance.get('Tags', [])}  # Extract tags as a dict
                if not tags:
                    tags = dict()
                instance_prof = instance.get('IamInstanceProfile')
                if instance_prof:
                    profile_name = instance_prof['Arn'].split('/')[-1]
                else:
                    profile_name = None

                instance_data.append(
                    dict(Name=tags.get('Name'),
                         CreateDate=json.dumps(
                             instance['LaunchTime'], cls=MyEncoder),
                         Region=region,
                         InstanceId=instance['InstanceId'],
                         State=instance['State']['Name'],
                         AccountNum=account['accountNum'],
                         IamInstanceProfile=profile_name,
                         ImageId=instance.get('ImageId'),
                         Membership=membership_lookup.lookup(
                             instance['InstanceId'], tags),
                         Runtime=runtime(instance),
                         ImageAge=age_lookup.lookup(instance.get('ImageId')),
                         AccountAlias=account.get('alias')))
    return instance_data


def lambda_handler(*kwargs):
    """ Lambda handler """
    function_name = kwargs[1].function_name
    account = None
    region = None
    query_params = kwargs[0].get('queryStringParameters')
    if query_params:
        account = query_params.get('account')
        if account == 'all':
            account = None
        region = query_params.get('region')

    if not region:
        region = 'us-east-1'

    results, run_time = get_instances(function_name, account, region)
    body = dict(Instances=results, Time=run_time)
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response
