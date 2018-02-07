![Alt text](bovine.png?raw=true "Logo")

BOVI(n)E - Building Operational Visibility Into (n) environments
===================
As Enterprises adopt AWS public cloud, one common strategy to use is the multi-account strategy. This strategy can help security teams isolate
workloads and provide a strong security boundary around sensitive applications. The biggest problem with the multi-account strategy is visibility
and governance. BOVI(n)E helps provide a 10,000 foot view of all your AWS accounts and audit security standards around them. 

BOVI(n)E is a fully serverless single page application leveraging AngularJS, AWS API Gateway, AWS Lambda, and AWS DynamoDB. 

[Quickstart Guide](docs/quickstart.md)

Runtime
-------
The application backend is run on AWS Lambda, and front end is an Angular app.  Authentication is handled through AWS Cognito, and the REST API is exposed through AWS APIGateway.

Deployment
----------

### Prerequisites

Prior to calling the deployment scripts, the following items must already be deployed on AWS:
*   A role in security account that has a trust relation with an assumable role in the target accounts. This role needs readonly rights in the target account.
*   Cognito user pool setup
*   Custom domain setup in Amazon Certificate Manager, API Gateway, and Route 53 (or other DNS provider)
*   DynamoDB table called AWS-Accounts-Table with accountNum as the primary key

You must also have proper serverless config files built:
*   ex: config.prod.json

### Deployment at the top level
Deployment of the API backend application is done with a simple serverless command.
*   To do the initial deploy of the application
    > serverless deploy --profile <aws credentials profile> --stage <deployment stage (dev/prod)>
* After deploying API Gateway, you need to add binary content support:
   - In the AWS Console under API Gateway, click the newly deployed BOVI(n)E API endpoint -> settings. Under "Binary Media Types" add the following content-types: image/png, image/x-icon

### Angular application
Deployment of the static content is an AWS S3 sync of the frontend directory. A simple bash script can be found in the tools directory. This will sync to the
appropriate S3 bucket for the stage.
 > sh deploy-content.sh <aws credential profile> <stage>


What's Next?
------------
*   Better documentation
*   Unit tests
*   Frontend framework update (Angular 4? React?)
*   Compliance rule engine

Additional Info
---------------
You can find additional information on Chick-fil-A's journey around this problem here: https://www.youtube.com/watch?v=_0BCJLIxowQ

