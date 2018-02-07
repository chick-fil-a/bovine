#!/bin/bash

# params: 
#   $1 = AWS credentials profile
#   $2 = stage (ie dev, test, prod)

PROFILE=$1
STAGE=$2

aws --profile $PROFILE s3 sync ../frontend s3://$STAGE-portal-html --exclude "*.py*" --exclude "*.sh" --exclude "text_data/*" --exclude ".idea/*" --exclude "*.swp" --exclude ".DS_Store"
cd ../backend;serverless deploy --stage $STAGE --profile $PROFILE

