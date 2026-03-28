# scripts/run_collectors.py
import time
from src.cloudwatch_collector import CloudWatchCollector

def main():
    collector = CloudWatchCollector()
    while True:
        try:
            # Collect EC2 metrics only (RDS not available)
            collector.collect_ec2_metrics("i-123456")
        except Exception as e:
            print(f"Error running collectors: {e}")
        time.sleep(300)

if __name__ == "__main__":
    main()
