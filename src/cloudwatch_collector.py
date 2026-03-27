"""
cloudwatch_collector.py
Fetches metrics from AWS CloudWatch and inserts them into the local DB.
"""

import boto3
from datetime import datetime, timedelta
from src.collect_metrics import insert_metric  # reuse your existing DB insert logic
from config import AWS_REGION

def fetch_ec2_cpu(instance_id, region=AWS_REGION):
    """
    Fetch average CPU utilization for an EC2 instance over the last 5 minutes.
    """
    client = boto3.client("cloudwatch", region_name=region)

    end = datetime.utcnow()
    start = end - timedelta(minutes=5)

    response = client.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        StartTime=start,
        EndTime=end,
        Period=300,
        Statistics=["Average"]
    )

    for datapoint in response["Datapoints"]:
        insert_metric(
            resource_id=instance_id,
            metric_name="cpu_usage",
            metric_value=datapoint["Average"],
            timestamp=datapoint["Timestamp"].isoformat()
        )
    print(f"Inserted CPU metrics for {instance_id}")

def fetch_rds_cpu(db_instance_id, region=AWS_REGION):
    """
    Fetch average CPU utilization for an RDS instance over the last 5 minutes.
    """
    client = boto3.client("cloudwatch", region_name=region)

    end = datetime.utcnow()
    start = end - timedelta(minutes=5)

    response = client.get_metric_statistics(
        Namespace="AWS/RDS",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "DBInstanceIdentifier", "Value": db_instance_id}],
        StartTime=start,
        EndTime=end,
        Period=300,
        Statistics=["Average"]
    )

    for datapoint in response["Datapoints"]:
        insert_metric(
            resource_id=db_instance_id,
            metric_name="rds_cpu_usage",
            metric_value=datapoint["Average"],
            timestamp=datapoint["Timestamp"].isoformat()
        )
    print(f"Inserted RDS CPU metrics for {db_instance_id}")
