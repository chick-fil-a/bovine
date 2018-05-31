Creating a BOVI(n)E Config File
---------------------------------
BOVI(n)E leverages the serverless.com framework for deployment. Before you can deploy BOVI(n)E backend, you need to create a serverless config file. Below is an example config:
```json
 {
    "s3bucket":"example-bovine-html",
    "reportsBucket":"example-bovine-reports",
    "rulesBucket":"example-bovine-rules",
    "auditLambda":"example-bovine-audit-lambda",
    "lambdaRole":"example-bovine-lambda-audit-role",
    "lambdaAssumeRole":"example-bovine-lambda-assume-role",
    "lambdaPolicy":"example-bovine-lambda-audit-policy",
    "accountId":"123456789012",
    "domainName":"example.bovine.com",
    "region":"us-east-1",
    "authorizerArn":"arn:aws:cognito-idp:us-east-1:123456789012:userpool/us-east-1_1q2w3e4r",
    "authUrl":"https://bovine-example.auth.us-east-1.amazoncognito.com/login?response_type=token&client_id=123456789asdfv&redirect_uri=https://example.bovine.com/login"
}
```

* s3bucket = The S3 bucket you want to host your BOVI(n)E static content
* reportsBucket = The S3 bucket you want to store your audit reports
* rulesBucket = The S3 bucket you want to store your audit rules
* auditLambda = The lambda of your auditor function (See Audit guide)
* lambdaRole = The role of your BOVI(n)E backend functions
* lambdaAssumeRole = The role that BOVIN(e)E will assume into the target account
* lambdaPolicy = The IAM policy that is assigned to the BOVI(n)E lambdas
* accountId = Account ID of the BOVI(n)E account
* domainName = Custom domain name for the BOVI(n)E web app
* region = AWS default region
* authorizerArn = The Cognito pool Authorizer ARN
* authUrl = The Cognito OAUTH authentication URL
