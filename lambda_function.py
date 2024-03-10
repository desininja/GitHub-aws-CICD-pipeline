import json
import boto3
import os
import pandas as pd 
from io import StringIO


sns_client = boto3.client('sns')
sns_arn = 'arn:aws:sns:us-east-1:767398036887:lambda-sns-email'


def lambda_handler(event, context):
    
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    destination_bucket = os.environ.get('destinationBucket')
    
    print('Bucket name: ', event['Records'][0]['s3']['bucket']['name'])
    print('Object key: ', event['Records'][0]['s3']['object']['key'])
    
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=source_bucket, Key=object_key)
    json_data = obj['Body'].read().decode('utf-8')
    
    
    print("JSON Data:")
    print(json_data)
    
    try:
        # Load the JSON data into a Pandas DataFrame
        df = pd.read_json(StringIO(json_data))
        
        print("Delivered orders are: ")
        delivered_df = df[df['status'] == 'delivered']
        print(delivered_df)
        
        dest_obj_key = object_key[0:10] + '-delivered_orders.json'
        s3.put_object(Bucket=destination_bucket, Key=dest_obj_key, Body=delivered_df.to_json(orient='records'))
        
        message = f"Input S3 File {'s3://' + source_bucket + '/' + object_key} has been processed successfully !! and uploaded to the destination bucket {'s3://' + destination_bucket + '/' + dest_obj_key}"
        sns_client.publish(Subject="SUCCESS - Daily DoorDash Data Processing",TargetArn=sns_arn, Message=message, MessageStructure='text')
        return {
            'statusCode': 200,
            'body': json.dumps('Lambda triggered on file upload')
        }
        
    except Exception as e:
        print("Error processing JSON data:", str(e))
        message = f"Input S3 File {'s3://'+source_bucket+'/'+object_key} Failed!!!!!!"
        sns_client.publish(Subject="FAILED!!!!! - Daily DoorDash Data Processing",TargetArn=sns_arn, Message=message, MessageStructure='text')
        
