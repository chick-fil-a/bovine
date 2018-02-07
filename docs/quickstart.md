Quick Start Guide
=================

IAM Permissions
---------------
In order to audit other accounts, an IAM role needs to be created with a cross-account trust from the BOVI(n)E account. 
-   [Setup Audit Role](setup_audit_role.md)


Database
--------
A DynamoDB table for account metadata.
-   [Dynamo Setup](setup_dynamodb.md)


User Setup
----------
Cognito user pools for user management.
-   [Cognito Setup](setup_cognito.md)

Custom Domain Name
------------------
This is optional. Custom domain name to be used instead of having to use the ugly API Gateway URL.
-   [Custom Domain Name setup](setup_custom_domain.md)


Serverless Config
-----------------
The Serverless Framework is used to control deployments and abstract away Cloudformation complexities.
-   [Serverless Config Example](setup_serverless_config.md)


Deploy API Stack
----------------
### Prerequisites

BOVI(n)E leverages the Serverless Framework found at [Serverless](http://www.serverless.com).

Install the Serverless Framework:
> npm install serverless -g

Prior to calling the deployment scripts, the following items must already be deployed on AWS:
*   [Setup BOVI(n)E Role](setup_bovine_role.md) A role in security account that has a trust relation with an assumable role in the target accounts. This role needs readonly rights in the target account.
*   [Cognito user pool setup](setup_cognito.md).
*   [Custom Domain Name setup](setup_custom_domain.md) in Amazon Certificate Manager, API Gateway, and Route 53 (or other DNS provider)
*   [Dynamo](setup_dynamodb.md) table called AWS-Accounts-Table with accountNum as the primary key

You must also have proper serverless config files built:
*   [Serverless Config Example](setup_serverless_config.md)

### Deployment
In the backend directory:
> serverless deploy --profile [aws credentials profile] --stage [deployment stage (dev/prod)]

The profile arg is your AWS credentials profile. The stage arg is the deployment stage.

After deploying, you need to add binary content support in API Gateway:
  - In the AWS Console under API Gateway, click the newly deployed BOVI(n)E API endpoint -> settings. Under "Binary Media Types" add the following content-types: image/png, image/x-icon, image/*, */*
    - NOTE: After making this change, you will need to redeploy the API for the changes to take affect.

Deploy Frontend App
-------------------
In the tools directory:
> sh deploy-content.sh [aws profile] [s3 bucket name for BOVI(n)E html]