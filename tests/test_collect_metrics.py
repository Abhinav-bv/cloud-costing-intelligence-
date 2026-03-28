"""
test_collect_metrics.py
Unit tests for verifying metric collection and DB insertion.
"""

import sqlite3
import os
import pytest

DB_FILE = "metrics.db"

# --- Helper function ---
def insert_sample_metric():
    """Insert one sample metric into the DB for testing."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO metrics (resource_id, metric_name, metric_value, timestamp)
        VALUES (?, ?, ?, ?)
    """, ("res-001", "cpu_usage", 42.5, "2026-03-28T02:05:00"))

    conn.commit()
    conn.close()

# --- Tests ---
def test_metrics_table_exists():
    """Ensure the metrics table exists in the DB."""
    assert os.path.exists(DB_FILE), "metrics.db should exist"

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='metrics';")
    result = cursor.fetchone()

    conn.close()
    assert result is not None, "metrics table should exist"

def test_insert_and_retrieve_metric():
    """Insert a metric and verify it can be retrieved."""
    insert_sample_metric()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT metric_name, metric_value FROM metrics WHERE resource_id='res-001';")
    row = cursor.fetchone()

    conn.close()
    assert row is not None, "Inserted metric should be retrievable"
    assert row[0] == "cpu_usage"
    assert row[1] == 42.5
