"""
check_db.py
Utility script to list tables and columns in metrics.db
"""

import sqlite3

DB_FILE = "metrics.db"

def show_schema():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # List tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print("Tables in metrics.db:")
    for table in tables:
        print("-", table[0])

        # Show columns for each table
        cursor.execute(f"PRAGMA table_info({table[0]});")
        columns = cursor.fetchall()
        for col in columns:
            print(f"   • {col[1]} ({col[2]})")

    conn.close()

if __name__ == "__main__":
    show_schema()
