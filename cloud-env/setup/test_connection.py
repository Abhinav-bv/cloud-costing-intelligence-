import boto3
from dotenv import load_dotenv
import os

# Load your keys from .env file
load_dotenv('../.env')

# Try to connect to AWS
sts = boto3.client(
    'sts',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

# Ask AWS "who am I?"
response = sts.get_caller_identity()
print("✅ Connected to AWS successfully!")
print(f"Account ID: {response['Account']}")
print(f"User: {response['Arn']}")