"""
aws_utils.py
AWS RDS connection utilities and database operations
"""

import psycopg2
import pymysql
import json
from typing import List, Dict, Any
from config import AWS_RDS_CONFIG

class RDSConnection:
    """Handle AWS RDS connections based on engine type"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or AWS_RDS_CONFIG
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish connection to AWS RDS"""
        try:
            engine = self.config.get("engine", "postgres")
            
            if engine == "postgres":
                self.connection = psycopg2.connect(
                    host=self.config["host"],
                    port=self.config["port"],
                    database=self.config["database"],
                    user=self.config["user"],
                    password=self.config["password"]
                )
            elif engine == "mysql" or engine == "mariadb":
                self.connection = pymysql.connect(
                    host=self.config["host"],
                    port=self.config["port"],
                    database=self.config["database"],
                    user=self.config["user"],
                    password=self.config["password"]
                )
            else:
                raise ValueError(f"Unsupported database engine: {engine}")
            
            self.cursor = self.connection.cursor()
            print(f"✅ Connected to AWS RDS ({engine})")
            return self
        
        except Exception as e:
            print(f"❌ Failed to connect to AWS RDS: {e}")
            raise
    
    def close(self):
        """Close RDS connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("✅ RDS connection closed")
    
    def execute(self, query: str, params: tuple = None):
        """Execute a single query"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor
        except Exception as e:
            print(f"❌ Query execution error: {e}")
            raise
    
    def executemany(self, query: str, data: List[tuple]):
        """Execute multiple queries (for bulk inserts)"""
        try:
            self.cursor.executemany(query, data)
            return self.cursor.rowcount
        except Exception as e:
            print(f"❌ Batch execution error: {e}")
            raise
    
    def commit(self):
        """Commit transaction"""
        self.connection.commit()
    
    def rollback(self):
        """Rollback transaction"""
        self.connection.rollback()
    
    def fetchall(self):
        """Fetch all results"""
        return self.cursor.fetchall()
    
    def fetchone(self):
        """Fetch single result"""
        return self.cursor.fetchone()


def create_rds_tables():
    """Create tables in AWS RDS if they don't exist"""
    rds = RDSConnection().connect()
    
    try:
        # Create resources table
        rds.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id SERIAL PRIMARY KEY,
                resource_id VARCHAR(255) UNIQUE NOT NULL,
                cloud_provider VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create metrics table
        rds.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id SERIAL PRIMARY KEY,
                resource_id VARCHAR(255) NOT NULL,
                metric_name VARCHAR(255) NOT NULL,
                metric_value FLOAT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resource_id) REFERENCES resources(resource_id)
            )
        """)
        
        rds.commit()
        print("✅ RDS tables created successfully")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        rds.rollback()
        raise
    finally:
        rds.close()


def import_json_to_rds(json_file: str):
    """Import JSON data into AWS RDS"""
    rds = RDSConnection().connect()
    
    try:
        # Read JSON file
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Expect data structure: {"resources": [...], "metrics": [...]}
        resources = data.get("resources", [])
        metrics = data.get("metrics", [])
        
        # Insert resources
        for resource in resources:
            rds.execute(
                "INSERT INTO resources (resource_id, cloud_provider) VALUES (%s, %s)",
                (resource["resource_id"], resource["cloud_provider"])
            )
        
        # Insert metrics
        for metric in metrics:
            rds.execute(
                """INSERT INTO metrics (resource_id, metric_name, metric_value, timestamp) 
                   VALUES (%s, %s, %s, %s)""",
                (metric["resource_id"], metric["metric_name"], metric["metric_value"], metric["timestamp"])
            )
        
        rds.commit()
        print(f"✅ Imported {len(resources)} resources and {len(metrics)} metrics to RDS")
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        rds.rollback()
        raise
    finally:
        rds.close()


def sync_sqlite_to_rds(sqlite_conn):
    """Sync data from local SQLite to AWS RDS"""
    rds = RDSConnection().connect()
    
    try:
        # Fetch all data from SQLite
        sqlite_cursor = sqlite_conn.cursor()
        
        # Get resources
        sqlite_cursor.execute("SELECT resource_id, cloud_provider FROM resources")
        resources = sqlite_cursor.fetchall()
        
        for resource in resources:
            rds.execute(
                "INSERT INTO resources (resource_id, cloud_provider) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                resource
            )
        
        # Get metrics
        sqlite_cursor.execute("SELECT resource_id, metric_name, metric_value, timestamp FROM metrics")
        metrics = sqlite_cursor.fetchall()
        
        for metric in metrics:
            rds.execute(
                """INSERT INTO metrics (resource_id, metric_name, metric_value, timestamp) 
                   VALUES (%s, %s, %s, %s)""",
                metric
            )
        
        rds.commit()
        print(f"✅ Synced {len(resources)} resources and {len(metrics)} metrics to RDS")
        
    except Exception as e:
        print(f"❌ Sync error: {e}")
        rds.rollback()
        raise
    finally:
        rds.close()
