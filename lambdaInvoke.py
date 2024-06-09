import boto3
import json

# Create a Boto3 Lambda client
lambda_client = boto3.client('lambda', endpoint_url='http://localhost:4566')  # Use the LocalStack endpoint URL

# Specify the function name
function_name = 'JobScraperLambda'

# Construct the input payload (if needed)
payload = {}

# Invoke the Lambda function
response = lambda_client.invoke(
    FunctionName=function_name,
    Payload=json.dumps(payload)
)

# Parse the response
response_payload = response['Payload'].read().decode('utf-8')
print(response_payload)
