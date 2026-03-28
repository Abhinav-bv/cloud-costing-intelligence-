"""
src/collect_metrics.py
SQLite database helpers for inserting and querying metrics.
"""

import sqlite3
from datetime import datetime
from config import LOCAL_DB_CONFIG

def get_connection():
    """Return a new SQLite DB connection."""
    return sqlite3.connect(LOCAL_DB_CONFIG["file"])


def insert_metric(resource_id: str, metric_name: str, metric_value: float, timestamp):
    """Insert a metric datapoint into the metrics table."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO metrics (resource_id, metric_name, metric_value, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (resource_id, metric_name, metric_value, timestamp),
        )
        conn.commit()
    except Exception as e:
        print(f"❌ Error inserting metric: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def get_metrics(resource_id: str, metric_name: str, start, end):
    """Fetch metrics for a resource between start and end timestamps."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT resource_id, metric_name, metric_value, timestamp
            FROM metrics
            WHERE resource_id = ?
              AND metric_name = ?
              AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
            """,
            (resource_id, metric_name, start, end),
        )
        rows = cur.fetchall()
        return rows
    except Exception as e:
        print(f"❌ Error fetching metrics: {e}")
        return []
    finally:
        cur.close()
        conn.close()
