import boto3
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta

load_dotenv('../.env')

# Connect to CloudWatch
cloudwatch = boto3.client(
    'cloudwatch',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

# Connect to S3
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

print("📡 Collecting metrics from CloudWatch...")

# Time range — last 1 hour
end_time = datetime.utcnow()
start_time = end_time - timedelta(hours=1)

# Collect all 3 metrics
metrics = ['IdleCPU', 'NetworkTraffic', 'LambdaInvocations']
all_data = {}

for metric in metrics:
    response = cloudwatch.get_metric_statistics(
        Namespace='HackathonMetrics',
        MetricName=metric,
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=['Average', 'Maximum']
    )
    
    # Sort by time
    datapoints = sorted(
        response['Datapoints'],
        key=lambda x: x['Timestamp']
    )
    
    all_data[metric] = [
        {
            'timestamp': str(dp['Timestamp']),
            'average': dp['Average'],
            'maximum': dp['Maximum']
        }
        for dp in datapoints
    ]
    
    print(f"✅ Collected {len(datapoints)} datapoints for {metric}")

# Save to JSON file
output = {
    'collected_at': str(datetime.utcnow()),
    'metrics': all_data
}

# Save locally
with open('metrics_output.json', 'w') as f:
    json.dump(output, f, indent=2)

print("💾 Saved metrics to metrics_output.json")
print("📊 Summary:")
for metric, data in all_data.items():
    print(f"   {metric}: {len(data)} datapoints")