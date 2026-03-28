import boto3
from dotenv import load_dotenv
import os
import time
from datetime import datetime

load_dotenv('../.env')

cloudwatch = boto3.client(
    'cloudwatch',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

print("📈 Traffic spike simulation started...")

for cycle in range(10):  # repeat 10 cycles
    print(f"\n--- Cycle {cycle+1}/10 ---")
    
    # Normal traffic phase
    for i in range(3):
        now = datetime.utcnow()
        cloudwatch.put_metric_data(
            Namespace='HackathonMetrics',
            MetricData=[{
                'MetricName': 'NetworkTraffic',
                'Value': 10.0,
                'Unit': 'Count',
                'Timestamp': now
            }]
        )
        print(f"[{now}] 🟢 Normal traffic - Requests: 10")
        time.sleep(5)

    # Spike phase
    for i in range(5):
        now = datetime.utcnow()
        cloudwatch.put_metric_data(
            Namespace='HackathonMetrics',
            MetricData=[{
                'MetricName': 'NetworkTraffic',
                'Value': 950.0,
                'Unit': 'Count',
                'Timestamp': now
            }]
        )
        print(f"[{now}] 🔴 SPIKE detected - Requests: 950")
        time.sleep(5)

    print(f"✅ Cycle {cycle+1} complete! Waiting 30 seconds...")
    time.sleep(30)

print("✅ All 10 cycles complete!")