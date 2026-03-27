"""
seed_db.py
Utility script to insert sample resources and metrics into metrics.db
"""

import sqlite3

DB_FILE = "metrics.db"

def seed_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Insert sample resources
    cursor.execute("INSERT INTO resources (resource_id, cloud_provider) VALUES (?, ?)", ("res-001", "AWS"))
    cursor.execute("INSERT INTO resources (resource_id, cloud_provider) VALUES (?, ?)", ("res-002", "Azure"))
    cursor.execute("INSERT INTO resources (resource_id, cloud_provider) VALUES (?, ?)", ("res-003", "GCP"))

    # Insert sample metrics
    cursor.execute("""
        INSERT INTO metrics (resource_id, metric_name, metric_value, timestamp)
        VALUES (?, ?, ?, ?)
    """, ("res-001", "cpu_usage", 55.0, "2026-03-28T02:15:00"))

    cursor.execute("""
        INSERT INTO metrics (resource_id, metric_name, metric_value, timestamp)
        VALUES (?, ?, ?, ?)
    """, ("res-002", "memory_usage", 70.2, "2026-03-28T02:16:00"))

    cursor.execute("""
        INSERT INTO metrics (resource_id, metric_name, metric_value, timestamp)
        VALUES (?, ?, ?, ?)
    """, ("res-003", "disk_io", 120.5, "2026-03-28T02:17:00"))

    conn.commit()
    conn.close()
    print("Seeded sample resources and metrics into metrics.db")

if __name__ == "__main__":
    seed_data()
