import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import boto3
import pandas as pd
import sqlite3
from datetime import datetime
from config import LOCAL_DB_CONFIG, USE_AWS, SYNC_MODE
from src.aws_utils import RDSConnection


# Database connections
sqlite_conn = None
rds_conn = None

def initialize_connections():
    """Initialize database connections based on configuration"""
    global sqlite_conn, rds_conn
    
    # Initialize SQLite if needed
    if SYNC_MODE in ["local", "both"]:
        sqlite_conn = sqlite3.connect(LOCAL_DB_CONFIG["file"])
        _create_sqlite_tables()
    
    # Initialize RDS if needed
    if USE_AWS or SYNC_MODE in ["aws", "both"]:
        try:
            rds_conn = RDSConnection().connect()
            print("✅ Connected to AWS RDS for metrics")
        except Exception as e:
            print(f"⚠️  AWS RDS connection failed: {e}")
            if USE_AWS:
                raise


def _create_sqlite_tables():
    """Create required tables in SQLite"""
    cursor = sqlite_conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS aws_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metric_name TEXT,
        value REAL,
        timestamp TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
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
    
    sqlite_conn.commit()


def collect_from_cloudwatch(aws_region="us-east-1"):
    """Collect metrics from AWS CloudWatch"""
    try:
        cloudwatch = boto3.client('cloudwatch', region_name=aws_region)
        print(f"📊 Collecting metrics from CloudWatch ({aws_region})...")
        
        # Example: Get EC2 metrics
        response = cloudwatch.list_metrics(Namespace='AWS/EC2')
        metrics = []
        
        for metric in response.get('Metrics', [])[:10]:  # Limit to first 10
            metrics.append({
                'metric_name': metric['MetricName'],
                'namespace': metric['Namespace'],
                'dimensions': metric.get('Dimensions', [])
            })
        
        return metrics
    except Exception as e:
        print(f"❌ Error collecting from CloudWatch: {e}")
        return []


def insert_metric_sqlite(metric_name, value, timestamp=None):
    """Insert metric into local SQLite"""
    if not sqlite_conn:
        return False
    
    cursor = sqlite_conn.cursor()
    timestamp = timestamp or datetime.now().isoformat()
    
    try:
        cursor.execute(
            "INSERT INTO aws_metrics (metric_name, value, timestamp) VALUES (?, ?, ?)",
            (metric_name, value, timestamp)
        )
        sqlite_conn.commit()
        return True
    except Exception as e:
        print(f"❌ SQLite insert error: {e}")
        return False


def insert_metric_rds(metric_name, value, timestamp=None, resource_id="res-001"):
    """Insert metric into AWS RDS"""
    if not rds_conn:
        return False
    
    timestamp = timestamp or datetime.now().isoformat()
    
    try:
        rds_conn.execute(
            """INSERT INTO metrics (resource_id, metric_name, metric_value, timestamp)
               VALUES (%s, %s, %s, %s)""",
            (resource_id, metric_name, value, timestamp)
        )
        rds_conn.commit()
        return True
    except Exception as e:
        print(f"❌ RDS insert error: {e}")
        return False


def insert_metric(metric_name, value, timestamp=None, resource_id="res-001"):
    """Insert metric into configured database(s)"""
    results = {}
    
    if SYNC_MODE in ["local", "both"]:
        results['sqlite'] = insert_metric_sqlite(metric_name, value, timestamp)
    
    if SYNC_MODE in ["aws", "both"]:
        results['rds'] = insert_metric_rds(metric_name, value, timestamp, resource_id)
    
    return results


# Sample data collection
sample_data = [
    ("CPUUtilization", 12.5, "2026-03-28 00:45:00"),
    ("NetworkIn", 1024.0, "2026-03-28 00:45:00"),
    ("MemoryUtilization", 45.3, "2026-03-28 00:46:00"),
]

if __name__ == "__main__":
    print(f"🔧 Database Mode: {SYNC_MODE}")
    print(f"💾 AWS Enabled: {USE_AWS}\n")
    
    # Initialize connections
    initialize_connections()
    
    # Insert sample data
    for metric_name, value, timestamp in sample_data:
        results = insert_metric(metric_name, value, timestamp)
        print(f"✅ Inserted {metric_name}: {results}")
    
    # Query back from SQLite
    if sqlite_conn:
        print("\n📋 Data from SQLite:")
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM aws_metrics LIMIT 5")
        for row in cursor.fetchall():
            print(row)
        sqlite_conn.close()
    
    # Query back from RDS
    if rds_conn:
        print("\n📋 Data from AWS RDS:")
        rds_conn.execute("SELECT * FROM metrics LIMIT 5")
        for row in rds_conn.fetchall():
            print(row)
        rds_conn.close()
    
    print("\n✅ Metrics collected and stored!")
