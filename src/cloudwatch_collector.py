"""
src/cloudwatch_collector.py
Collectors for AWS CloudWatch metrics (EC2, RDS).
"""

import boto3
from datetime import datetime, timedelta, timezone
from src.collect_metrics import insert_metric

def fetch_ec2_cpu(instance_id: str):
    """Fetch EC2 CPU utilization and insert into DB."""
    client = boto3.client("cloudwatch", region_name="us-east-1")

    end = datetime.now(timezone.utc)
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

    datapoints = response.get("Datapoints", [])
    for dp in datapoints:
        insert_metric(
            resource_id=instance_id,
            metric_name="cpu_usage",
            metric_value=dp["Average"],
            timestamp=dp["Timestamp"]
        )
    print(f"Inserted CPU metrics for {instance_id}")


def fetch_rds_cpu(db_identifier: str):
    """Fetch RDS CPU utilization and insert into DB."""
    client = boto3.client("cloudwatch", region_name="us-east-1")

    end = datetime.now(timezone.utc)
    start = end - timedelta(minutes=5)

    response = client.get_metric_statistics(
        Namespace="AWS/RDS",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "DBInstanceIdentifier", "Value": db_identifier}],
        StartTime=start,
        EndTime=end,
        Period=300,
        Statistics=["Average"]
    )

    datapoints = response.get("Datapoints", [])
    for dp in datapoints:
        insert_metric(
            resource_id=db_identifier,
            metric_name="cpu_usage",
            metric_value=dp["Average"],
            timestamp=dp["Timestamp"]
        )
    print(f"Inserted RDS CPU metrics for {db_identifier}")
