"""
tests/test_cloudwatch.py
Unit tests for cloudwatch_collector.py using moto to mock AWS CloudWatch.
"""

import boto3
import pytest
from moto import mock_aws
from datetime import datetime, timezone
import src.cloudwatch_collector as collector  # import the module itself

# In-memory capture of inserted metrics
inserted_metrics = []

def fake_insert_metric(*args, **kwargs):
    # Accept both positional and keyword arguments
    inserted_metrics.append({
        "resource_id": args[0] if args else kwargs.get("resource_id"),
        "metric_name": args[1] if len(args) > 1 else kwargs.get("metric_name"),
        "metric_value": args[2] if len(args) > 2 else kwargs.get("metric_value"),
        "timestamp": args[3] if len(args) > 3 else kwargs.get("timestamp"),
    })

@pytest.fixture(autouse=True)
def patch_insert(monkeypatch):
    # Patch the binding inside cloudwatch_collector
    monkeypatch.setattr(collector, "insert_metric", fake_insert_metric)
    inserted_metrics.clear()


@mock_aws
def test_fetch_ec2_cpu_inserts_metrics():
    client = boto3.client("cloudwatch", region_name="us-east-1")
    now = datetime.now(timezone.utc)  # timezone-aware

    client.put_metric_data(
        Namespace="AWS/EC2",
        MetricData=[{
            "MetricName": "CPUUtilization",
            "Dimensions": [{"Name": "InstanceId", "Value": "i-123456"}],
            "Value": 42.0,
            "Timestamp": now
        }]
    )

    collector.fetch_ec2_cpu("i-123456")

    assert len(inserted_metrics) > 0, "No metrics were inserted for EC2"
    assert inserted_metrics[0]["metric_name"] == "cpu_usage"
    assert inserted_metrics[0]["metric_value"] == 42.0


@mock_aws
def test_fetch_rds_cpu_inserts_metrics():
    client = boto3.client("cloudwatch", region_name="us-east-1")
    now = datetime.now(timezone.utc)  # timezone-aware

    client.put_metric_data(
        Namespace="AWS/RDS",
        MetricData=[{
            "MetricName": "CPUUtilization",
            "Dimensions": [{"Name": "DBInstanceIdentifier", "Value": "db-123456"}],
            "Value": 55.0,
            "Timestamp": now
        }]
    )

    collector.fetch_rds_cpu("db-123456")

    assert len(inserted_metrics) > 0, "No metrics were inserted for RDS"
    assert inserted_metrics[0]["metric_name"] == "cpu_usage"
    assert inserted_metrics[0]["metric_value"] == 55.0
