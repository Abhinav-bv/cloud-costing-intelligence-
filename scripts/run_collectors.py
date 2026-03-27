# scripts/run_collectors.py
import time
from src.cloudwatch_collector import fetch_ec2_cpu, fetch_rds_cpu

def main():
    while True:
        try:
            # Replace with your actual instance IDs
            fetch_ec2_cpu("i-123456")
            fetch_rds_cpu("db-123456")
        except Exception as e:
            print(f"Error running collectors: {e}")
        time.sleep(300)  # wait 5 minutes

if __name__ == "__main__":
    main()
