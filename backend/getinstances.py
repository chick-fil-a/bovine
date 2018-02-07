
import boto3
import json
import datetime
from time import mktime
from dateutil.tz import tzutc
import dateutil.parser
from multiprocessing.dummy import Pool
import time
import itertools

from lib import rolesession
from lib.awsaccounts import AwsAccounts


class MyEncoder(json.JSONEncoder):
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
        instances = ecs.list_container_instances(cluster=cluster)['containerInstanceArns']
        if instances:
            ec2_to_cluster = [(x['ec2InstanceId'], cluster) for x in ecs.describe_container_instances(
                cluster=cluster, containerInstances=instances)['containerInstances']]
            result.update(ec2_to_cluster)
    return result


class LookupInstanceMembership:
    def __init__(self, session):
        self.ec2_to_ecs = lookup_ec2_to_cluster(session)

    def lookup(self, instance, tags):
        in_ecs = self.ec2_to_ecs.get(instance)
        if in_ecs is not None:
            return "ECS"
        elif tags.get('elasticbeanstalk:environment-id') is not None:
            return "EBS"
        elif tags.get('aws:autoscaling:groupName') is not None:
            return "ASG"
        return None


class ImageAgeLookup:
    """
    This class looks up image age on demand but caches results
    """
    def __init__(self, session):
        self.image_age = dict()
        self.session = session

    def lookup(self, image_id):
        if image_id is None:
            return 12
        # Check to see if its in the dictionary, if not, lookup
        if self.image_age.get(image_id) is None:
            ec2 = self.session.client('ec2')
            #print(image_id)
            image_info = ec2.describe_images(ImageIds=[image_id])['Images']
            if image_info:
                creation_date = dateutil.parser.parse(image_info[0]['CreationDate'])
                d = datetime.datetime.now(tz=tzutc()) - creation_date
                age = d.days * 12 / 365
            else:
                age = 999  #Not sure what we do when the image doesn't look up properly
            self.image_age[image_id] = age
        else:
            return self.image_age.get(image_id)


def runtime(instance):
    """
    Basically difference from launch time to now in months
    """
    d = datetime.datetime.now(tz=tzutc()) - instance['LaunchTime']
    #print(d.days*12/365)
    return d.days*12/365

def invoke_get_instances(account):
    #print "invoke_get_instances: %s" % account
    final_data = []
    client = boto3.client('lambda')
    payload = {
        "queryStringParameters":{
            "account": account['accountNum'],
            "region": account['region']
        }
    }
    response = client.invoke(
        FunctionName=function_name,
        #Payload=json.dumps({"account":account,"region":account['region']}),
        Payload=json.dumps(payload),
        InvocationType='RequestResponse'
    )
    data = json.loads(response['Payload'].read())
    instances = json.loads(data.get('body')).get('Instances')
    return instances

def get_instances(account,region):
    if not region:
        region = 'us-east-1'
    start = time.time()
    instance_data = []
    aws_accounts = AwsAccounts()
    if not account:
        # running for all accounts, fan out Lambdas to make it faster
        account_list = aws_accounts.all(attr=['accountNum','alias'])
        client = boto3.client('lambda')
        user_count = 0
        pool = Pool(10)
        account_map = []
        for account in account_list:
            account['region'] = region
            account_map.append(account)
        results = pool.map(invoke_get_instances, account_map)
        pool.close()
        pool.join()
        instance_data = [item for sublist in results for item in sublist]
        end = time.time()
        return instance_data,(end-start)
    else:
        # running for a single account
        end = time.time()
        account_data = aws_accounts.with_number(account)
        data = get_instances_for_account(account_data,region)
        return data,(end-start)

def get_instances_for_account(account,region):
    instance_data = []
    session = boto3.session.Session(region_name=region)
    try:
        assume = rolesession.assume_crossact_audit_role(
                    session, account['accountNum'], region)
    except Exception,e:
        assume = None
        print "Exception: %e" % e
    if assume:
        age_lookup = ImageAgeLookup(assume)
        membership_lookup = LookupInstanceMembership(assume)
        ec2 = assume.client('ec2')
        try:
            instances = ec2.describe_instances()['Reservations']
        except:
            instances = []
        for res in instances:
            for instance in res['Instances']:
                try:
                    tags = {x['Key']: x['Value'] for x in instance['Tags']}  # Extract tags as a dict
                except:
                    tags = dict()
                try:
                    profile_name = instance['IamInstanceProfile']['Arn'].split('/')[-1]
                except:
                    profile_name = None
                name = tags.get('Name')

                instance_data.append(
                    dict(Name=tags.get('Name'),
                            CreateDate=json.dumps(instance['LaunchTime'], cls=MyEncoder),
                            Region=region,
                            InstanceId=instance['InstanceId'],
                            State=instance['State']['Name'],
                            AccountNum=account['accountNum'],
                            IamInstanceProfile=profile_name,
                            ImageId=instance.get('ImageId'),
                            Membership=membership_lookup.lookup(instance['InstanceId'], tags),
                            Runtime=runtime(instance),
                            ImageAge=age_lookup.lookup(instance.get('ImageId')),
                            AccountAlias=account.get('alias')))
    return instance_data

def lambda_handler(event,context):
    global function_name
    function_name = context.function_name
    account = None
    region = None
    query_params = event.get('queryStringParameters')
    if query_params:    
        account = query_params.get('account')
        if account == 'all':
            account = None
        region = query_params.get('region')
    
    if not region:
        region = 'us-east-1'

    results,run_time = get_instances(account,region)
    body = dict(Instances=results,Time=run_time)
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response

if __name__ == "__main__":
    resp = lambda_handler(None,None)
    print resp
