import json
import boto3
import os
from enum import Enum

class NotificationType(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"

def lambda_handler(event, context):
    # Initialize clients
    stepfunctions = boto3.client('stepfunctions')
    sns = boto3.client('sns')
    
    # Process each record from SQS
    for record in event['Records']:
        try:
            message = json.loads(record['body'])
            
            # Validate message structure
            if not all(key in message for key in ['recipient', 'message', 'notification_type']):
                raise ValueError("Missing required fields in message")
            
            # Determine notification type
            notification_type = NotificationType(message['notification_type'].lower())
            
            # Start appropriate Step Function workflow
            state_machine_arn = os.environ[f'{notification_type.value.upper()}_STATE_MACHINE_ARN']
            
            response = stepfunctions.start_execution(
                stateMachineArn=state_machine_arn,
                input=json.dumps(message)
            )
            
            print(f"Started {notification_type.value} workflow: {response['executionArn']}")
            
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            # Message will be retried or sent to DLQ based on SQS configuration
            raise e

    return {
        'statusCode': 200,
        'body': json.dumps('Messages processed successfully')
    }