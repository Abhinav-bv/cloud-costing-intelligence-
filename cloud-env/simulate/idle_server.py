import boto3
from dotenv import load_dotenv
import os
import time
from datetime import datetime

load_dotenv('../.env')

# Connect to CloudWatch
cloudwatch = boto3.client(
    'cloudwatch',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

print("😴 Idle server simulation started...")

while True:
    # Get current time
    now = datetime.utcnow()
    
    # Send a metric to CloudWatch saying CPU is very low (idle)
    cloudwatch.put_metric_data(
        Namespace='HackathonMetrics',
        MetricData=[
            {
                'MetricName': 'IdleCPU',
                'Value': 2.0,  # 2% CPU = basically doing nothing
                'Unit': 'Percent',
                'Timestamp': now
            }
        ]
    )
    
    print(f"[{now}] 📊 Sent idle metric to CloudWatch - CPU: 2%")
    time.sleep(10)  # wait 60 seconds and repeat