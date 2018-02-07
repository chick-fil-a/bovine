# Script to write csv records into dynamo db table.
# For help on prerequisites and running this script, read this blog.

from __future__ import print_function # Python 2/3 compatibility
from __future__ import division #Python 2/3 compatiblity for integer division
import argparse
import boto3
import csv
import time

# command line arguments
parser = argparse.ArgumentParser(description='Write CSV records to dynamo db table. CSV Header must map to dynamo table field names.')
parser.add_argument('csvFile', help='Path to csv file location')
parser.add_argument('table', help='Dynamo db table name')
parser.add_argument('writeRate', default=5, type=int, nargs='?', help='Number of records to write in table per second (default:5)')
parser.add_argument('delimiter', default='|', nargs='?', help='Delimiter for csv records (default=|)')
parser.add_argument('region', default='us-east-1', nargs='?', help='Dynamo db region name (default=us-west-2')
args = parser.parse_args()
print(args)

# dynamodb and table initialization
endpointUrl = "https://dynamodb." + args.region + ".amazonaws.com"
dynamodb = boto3.resource('dynamodb', region_name=args.region, endpoint_url=endpointUrl)
table = dynamodb.Table(args.table)

# write records to dynamo db
with open(args.csvFile) as csv_file:
    tokens = csv.reader(csv_file, delimiter=args.delimiter)
    # read first line in file which contains dynamo db field names
    header = tokens.next();
    # read second line in file which contains dynamo db field data types
    headerFormat = tokens.next();
    # rest of file contain new records
    for token in tokens:
       item = {}
       for i,val in enumerate(token):
         if val:
           key = header[i]
           if headerFormat[i]=='int':
             val = int(val)
           item[key] = val
       print(item)
       table.put_item(Item = item)

       time.sleep(1/args.writeRate) # to accomodate max write provisioned capacity for table