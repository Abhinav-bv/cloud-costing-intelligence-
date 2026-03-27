"""
load_aws_data.py
Load JSON data from AWS S3 or local file into SQLite/RDS
"""

import json
import sys
import os
import argparse
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aws_utils import RDSConnection, import_json_to_rds
from config import LOCAL_DB_CONFIG
import sqlite3


def load_json_to_sqlite(json_file: str):
    """Load JSON data into local SQLite database"""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        conn = sqlite3.connect(LOCAL_DB_CONFIG["file"])
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_id TEXT UNIQUE NOT NULL,
                cloud_provider TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                timestamp TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resource_id) REFERENCES resources(resource_id)
            )
        """)
        
        # Insert resources
        resources = data.get("resources", [])
        for resource in resources:
            try:
                cursor.execute(
                    "INSERT INTO resources (resource_id, cloud_provider) VALUES (?, ?)",
                    (resource["resource_id"], resource["cloud_provider"])
                )
            except sqlite3.IntegrityError:
                print(f"⚠️  Resource {resource['resource_id']} already exists, skipping")
        
        # Insert metrics
        metrics = data.get("metrics", [])
        for metric in metrics:
            cursor.execute(
                """INSERT INTO metrics (resource_id, metric_name, metric_value, timestamp)
                   VALUES (?, ?, ?, ?)""",
                (metric["resource_id"], metric["metric_name"], metric["metric_value"], metric["timestamp"])
            )
        
        conn.commit()
        conn.close()
        
        print(f"✅ Imported {len(resources)} resources and {len(metrics)} metrics to SQLite")
        
    except Exception as e:
        print(f"❌ Error loading JSON to SQLite: {e}")
        raise


def download_from_s3(bucket: str, key: str, local_file: str):
    """Download JSON file from AWS S3"""
    try:
        import boto3
        s3 = boto3.client('s3')
        s3.download_file(bucket, key, local_file)
        print(f"✅ Downloaded from S3: s3://{bucket}/{key}")
        return local_file
    except Exception as e:
        print(f"❌ Error downloading from S3: {e}")
        raise


def load_from_s3_json(bucket: str, key: str, target: str = "both"):
    """Load data directly from S3 JSON file"""
    try:
        import boto3
        s3 = boto3.client('s3')
        
        obj = s3.get_object(Bucket=bucket, Key=key)
        data = json.loads(obj['Body'].read())
        
        resources = data.get("resources", [])
        metrics = data.get("metrics", [])
        
        if target in ["sqlite", "both"]:
            _insert_sqlite_data(resources, metrics)
        
        if target in ["rds", "both"]:
            _insert_rds_data(resources, metrics)
        
        print(f"✅ Loaded {len(resources)} resources and {len(metrics)} metrics from S3")
        
    except Exception as e:
        print(f"❌ Error loading from S3: {e}")
        raise


def _insert_sqlite_data(resources: list, metrics: list):
    """Helper to insert data into SQLite"""
    conn = sqlite3.connect(LOCAL_DB_CONFIG["file"])
    cursor = conn.cursor()
    
    for resource in resources:
        try:
            cursor.execute(
                "INSERT INTO resources (resource_id, cloud_provider) VALUES (?, ?)",
                (resource["resource_id"], resource["cloud_provider"])
            )
        except sqlite3.IntegrityError:
            pass
    
    for metric in metrics:
        cursor.execute(
            """INSERT INTO metrics (resource_id, metric_name, metric_value, timestamp)
               VALUES (?, ?, ?, ?)""",
            (metric["resource_id"], metric["metric_name"], metric["metric_value"], metric["timestamp"])
        )
    
    conn.commit()
    conn.close()


def _insert_rds_data(resources: list, metrics: list):
    """Helper to insert data into RDS"""
    rds = RDSConnection().connect()
    
    for resource in resources:
        try:
            rds.execute(
                "INSERT INTO resources (resource_id, cloud_provider) VALUES (%s, %s)",
                (resource["resource_id"], resource["cloud_provider"])
            )
        except Exception:
            pass
    
    for metric in metrics:
        rds.execute(
            """INSERT INTO metrics (resource_id, metric_name, metric_value, timestamp)
               VALUES (%s, %s, %s, %s)""",
            (metric["resource_id"], metric["metric_name"], metric["metric_value"], metric["timestamp"])
        )
    
    rds.commit()
    rds.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load AWS data from JSON/S3")
    
    parser.add_argument("--local-file", help="Load from local JSON file")
    parser.add_argument("--s3-bucket", help="S3 bucket name")
    parser.add_argument("--s3-key", help="S3 object key")
    parser.add_argument("--target", choices=["sqlite", "rds", "both"], default="both",
                       help="Target database")
    
    args = parser.parse_args()
    
    if args.local_file:
        load_json_to_sqlite(args.local_file)
    elif args.s3_bucket and args.s3_key:
        load_from_s3_json(args.s3_bucket, args.s3_key, args.target)
    else:
        print("Usage:")
        print("  Local JSON: python load_aws_data.py --local-file data/sample_data.json")
        print("  From S3:    python load_aws_data.py --s3-bucket my-bucket --s3-key data.json")
