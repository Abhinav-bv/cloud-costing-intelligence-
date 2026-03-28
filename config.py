"""
config.py
Configuration for data pipeline: metrics collection, storage, and cleaning
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# LOCAL STORAGE (SQLite) - PRIMARY DATA STORE FOR PIPELINE
# ============================================================================

LOCAL_DB_CONFIG = {
    "type": "sqlite",
    "file": os.getenv("LOCAL_DB_FILE", "metrics.db"),
}

# ============================================================================
# AWS CONFIGURATION - FOR DATA COLLECTION VIA CloudWatch/Cost Explorer
# ============================================================================

# AWS Region for CloudWatch/Monitoring API calls
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_PROFILE = os.getenv("AWS_PROFILE", "default")  # AWS credentials profile

# CloudWatch Configuration
CLOUDWATCH_NAMESPACE = os.getenv("CLOUDWATCH_NAMESPACE", "AWS/EC2")
CLOUDWATCH_PERIOD = int(os.getenv("CLOUDWATCH_PERIOD", 300))  # 5 minutes

# GCP Configuration (if using GCP)
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", None)
GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH", None)

# ============================================================================
# DATA PIPELINE SETTINGS
# ============================================================================

# Resource IDs to monitor (EC2 instances, RDS DBs, Lambda functions)
# Example value in .env: MONITORED_RESOURCES=i-0123456789abcdef0,db-ABCDEFGHIJKLMNOP,lambda:us-east-1:123456789012:function:my-func
MONITORED_RESOURCES = os.getenv("MONITORED_RESOURCES", "i-0123456789abcdef0,db-ABCDEFGHIJKLMNOP,lambda:us-east-1:123456789012:function:my-func").split(",")

# Data collection interval (minutes)
COLLECTION_INTERVAL = int(os.getenv("COLLECTION_INTERVAL", 5))

# Data retention (days)
DATA_RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", 90))

# ============================================================================
# PANDAS/ML PIPELINE SETTINGS
# ============================================================================

# Output directory for cleaned data/CSV exports
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")
ML_READY_CSV = os.getenv("ML_READY_CSV", "ml_ready_data.csv")

# Optional optimization cost report from S3 (for dashboard before/after view)
COST_REPORT_BUCKET = os.getenv(
    "COST_REPORT_BUCKET",
    "hackathon-cost-reports-457563661765-us-east-1-an",
)
COST_REPORT_KEY = os.getenv("COST_REPORT_KEY", "cost_report.json")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "pipeline.log")
