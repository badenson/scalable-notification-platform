#!/bin/bash

ENVIRONMENT=${1:-dev}
REGION=${2:-us-east-1}

# Deploy core infrastructure
aws cloudformation deploy \
  --template-file infrastructure/cfn-templates/notification-platform-core.yml \
  --stack-name notification-platform-core-${ENVIRONMENT} \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides EnvironmentName=${ENVIRONMENT} \
  --region ${REGION}

# Get outputs from core stack
CORE_OUTPUTS=$(aws cloudformation describe-stacks \
  --stack-name notification-platform-core-${ENVIRONMENT} \
  --query 'Stacks[0].Outputs' \
  --region ${REGION})

# Extract specific outputs
TOPIC_ARN=$(echo $CORE_OUTPUTS | jq -r '.[] | select(.OutputKey=="NotificationTopicArn") | .OutputValue')
QUEUE_URL=$(echo $CORE_OUTPUTS | jq -r '.[] | select(.OutputKey=="NotificationQueueUrl") | .OutputValue')

# Package and deploy Lambda functions
# (Assuming you're using SAM for Lambda deployment)
sam package \
  --template-file infrastructure/sam-templates/lambda-functions.yml \
  --output-template-file packaged.yaml \
  --s3-bucket your-deployment-bucket-${ENVIRONMENT}

sam deploy \
  --template-file packaged.yaml \
  --stack-name notification-lambdas-${ENVIRONMENT} \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
      EnvironmentName=${ENVIRONMENT} \
      NotificationTopicArn=${TOPIC_ARN} \
      NotificationQueueUrl=${QUEUE_URL} \
  --region ${REGION}

# Deploy Step Functions
aws cloudformation deploy \
  --template-file infrastructure/cfn-templates/step-functions.yml \
  --stack-name notification-stepfunctions-${ENVIRONMENT} \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
      EnvironmentName=${ENVIRONMENT} \
      NotificationTopicArn=${TOPIC_ARN} \
      EmailSenderLambdaArn="arn:aws:lambda:${REGION}:123456789012:function:email-sender-${ENVIRONMENT}" \
      PushNotificationLambdaArn="arn:aws:lambda:${REGION}:123456789012:function:push-notification-${ENVIRONMENT}" \
      SmsSenderLambdaArn="arn:aws:lambda:${REGION}:123456789012:function:sms-sender-${ENVIRONMENT}" \
  --region ${REGION}