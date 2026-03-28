#!/usr/bin/env python3
"""
QUICK START GUIDE - Run this to verify everything works!
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n{'='*60}")
    print(f"🔷 {description}")
    print(f"{'='*60}")
    print(f"Running: {cmd}\n")
    
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode == 0:
        print(f"\n✅ {description} - SUCCESS")
        return True
    else:
        print(f"\n❌ {description} - FAILED")
        return False

def main():
    print("\n" + "="*60)
    print("🚀 CLOUD COST INTELLIGENCE - DATA PIPELINE SETUP")
    print("="*60)
    
    # Step 1: Initialize database
    success = run_command(
        "python scripts/seed_db.py",
        "Initialize SQLite Database"
    )
    if not success:
        print("❌ Failed to initialize database. Check if boto3 and psycopg2 are installed.")
        sys.exit(1)
    
    # Step 2: Test configuration
    print(f"\n{'='*60}")
    print("🔷 Verify Configuration")
    print(f"{'='*60}\n")
    
    try:
        from config import (
            LOCAL_DB_CONFIG, AWS_REGION, MONITORED_RESOURCES,
            OUTPUT_DIR, ML_READY_CSV
        )
        
        print("✅ Configuration loaded:")
        print(f"   - Database: {LOCAL_DB_CONFIG['file']}")
        print(f"   - AWS Region: {AWS_REGION}")
        print(f"   - Resources: {', '.join(MONITORED_RESOURCES)}")
        print(f"   - Output: {OUTPUT_DIR}/{ML_READY_CSV}")
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Step 3: Display next steps
    print(f"\n{'='*60}")
    print("📋 NEXT STEPS")
    print(f"{'='*60}")
    
    steps = """
1. UPDATE .env FILE with your AWS resources:
   
   MONITORED_RESOURCES=i-0123456789abcdef0,rds-db-prod-01,lambda-func-01
   AWS_REGION=us-east-1
   AWS_PROFILE=default

2. VERIFY AWS CREDENTIALS:
   
   aws sts get-caller-identity
   
   Should show your AWS account info.

3. RUN DATA COLLECTION PIPELINE:
   
   # Collect CloudWatch metrics
   python scripts/run_data_pipeline.py --collect-cloudwatch
   
   # Collect billing data
   python scripts/run_data_pipeline.py --collect-billing
   
   # Clean data (prepare for ML)
   python scripts/run_data_pipeline.py --clean-data
   
   # Run EVERYTHING
   python scripts/run_data_pipeline.py --full

4. CHECK OUTPUTS:
   
   - SQLite: metrics.db (contains raw metrics, billing)
   - CSV: output/ml_ready_data.csv (ready for ML model)
   - Logs: pipeline.log (detailed execution logs)

5. PASS TO ML ENGINEER:
   
   Hand over: output/ml_ready_data.csv
   
   This has:
   ✅ Clean, normalized metrics
   ✅ One row per resource per hour
   ✅ Metrics as columns (cpu, memory, network, etc.)
   ✅ No missing values
   ✅ Ready for Prophet/Isolation Forest
    """
    
    print(steps)
    
    print(f"\n{'='*60}")
    print("✅ SETUP COMPLETE!")
    print(f"{'='*60}")
    print("\nYour data pipeline is ready. Start with:\n")
    print("   python scripts/run_data_pipeline.py --full\n")

if __name__ == "__main__":
    main()
