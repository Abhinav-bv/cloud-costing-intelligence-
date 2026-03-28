"""
scripts/run_data_pipeline.py
Main orchestration script for the data collection and cleaning pipeline.

Usage:
    python scripts/run_data_pipeline.py --collect-cloudwatch
    python scripts/run_data_pipeline.py --collect-billing
    python scripts/run_data_pipeline.py --clean-data
    python scripts/run_data_pipeline.py --full  # All steps
"""

import argparse
import logging
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import MONITORED_RESOURCES, LOG_LEVEL, LOG_FILE, OUTPUT_DIR
from src.cloudwatch_collector import CloudWatchCollector
from src.billing_collector import BillingDataPipeline
from src.data_cleaner import DataCleaner

# ============================================================================
# LOGGING SETUP
# ============================================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# ============================================================================
# PIPELINE FUNCTIONS
# ============================================================================

def collect_cloudwatch_metrics(resources: list = None):
    """
    Collect metrics from AWS CloudWatch for all resource types.
    
    Args:
        resources: List of resource IDs to monitor (uses config default if None)
    """
    logger.info("=" * 60)
    logger.info("COLLECT: CloudWatch Metrics")
    logger.info("=" * 60)
    
    if resources is None:
        resources = MONITORED_RESOURCES
    
    collector = CloudWatchCollector()
    
    # Map resource patterns to collector methods
    for resource_id in resources:
        logger.info(f"\nCollecting metrics for: {resource_id}")
        
        # Detect resource type from ID pattern
        if resource_id.startswith("i-"):
            logger.info(f"  -> Detected as EC2 instance")
            collector.collect_ec2_metrics(resource_id)
        
        elif resource_id.startswith("arn:aws:lambda:") or resource_id.startswith("lambda-"):
            logger.info(f"  -> Detected as Lambda function")
            collector.collect_lambda_metrics(resource_id)

        else:
            logger.warning(f"  WARNING: Unknown resource type: {resource_id}")
    logger.info("\nCloudWatch collection complete!\n")


def collect_billing_data():
    """Collect cost and usage data from AWS Cost Explorer"""
    logger.info("=" * 60)
    logger.info("COLLECT: Billing Data")
    logger.info("=" * 60)
    
    pipeline = BillingDataPipeline()
    
    # Collect costs by service
    logger.info("\nCollecting costs by service (past 7 days)...")
    service_costs = pipeline.collect_costs_by_service(days_back=7)
    
    logger.info(f"\nTop services by cost:")
    for service, cost in sorted(service_costs.items(), key=lambda x: x[1], reverse=True)[:10]:
        logger.info(f"  • {service}: ${cost:.2f}")
    
    # Collect costs by resource
    logger.info("\nCollecting costs by resource (past 7 days)...")
    resource_costs = pipeline.collect_costs_by_resource(days_back=7)
    
    if resource_costs:
        logger.info(f"\nTop resources by cost:")
        for resource, cost in sorted(resource_costs.items(), key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"  • {resource}: ${cost:.2f}")
    
    logger.info("\nBilling collection complete!\n")


def clean_and_prepare_data():
    """
    Clean metrics and prepare ML-ready dataset.
    
    Steps:
    1. Load raw metrics from SQLite
    2. Clean and normalize
    3. Aggregate to hourly
    4. Pivot metrics to columns
    5. Export to CSV for ML model
    """
    logger.info("=" * 60)
    logger.info("CLEAN: Prepare ML Dataset")
    logger.info("=" * 60)
    
    cleaner = DataCleaner()
    ml_ready_df = cleaner.prepare_ml_dataset()
    
    if not ml_ready_df.empty:
        logger.info("\n" + cleaner.generate_summary(ml_ready_df))
    
    logger.info("\nData cleaning complete!\n")


def run_full_pipeline():
    """Execute complete pipeline: collect → collect billing → clean"""
    logger.info("\n" + "=" * 60)
    logger.info("RUNNING FULL DATA PIPELINE")
    logger.info("=" * 60)
    
    try:
        # Step 1: Collect CloudWatch metrics
        collect_cloudwatch_metrics()
        
        # Step 2: Collect billing data
        collect_billing_data()
        
        # Step 3: Clean and prepare data for ML
        clean_and_prepare_data()
        
        logger.info("\n" + "=" * 60)
        logger.info("FULL PIPELINE COMPLETE - All steps succeeded!")
        logger.info("=" * 60)
        logger.info(f"\nOutput files saved to: {OUTPUT_DIR}/")
        logger.info(f"ML-ready dataset: ml_ready_data.csv")
        logger.info(f"Logs: {LOG_FILE}\n")
        
        return True
        
    except Exception as e:
        logger.error("\n" + "=" * 60)
        logger.error(f"PIPELINE FAILED: {e}")
        logger.error("=" * 60 + "\n")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Data Pipeline: Collect metrics, billing, and prepare ML dataset"
    )
    
    parser.add_argument(
        "--collect-cloudwatch",
        action="store_true",
        help="Collect metric data from AWS CloudWatch"
    )
    
    parser.add_argument(
        "--collect-billing",
        action="store_true",
        help="Collect cost data from AWS Cost Explorer"
    )
    
    parser.add_argument(
        "--clean-data",
        action="store_true",
        help="Clean metrics and prepare ML-ready dataset"
    )
    
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run complete pipeline (all steps)"
    )
    
    parser.add_argument(
        "--resources",
        type=str,
        help="Comma-separated list of resource IDs to monitor"
    )
    
    args = parser.parse_args()
    
    # Parse resources if provided
    resources = None
    if args.resources:
        resources = [r.strip() for r in args.resources.split(",")]
    
    # Execute requested operations
    if args.full:
        success = run_full_pipeline()
    else:
        success = True
        
        if args.collect_cloudwatch:
            collect_cloudwatch_metrics(resources)
        
        if args.collect_billing:
            collect_billing_data()
        
        if args.clean_data:
            clean_and_prepare_data()
        
        # If no arguments provided, show help
        if not (args.collect_cloudwatch or args.collect_billing or args.clean_data):
            parser.print_help()
            return
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
