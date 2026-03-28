"""
aws_utils.py
AWS SDK helpers for cost intelligence data pipeline.
"""

import boto3
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CostExplorerCollector:
    """Collect cost and usage data from AWS Cost Explorer"""
    
    def __init__(self, region: str = "us-east-1"):
        self.client = boto3.client("ce", region_name=region)
    
    def get_cost_data(self, start_date: str, end_date: str,
                     granularity: str = "DAILY",
                     metrics: List[str] = None) -> Dict[str, Any]:
        """
        Fetch cost and usage data from AWS Cost Explorer.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            granularity: DAILY, MONTHLY
            metrics: Cost metrics to retrieve (default: UnblendedCost)
        
        Returns:
            Cost and usage data grouped by service or dimension
        """
        if metrics is None:
            metrics = ["UnblendedCost"]
        
        try:
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    "Start": start_date,
                    "End": end_date
                },
                Granularity=granularity,
                Metrics=metrics,
                GroupBy=[
                    {
                        "Type": "DIMENSION",
                        "Key": "SERVICE"
                    }
                ]
            )
            
            logger.info(f"✅ Retrieved cost data from {start_date} to {end_date}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error fetching cost data: {e}")
            return {}
    
    def get_cost_by_resource(self, start_date: str, end_date: str,
                            service: str = None) -> Dict[str, Any]:
        """
        Get cost breakdown by resource.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            service: Filter by AWS service (optional)
        
        Returns:
            Cost data grouped by resource ID or tag
        """
        try:
            request = {
                "TimePeriod": {
                    "Start": start_date,
                    "End": end_date
                },
                "Granularity": "DAILY",
                "Metrics": ["UnblendedCost"],
                "GroupBy": [
                    {
                        "Type": "TAG",
                        "Key": "Name"  # Group by Name tag
                    }
                ]
            }
            
            if service:
                request["Filter"] = {
                    "Dimensions": {
                        "Key": "SERVICE",
                        "Values": [service]
                    }
                }
            
            response = self.client.get_cost_and_usage(**request)
            logger.info(f"✅ Retrieved cost data by resource")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error fetching resource cost data: {e}")
            return {}


class EC2Manager:
    """Manage EC2 instances for cost optimization"""
    
    def __init__(self, region: str = "us-east-1"):
        self.client = boto3.client("ec2", region_name=region)
    
    def get_instances(self, filters: List[Dict] = None) -> List[Dict]:
        """Get EC2 instances with optional filters"""
        try:
            params = {}
            if filters:
                params["Filters"] = filters
            
            response = self.client.describe_instances(**params)
            instances = []
            
            for reservation in response.get("Reservations", []):
                instances.extend(reservation.get("Instances", []))
            
            logger.info(f"✅ Retrieved {len(instances)} EC2 instances")
            return instances
            
        except Exception as e:
            logger.error(f"❌ Error getting EC2 instances: {e}")
            return []
    
    def get_idle_instances(self, cpu_threshold: float = 5.0) -> List[str]:
        """
        Find idle EC2 instances based on CPU utilization.
        (Requires CloudWatch metrics analysis)
        """
        logger.info("Note: Call CloudWatchCollector to analyze CPU metrics first")
        return []
    
    def stop_instance(self, instance_id: str) -> bool:
        """Stop a running EC2 instance"""
        try:
            self.client.stop_instances(InstanceIds=[instance_id])
            logger.info(f"✅ Stopped instance {instance_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error stopping instance {instance_id}: {e}")
            return False
    
    def terminate_instance(self, instance_id: str) -> bool:
        """Terminate an EC2 instance"""
        try:
            self.client.terminate_instances(InstanceIds=[instance_id])
            logger.info(f"✅ Terminated instance {instance_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error terminating instance {instance_id}: {e}")
            return False


class S3Manager:
    """Manage S3 buckets for data storage"""
    
    def __init__(self):
        self.client = boto3.client("s3")
    
    def upload_file(self, file_path: str, bucket: str, key: str) -> bool:
        """Upload file to S3"""
        try:
            self.client.upload_file(file_path, bucket, key)
            logger.info(f"✅ Uploaded {file_path} to s3://{bucket}/{key}")
            return True
        except Exception as e:
            logger.error(f"❌ Error uploading to S3: {e}")
            return False
    
    def download_file(self, bucket: str, key: str, file_path: str) -> bool:
        """Download file from S3"""
        try:
            self.client.download_file(bucket, key, file_path)
            logger.info(f"✅ Downloaded s3://{bucket}/{key} to {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Error downloading from S3: {e}")
            return False

