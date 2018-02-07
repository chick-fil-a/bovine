
import datetime
from time import mktime

import boto3
from lib import rolesession
import json

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))
        return json.JSONEncoder.default(self, obj)

def s3_acl_is_global(acl):
    global_uri = 'http://acs.amazonaws.com/groups/global/AllUsers'
    return acl['Grantee']['URI'] == global_uri

def get_s3_bucket(account, bucket, region='us-east-1'):
    if account.isdigit() and len(account) == 12:
        account = account
    else:
        return dict(Error='Account Not Found.'),404
    obj_data = []
    session = boto3.session.Session()
    assume = rolesession.assume_crossact_audit_role(
        session, account, region)
    if assume:
        s3 = assume.client('s3')

        s3_global = False
        try:
            s3_acls = s3.get_bucket_acl(Bucket=bucket)['Grants']
        except Exception as e:
            return dict(Error=e),500
        for acl in s3_acls:
            try:
                if s3_acl_is_global(acl):
                    s3_global = True
            except:
                pass
        try:
            s3_objects = s3.list_objects(Bucket=bucket)['Contents']
        except Exception as e:
            #Exception is likely a key error when the bucket has no contents.
            #There may be a better way to handle it.
            s3_objects = []
        if len(s3_objects) > 0:
            for obj in s3_objects:  # definately a bug,
                                    # if we get no buckets, this still happens
                s3_obj = s3.head_object(Bucket=bucket, Key=obj['Key'])
                obj_key = obj['Key']
                obj_last_modified = s3_obj['LastModified'].isoformat()
                obj_size = s3_obj['ContentLength']
                obj_enc = s3_obj.get('ServerSideEncryption')
                obj_storage = s3_obj.get('StorageClass')
                obj_data.append(dict(
                    Key=obj_key,
                    ModifiedDate=obj_last_modified,
                    Size=obj_size,
                    Encryption=obj_enc,
                    StorageType=obj_storage))
        else:
            print("Bucket has no contents")

        result = dict(
            Bucket=dict(
                Name=bucket,
                GlobalAccess=s3_global,
                AccountNum=account),
            Objects=obj_data)
    else:
        result = dict(Bucket=dict(Error='Unable to assume account'))
    return result,200

def lambda_handler(event,context):
    account = None
    bucket = None
    region = None
    query_params = event.get('queryStringParameters')
    if query_params:    
        account = query_params.get('account')
        bucket = query_params.get('bucket')
        region = query_params.get('region')
        results = get_s3_bucket(account,bucket,region)
        body,status = results
        #print body
    else:
        body = {"Message":"Bucket not found."}
    response = {
        "statusCode": status,
        "body": json.dumps(body)
    }
    return response

if __name__ == "__main__":
    resp = lambda_handler(None,None)
    print resp
