"""
scripts/seed_db.py
Initialize SQLite database with schema and sample data for testing.
"""

import sqlite3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import LOCAL_DB_CONFIG

DB_FILE = LOCAL_DB_CONFIG["file"]


def create_tables():
    """Create required tables in SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Resources table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_id TEXT UNIQUE NOT NULL,
            resource_type TEXT NOT NULL,
            cloud_provider TEXT NOT NULL,
            region TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Metrics table - stores all metrics from CloudWatch
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_id TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            timestamp TEXT NOT NULL,
            unit TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (resource_id) REFERENCES resources(resource_id)
        )
    """)

    # Billing table - stores cost data from Cost Explorer
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS billing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_id TEXT,
            service TEXT NOT NULL,
            cost REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print(f"✅ Created tables in {DB_FILE}")


def insert_sample_resources():
    """Insert sample resources for testing"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    sample_resources = [
        ("i-0123456789abcdef0", "EC2", "AWS", "us-east-1"),
        ("i-0abcdef0123456789", "EC2", "AWS", "us-east-1"),
        ("rds-db-prod-01", "RDS", "AWS", "us-east-1"),
        ("lambda-func-01", "Lambda", "AWS", "us-east-1"),
    ]

    for resource_id, resource_type, provider, region in sample_resources:
        try:
            cursor.execute(
                """INSERT INTO resources (resource_id, resource_type, cloud_provider, region) 
                   VALUES (?, ?, ?, ?)""",
                (resource_id, resource_type, provider, region)
            )
        except sqlite3.IntegrityError:
            print(f"⚠️  Resource {resource_id} already exists, skipping")

    conn.commit()
    conn.close()
    print(f"✅ Inserted sample resources into {DB_FILE}")


def insert_sample_metrics():
    """Insert sample metrics for testing"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    sample_metrics = [
        ("i-0123456789abcdef0", "cpu_utilization", 45.5, "2026-03-28T10:00:00Z", "%"),
        ("i-0123456789abcdef0", "cpu_utilization", 48.2, "2026-03-28T10:05:00Z", "%"),
        ("i-0abcdef0123456789", "cpu_utilization", 5.2, "2026-03-28T10:00:00Z", "%"),
        ("i-0abcdef0123456789", "memory_utilization", 72.1, "2026-03-28T10:00:00Z", "%"),
        ("rds-db-prod-01", "cpu_utilization", 38.5, "2026-03-28T10:00:00Z", "%"),
        ("rds-db-prod-01", "database_connections", 125, "2026-03-28T10:00:00Z", "Count"),
        ("lambda-func-01", "invocations", 1250, "2026-03-28T10:00:00Z", "Count"),
        ("lambda-func-01", "errors", 3, "2026-03-28T10:00:00Z", "Count"),
    ]

    for resource_id, metric_name, value, timestamp, unit in sample_metrics:
        cursor.execute(
            """INSERT INTO metrics (resource_id, metric_name, metric_value, timestamp, unit)
               VALUES (?, ?, ?, ?, ?)""",
            (resource_id, metric_name, value, timestamp, unit)
        )

    conn.commit()
    conn.close()
    print(f"✅ Inserted sample metrics into {DB_FILE}")


def insert_sample_billing():
    """Insert sample billing data for testing"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    sample_billing = [
        ("i-0123456789abcdef0", "EC2 - On Demand", 15.45, "USD", "2026-03-28"),
        ("i-0abcdef0123456789", "EC2 - On Demand", 2.30, "USD", "2026-03-28"),
        ("rds-db-prod-01", "RDS - PostgreSQL", 45.50, "USD", "2026-03-28"),
        ("lambda-func-01", "Lambda", 8.25, "USD", "2026-03-28"),
    ]

    for resource_id, service, cost, currency, date in sample_billing:
        cursor.execute(
            """INSERT INTO billing (resource_id, service, cost, currency, date)
               VALUES (?, ?, ?, ?, ?)""",
            (resource_id, service, cost, currency, date)
        )

    conn.commit()
    conn.close()
    print(f"✅ Inserted sample billing data into {DB_FILE}")


def reset_database():
    """Drop all tables (destructive!)"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS metrics")
    cursor.execute("DROP TABLE IF EXISTS billing")
    cursor.execute("DROP TABLE IF EXISTS resources")

    conn.commit()
    conn.close()
    print(f"✅ Reset database {DB_FILE}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed SQLite database for metrics pipeline")
    parser.add_argument("--reset", action="store_true", help="Reset database (destructive)")
    parser.add_argument("--create-only", action="store_true", help="Only create schema, skip sample data")

    args = parser.parse_args()

    if args.reset:
        reset_database()

    create_tables()

    if not args.create_only:
        insert_sample_resources()
        insert_sample_metrics()
        insert_sample_billing()

    print("✅ Database initialization complete!")
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
