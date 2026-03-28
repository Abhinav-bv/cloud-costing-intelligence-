import sqlite3
import os

DB_FILE = os.getenv('LOCAL_DB_FILE', 'metrics.db')

CREATE_RESOURCES = """
CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id TEXT UNIQUE NOT NULL,
    resource_type TEXT NOT NULL,
    cloud_provider TEXT NOT NULL,
    region TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_METRICS = """
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    unit TEXT DEFAULT 'None',
    timestamp TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(resource_id) REFERENCES resources(resource_id)
);
"""

CREATE_BILLING = """
CREATE TABLE IF NOT EXISTS billing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id TEXT,
    service TEXT NOT NULL,
    cost REAL NOT NULL,
    currency TEXT DEFAULT 'USD',
    date TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(resource_id) REFERENCES resources(resource_id)
);
"""


def create_tables():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(CREATE_RESOURCES)
    cursor.execute(CREATE_METRICS)
    cursor.execute(CREATE_BILLING)

    conn.commit()
    conn.close()
    print(f"Created tables in {DB_FILE}")


def insert_sample_resources():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    sample_resources = [
        ("i-0123456789abcdef0", "ec2", "aws", "us-east-1"),
        ("db-ABCDEFGHIJKLMNOP", "rds", "aws", "us-east-1"),
        ("lambda:us-east-1:123456789012:function:my-func", "lambda", "aws", "us-east-1"),
    ]

    for resource_id, resource_type, cloud_provider, region in sample_resources:
        cursor.execute(
            "INSERT OR IGNORE INTO resources (resource_id, resource_type, cloud_provider, region) VALUES (?, ?, ?, ?)",
            (resource_id, resource_type, cloud_provider, region)
        )

    conn.commit()
    conn.close()
    print("Inserted sample resources")


def insert_sample_metrics():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    sample_metrics = [
        ("i-0123456789abcdef0", "cpu_utilization", 55.0, "%", "2026-03-28T02:15:00"),
        ("i-0123456789abcdef0", "network_in", 130.0, "Bytes", "2026-03-28T02:20:00"),
        ("db-ABCDEFGHIJKLMNOP", "db_cpu_utilization", 45.0, "%", "2026-03-28T02:20:00"),
        ("lambda:us-east-1:123456789012:function:my-func", "invocations", 12, "Count", "2026-03-28T02:20:00"),
    ]

    for resource_id, metric_name, metric_value, unit, timestamp in sample_metrics:
        cursor.execute(
            "INSERT OR IGNORE INTO metrics (resource_id, metric_name, metric_value, unit, timestamp) VALUES (?, ?, ?, ?, ?)",
            (resource_id, metric_name, metric_value, unit, timestamp)
        )

    conn.commit()
    conn.close()
    print("Inserted sample metrics")


def insert_sample_billing():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    sample_billing = [
        ("i-0123456789abcdef0", "EC2", 2.45, "USD", "2026-03-27"),
        ("db-ABCDEFGHIJKLMNOP", "RDS", 4.33, "USD", "2026-03-27"),
        ("lambda:us-east-1:123456789012:function:my-func", "Lambda", 0.12, "USD", "2026-03-27"),
    ]

    for resource_id, service, cost, currency, date in sample_billing:
        cursor.execute(
            "INSERT OR IGNORE INTO billing (resource_id, service, cost, currency, date) VALUES (?, ?, ?, ?, ?)",
            (resource_id, service, cost, currency, date)
        )

    conn.commit()
    conn.close()
    print("Inserted sample billing")


def reset_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS metrics")
    cursor.execute("DROP TABLE IF EXISTS billing")
    cursor.execute("DROP TABLE IF EXISTS resources")

    conn.commit()
    conn.close()
    print(f"Reset database {DB_FILE}")


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

    print("Database initialization complete!")
