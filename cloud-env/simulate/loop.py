import boto3
from dotenv import load_dotenv
import os
import json
import time
from datetime import datetime

load_dotenv('../.env')

# Connect to Lambda
lambda_client = boto3.client(
    'lambda',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

print("🔁 Lambda loop simulation started...")

for i in range(10):
    now = datetime.utcnow()
    
    # Invoke Lambda function
    response = lambda_client.invoke(
        FunctionName='hackathon-loop-function',
        InvocationType='RequestResponse',
        Payload=json.dumps({'count': i})
    )
    
    result = json.loads(response['Payload'].read())
    status = result.get('statusCode', 200)
    print(f"[{now}] 🔁 Invocation #{i+1} - Status: {status}")
    time.sleep(2)

print("✅ Loop simulation complete!")