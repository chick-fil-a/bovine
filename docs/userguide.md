User Guide
=================
Once BOVI(n)E is running in your security account, you can access it by hitting the custom domain setup during the install process (ex: https://bovine.example.com). Your login will leverage Cognito which can be federated to a SAML provider or use local accounts. After successfully authenticating, you will be presented with a dashboard summary of all accounts accessible to BOVI(n)E.

![Alt text](images/dashboard.png?raw=true "Dashboard")

Each dashboard panel is clickable and will take you to a listing of all the resources in that type - accounts, IAM Users, EC2 Instances, etc. The top level menus are split into the following categories - accounts, IAM (Users and Roles), Infrastructure (EC2 instances, security groups, etc), Databases (RDS, Redshift, and Dynamo), and S3.

To view all Instances, click the Instances dashboard panel or click the Infrastructure drop down at the top and choose instances.

![Alt text](images/instances.png?raw=true "Instances")

To view the details of a specific instance, click the instance you would like to view. From there you will see high level details of that specific instance such as public/private IP, DNS name, image name, subnet, etc.

![Alt text](images/instance.png?raw=true "Instance")

To view all IAM users across all of your accounts, click the IAM dropdown at top and choose Users.

![Alt text](images/users.png?raw=true "Users")

To view the details of a specific IAM user, click the user you would like to view. You will see a high level overview of that user with details such as the creation date, whether or not a password is set, and the IAM policies associated to the user.

![Alt text](images/user.png?raw=true "User")

Each section is similar to the above so if you have any questions or suggestions, please let us know!