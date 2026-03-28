import boto3
from cost_tracker import log_intervention

def execute_cost_optimization(resource_id, anomaly_score, dry_run=True):
    """Stops an instance if it is identified as a waste of money."""
    # Note: For Lambda ARNs, we might log it; for i-xxxx IDs, we stop them.
    is_ec2 = resource_id.startswith('i-')
    
    try:
        if is_ec2:
            ec2 = boto3.client('ec2', region_name='us-east-1')
            print(f"🤖 AI ACTION: Stopping Zombie EC2 {resource_id} (Score: {anomaly_score})")
            ec2.stop_instances(InstanceIds=[resource_id], DryRun=dry_run)
        else:
            print(f"🤖 AI ADVISORY: Flagging non-EC2 resource {resource_id} for review.")

        # Always log to our internal database for the React Dashboard
        log_intervention(resource_id, "ISOLATE/STOP", anomaly_score)
        return True
    except Exception as e:
        # If it's a dry run, Boto3 throws an error - we treat that as success for the demo
        if 'DryRunOperation' in str(e):
            log_intervention(resource_id, "DRY_RUN_STOP", anomaly_score)
            return True
        print(f"❌ Error performing action: {e}")
        return False