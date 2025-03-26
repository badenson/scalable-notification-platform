import json
import boto3
import os
from botocore.exceptions import ClientError

ses_client = boto3.client('ses')

def lambda_handler(event, context):
    # Parse input from Step Function
    input_data = event.get('input', {})
    
    try:
        response = ses_client.send_email(
            Source=os.environ['SENDER_EMAIL'],
            Destination={
                'ToAddresses': [input_data['recipient']],
            },
            Message={
                'Subject': {
                    'Data': input_data.get('subject', 'Notification'),
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': input_data['message'],
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        
        return {
            'status': 'SUCCESS',
            'message_id': response['MessageId']
        }
        
    except ClientError as e:
        print(f"Error sending email: {e.response['Error']['Message']}")
        raise e