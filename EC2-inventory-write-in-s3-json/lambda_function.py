import json

import boto3
import json
import datetime

def lambda_handler(event, context):
    # Describe EC2 Instances
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_instances()

    instance_status = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_state = instance['State']['Name']
            instance_status.append({"Instance ID": instance_id, "Status": instance_state})

    # Create a JSON file with the inventory information
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"ec2_inventory_{timestamp}.json"
    file_content = json.dumps(instance_status)

    # Upload the file to the S3 bucket
    bucket_name = 'my-bucket-987565'  # Replace with your S3 bucket name
    s3_client = boto3.client('s3')
    s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=file_content)

    return {
        "statusCode": 200,
        "body": "EC2 inventory status has been saved to S3."
    }


