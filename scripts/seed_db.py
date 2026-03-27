"""
seed_db.py
Utility script to insert sample resources and metrics into metrics.db (SQLite)
and/or AWS RDS with support for both local and cloud environments
"""

import sqlite3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import LOCAL_DB_CONFIG, USE_AWS, SYNC_MODE
from aws_utils import RDSConnection, create_rds_tables, sync_sqlite_to_rds

DB_FILE = LOCAL_DB_CONFIG["file"]

def seed_local_sqlite():
    """Seed data into local SQLite database"""
    conn = sqlite3.connect(DB_FILE)
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

    # Insert sample resources
    sample_resources = [
        ("res-001", "AWS"),
        ("res-002", "Azure"),
        ("res-003", "GCP"),
    ]

    for resource_id, provider in sample_resources:
        try:
            cursor.execute(
                "INSERT INTO resources (resource_id, cloud_provider) VALUES (?, ?)",
                (resource_id, provider)
            )
        except sqlite3.IntegrityError:
            print(f"⚠️  Resource {resource_id} already exists, skipping")

    # Insert sample metrics
    sample_metrics = [
        ("res-001", "cpu_usage", 55.0, "2026-03-28T02:15:00"),
        ("res-002", "memory_usage", 70.2, "2026-03-28T02:16:00"),
        ("res-003", "disk_io", 120.5, "2026-03-28T02:17:00"),
    ]

    for resource_id, metric_name, value, timestamp in sample_metrics:
        cursor.execute(
            """INSERT INTO metrics (resource_id, metric_name, metric_value, timestamp)
               VALUES (?, ?, ?, ?)""",
            (resource_id, metric_name, value, timestamp)
        )

    conn.commit()
    conn.close()
    print(f"✅ Seeded sample data into {DB_FILE}")
    return conn


def seed_aws_rds():
    """Seed data into AWS RDS"""
    try:
        # Create tables in RDS
        create_rds_tables()
        
        # Seed sample data
        rds = RDSConnection().connect()
        
        sample_resources = [
            ("res-001", "AWS"),
            ("res-002", "Azure"),
            ("res-003", "GCP"),
        ]

        for resource_id, provider in sample_resources:
            try:
                rds.execute(
                    "INSERT INTO resources (resource_id, cloud_provider) VALUES (%s, %s)",
                    (resource_id, provider)
                )
            except Exception as e:
                print(f"⚠️  Resource {resource_id} may already exist: {e}")

        sample_metrics = [
            ("res-001", "cpu_usage", 55.0, "2026-03-28T02:15:00"),
            ("res-002", "memory_usage", 70.2, "2026-03-28T02:16:00"),
            ("res-003", "disk_io", 120.5, "2026-03-28T02:17:00"),
        ]

        for resource_id, metric_name, value, timestamp in sample_metrics:
            rds.execute(
                """INSERT INTO metrics (resource_id, metric_name, metric_value, timestamp)
                   VALUES (%s, %s, %s, %s)""",
                (resource_id, metric_name, value, timestamp)
            )

        rds.commit()
        print("✅ Seeded sample data into AWS RDS")
        rds.close()
        
    except Exception as e:
        print(f"❌ Error seeding AWS RDS: {e}")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed database with sample data")
    parser.add_argument("--aws", action="store_true", help="Seed AWS RDS only")
    parser.add_argument("--local", action="store_true", help="Seed local SQLite only")
    parser.add_argument("--both", action="store_true", help="Seed both local and AWS (default if neither specified)")
    parser.add_argument("--sync", action="store_true", help="Sync local SQLite to AWS RDS after seeding")
    
    args = parser.parse_args()
    
    # Default to both if no option specified
    if not args.aws and not args.local and not args.both and not args.sync:
        args.both = True
    
    # Seed local SQLite
    if args.local or args.both:
        seed_local_sqlite()
    
    # Seed AWS RDS
    if args.aws or args.both:
        seed_aws_rds()
    
    # Sync option
    if args.sync:
        conn = sqlite3.connect(DB_FILE)
        sync_sqlite_to_rds(conn)
        conn.close()
