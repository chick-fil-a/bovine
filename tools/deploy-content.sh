# params: 
#   $1 = AWS credentials profile
#   $2 = s3 bucket 
aws --profile $1 s3 sync ../frontend s3://$2 --exclude "*.py*" --exclude "*.sh" --exclude "text_data/*" --exclude ".idea/*" --exclude "*.swp" --exclude ".DS_Store"


