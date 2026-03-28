"""
src/cloudwatch_collector.py
AWS CloudWatch metric collectors for EC2, RDS, and other services.
"""

import boto3
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from config import AWS_REGION, CLOUDWATCH_PERIOD
from src.collect_metrics import insert_metric

logger = logging.getLogger(__name__)


class CloudWatchCollector:
    """Collect metrics from AWS CloudWatch"""
    
    def __init__(self, region: str = AWS_REGION):
        self.region = region
        self.client = boto3.client("cloudwatch", region_name=region)
    
    def fetch_metric_statistics(self, namespace: str, metric_name: str,
                                dimensions: Dict[str, str], 
                                start_time: datetime = None,
                                end_time: datetime = None,
                                period: int = CLOUDWATCH_PERIOD,
                                statistic: str = "Average") -> List[Dict[str, Any]]:
        """
        Fetch metric statistics from CloudWatch.
        
        Args:
            namespace: AWS namespace (e.g., "AWS/EC2")
            metric_name: Name of metric (e.g., "CPUUtilization")
            dimensions: Dict of dimension names/values
            start_time: Start time (default: 5 mins ago)
            end_time: End time (default: now)
            period: Period in seconds (default from config)
            statistic: Statistic type (Average, Sum, Maximum, Minimum, Count)
        
        Returns:
            List of datapoints
        """
        if end_time is None:
            end_time = datetime.now(timezone.utc)
        if start_time is None:
            start_time = end_time - timedelta(minutes=5)
        
        try:
            response = self.client.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                Dimensions=[{"Name": k, "Value": v} for k, v in dimensions.items()],
                StartTime=start_time,
                EndTime=end_time,
                Period=period,
                Statistics=[statistic]
            )
            
            datapoints = response.get("Datapoints", [])
            logger.info(f"Fetched {len(datapoints)} {metric_name} datapoints from {namespace}")
            return datapoints
            
        except Exception as e:
            logger.error(f"❌ Error fetching {metric_name} from {namespace}: {e}")
            return []
    
    def collect_ec2_metrics(self, instance_id: str, 
                           metrics: List[str] = None) -> Dict[str, List]:
        """
        Collect EC2 instance metrics (CPU, Network, etc).
        
        Args:
            instance_id: EC2 instance ID
            metrics: List of metric names (default: CPUUtilization, NetworkIn, NetworkOut)
        
        Returns:
            Dict with metric name as key and datapoints list as value
        """
        if metrics is None:
            metrics = ["CPUUtilization", "NetworkIn", "NetworkOut"]
        
        results = {}
        for metric_name in metrics:
            datapoints = self.fetch_metric_statistics(
                namespace="AWS/EC2",
                metric_name=metric_name,
                dimensions={"InstanceId": instance_id}
            )
            results[metric_name] = datapoints
            
            # Store in database
            for dp in datapoints:
                insert_metric(
                    resource_id=instance_id,
                    metric_name=metric_name.lower(),
                    metric_value=dp.get("Average", 0),
                    timestamp=dp["Timestamp"].isoformat()
                )
        
        logger.info(f"Collected EC2 metrics for {instance_id}")
        return results
    
    def collect_lambda_metrics(self, function_name: str,
                              metrics: List[str] = None) -> Dict[str, List]:
        """
        Collect Lambda function metrics.
        
        Args:
            function_name: Lambda function name
            metrics: List of metric names (default: Invocations, Errors, Duration)
        
        Returns:
            Dict with metric name as key and datapoints list as value
        """
        if metrics is None:
            metrics = ["Invocations", "Errors", "Duration", "Throttles"]
        
        results = {}
        for metric_name in metrics:
            datapoints = self.fetch_metric_statistics(
                namespace="AWS/Lambda",
                metric_name=metric_name,
                dimensions={"FunctionName": function_name}
            )
            results[metric_name] = datapoints
            
            # Store in database
            for dp in datapoints:
                insert_metric(
                    resource_id=function_name,
                    metric_name=metric_name.lower(),
                    metric_value=dp.get("Sum" if metric_name == "Invocations" else "Average", 0),
                    timestamp=dp["Timestamp"].isoformat()
                )
        
        logger.info(f"✅ Collected Lambda metrics for {function_name}")
        return results


# Convenience functions
def fetch_ec2_cpu(instance_id: str):
    """Fetch EC2 CPU utilization and insert into DB."""
    collector = CloudWatchCollector()
    collector.collect_ec2_metrics(instance_id, metrics=["CPUUtilization"])
