import sqlite3

DB_FILE = "metrics.db"

def show_tables():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print("Tables in metrics.db:")
    for table in tables:
        print("-", table[0])

    conn.close()

if __name__ == "__main__":
    show_tables()
