import boto3
import pandas as pd
import sqlite3

# Connect to SQLite database (creates file if not exists)
conn = sqlite3.connect("metrics.db")
cursor = conn.cursor()

# Create a simple table for metrics
cursor.execute("""
CREATE TABLE IF NOT EXISTS aws_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT,
    value REAL,
    timestamp TEXT
)
""")

# Placeholder: simulate metric collection
sample_data = [
    ("CPUUtilization", 12.5, "2026-03-28 00:45:00"),
    ("NetworkIn", 1024.0, "2026-03-28 00:45:00")
]

# Insert sample data
cursor.executemany("INSERT INTO aws_metrics (metric_name, value, timestamp) VALUES (?, ?, ?)", sample_data)
conn.commit()

print("✅ Metrics collected and stored in SQLite!")

# Query back to verify
for row in cursor.execute("SELECT * FROM aws_metrics"):
    print(row)

# Close connection
conn.close()
