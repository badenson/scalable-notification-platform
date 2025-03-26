import json
import boto3
import os

pinpoint = boto3.client('pinpoint')

def lambda_handler(event, context):
    input_data = event.get('input', {})
    
    try:
        response = pinpoint.send_messages(
            ApplicationId=os.environ['PINPOINT_APP_ID'],
            MessageRequest={
                'Addresses': {
                    input_data['recipient']: {
                        'ChannelType': 'APNS'  # or 'GCM' for Android
                    }
                },
                'MessageConfiguration': {
                    'APNSMessage': {
                        'Action': 'OPEN_APP',
                        'Body': input_data['message'],
                        'Title': input_data.get('title', 'Notification')
                    }
                }
            }
        )
        
        return {
            'status': 'SUCCESS',
            'message_id': response['MessageResponse']['Result'][input_data['recipient']]['MessageId']
        }
        
    except Exception as e:
        print(f"Error sending push notification: {str(e)}")
        raise e