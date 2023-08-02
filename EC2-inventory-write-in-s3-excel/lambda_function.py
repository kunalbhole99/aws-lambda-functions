import json

import boto3
import openpyxl
import io

def lambda_handler(event, context):
    # Describe EC2 Instances
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_instances()

    # Process the Inventory Data and create an Excel file
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(["Instance ID", "Instance Name", "Instance State"])

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_name = instance.get('Tags', [{}])[0].get('Value', 'N/A')
            instance_state = instance['State']['Name']
            sheet.append([instance_id, instance_name, instance_state])

    # Save Excel file in memory
    excel_file = io.BytesIO()
    workbook.save(excel_file)
    excel_file.seek(0)

    # Upload the Excel file to the S3 bucket
    bucket_name = 'my-bucket-987565'  # Replace with your S3 bucket name
    s3_client = boto3.client('s3')
    s3_client.put_object(Bucket=bucket_name, Key='ec2_inventory.xlsx', Body=excel_file)

    return {
        "statusCode": 200,
        "body": "EC2 inventory details have been saved to S3 in Excel format.."
    }