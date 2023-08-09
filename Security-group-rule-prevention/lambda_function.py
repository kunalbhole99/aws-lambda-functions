import boto3

def lambda_handler(event, context):
    ec2_client = boto3.client('ec2')

    # Describe all security groups
    response = ec2_client.describe_security_groups()
    security_groups = response['SecurityGroups']

    print(security_groups)
    for security_group in security_groups:
        for permission in security_group['IpPermissions']:
            for ip_range in permission.get('IpRanges', []):
                if ip_range['CidrIp'] == '0.0.0.0/0':
                    # Revoke the rule with 0.0.0.0/0 source
                    ec2_client.revoke_security_group_ingress(
                        GroupId=security_group['GroupId'],
                        IpPermissions=[permission]
                    )
                    print(f"Revoked rule in security group {security_group['GroupId']}: {permission}")
    
    return "Completed rule removal"
