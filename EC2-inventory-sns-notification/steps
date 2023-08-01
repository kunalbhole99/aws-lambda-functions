import json

import boto3

def lambda_handler(event, context):
    # Connect to AWS SNS
    sns_client = boto3.client('sns')
    
    # Describe EC2 Instances
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_instances()

    instance_status = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_state = instance['State']['Name']
            instance_status.append(f"Instance ID: {instance_id}, Status: {instance_state}")

    # Publish SNS message
    topic_arn = 'arn:aws:sns:us-east-1:819807368852:my-topic' # Replace with your topic arn
    sns_client.publish(
        TopicArn=topic_arn,
        Subject='EC2 Instance Status Report',
        Message='\n'.join(instance_status)
    )

    return {
        'statusCode': 200,
        'body': 'Email Notification send successfully.'
    }

