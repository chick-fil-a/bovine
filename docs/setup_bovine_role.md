Deploy BOVI(n)E Role in BOVI(n)E Account
----------------------------------------
In order for BOVI(n)E to be able to pull account information, it will need the ability to assume into a role in your target accounts. The target account role will also need the SecurityAudit and ReadOnlyAccess IAM policies attached.

This role can be deployed via the cloudformation template found here: [BOVI(n)E Role Setup](tools/bovine-role-cf.yml)