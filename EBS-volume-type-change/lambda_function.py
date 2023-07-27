import json
import boto3


def get_volume_id_from_arn(volume_arn):
    # split the ARN using the colon (':') separator
    arn_parts = volume_arn.split(':')
    # The volume ID is the last part of the arn after the 'volume/' prefix
    volume_id = arn_parts[-1].split('/')[-1]
    return volume_id


def lambda_handler(event, context):
    
    volume_arn = event['resources'][0]
    volume_id = get_volume_id_from_arn(volume_arn)

    ec2_client = boto3.client('ec2')

    response = ec2_client.modify_volume(
        VolumeId=volume_id,
        VolumeType='gp3',
   )

   # this is the outout of event in this project 
'''
   def lambda_handler(event, context):
       print(event)
   
    {
  "version":"0",
  "id":"befe1d72-3332-1cdd-76cf-d7a1df0571cf",
  "detail-type":"EBS Volume Notification",
  "source":"aws.ec2",
  "account":"819807368852",
  "time":"2023-07-26T10:50:34Z",
  "region":"us-east-1",
  "resources":[
      "arn:aws:ec2:us-east-1:819807368852:volume/vol-0d618373dcb9dd3ad"
  ],
  "detail":{
      "result":"available",
      "cause":"",
      "event":"createVolume",
      "request-id":"6c0375f9-b48c-4b3d-bae8-0c78ab623bcf"
  }
}
   
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

    '''
