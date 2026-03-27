"""
config.py
Configuration file for AWS and local database connections
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AWS RDS Configuration
AWS_RDS_CONFIG = {
    "host": os.getenv("AWS_RDS_HOST", "localhost"),
    "port": int(os.getenv("AWS_RDS_PORT", 5432)),
    "database": os.getenv("AWS_RDS_DB_NAME", "cloud_costing"),
    "user": os.getenv("AWS_RDS_USER", "admin"),
    "password": os.getenv("AWS_RDS_PASSWORD", "password"),
    "engine": os.getenv("AWS_RDS_ENGINE", "postgres"),  # mysql, postgres, mariadb
}

# Local SQLite Configuration
LOCAL_DB_CONFIG = {
    "type": "sqlite",
    "file": os.getenv("LOCAL_DB_FILE", "metrics.db"),
}

# Environment flag
USE_AWS = os.getenv("USE_AWS", "False").lower() == "true"
SYNC_MODE = os.getenv("SYNC_MODE", "both")  # "local", "aws", "both"

# AWS Credentials (optional, uses default AWS profile if not set)
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_PROFILE = os.getenv("AWS_PROFILE", "default")
