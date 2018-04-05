""" BOVI(n)E gets3bucket endpoint. """
import json

import boto3
from botocore.exceptions import ClientError

from lib import rolesession


def s3_acl_is_global(acl):
    """ Return bool if s3 has global allow ACL. """
    global_uri = 'http://acs.amazonaws.com/groups/global/AllUsers'
    grantee = acl.get('Grantee')
    return grantee.get('URI') == global_uri


def get_s3_bucket(account, bucket, region='us-east-1'):
    """ Get s3 bucket from specific account.
    :param account: AWS account
    :param bucket: S3 bucket
    :param region: AWS region
    """
    if account.isdigit() and len(account) == 12:
        account = account
    else:
        return dict(Error='Account Not Found.'), 404
    obj_data = []
    session = boto3.session.Session()
    assume = rolesession.assume_crossact_audit_role(
        session, account, region)
    if assume:
        s3_client = assume.client('s3')

        s3_global = False
        try:
            s3_acls = s3_client.get_bucket_acl(Bucket=bucket)['Grants']
        except ClientError as err:
            return dict(Error=err), 500
        for acl in s3_acls:
            s3_global = s3_acl_is_global(acl)
        s3_objects = s3_client.list_objects(Bucket=bucket).get('Contents')
        if s3_objects:
            for obj in s3_objects:  # definately a bug,
                                    # if we get no buckets, this still happens
                s3_obj = s3_client.head_object(Bucket=bucket, Key=obj['Key'])
                obj_data.append(dict(
                    Key=obj['Key'],
                    ModifiedDate=s3_obj['LastModified'].isoformat(),
                    Size=s3_obj['ContentLength'],
                    Encryption=s3_obj.get('ServerSideEncryption'),
                    StorageType=s3_obj.get('StorageClass')))
        else:
            print "Bucket has no contents"

        result = dict(
            Bucket=dict(
                Name=bucket,
                GlobalAccess=s3_global,
                AccountNum=account),
            Objects=obj_data)
    else:
        result = dict(Bucket=dict(Error='Unable to assume account'))
    return result, 200


def lambda_handler(*kwargs):
    """ Lambda handler function
    :param event: Lambda event
    :param context: Lambda context
    """
    account = None
    bucket = None
    region = None
    query_params = kwargs[0].get('queryStringParameters')
    if query_params:
        account = query_params.get('account')
        bucket = query_params.get('bucket')
        region = query_params.get('region')
        results = get_s3_bucket(account, bucket, region)
        body, status = results
    else:
        body = {"Message": "Bucket not found."}
    response = {
        "statusCode": status,
        "body": json.dumps(body)
    }
    return response
