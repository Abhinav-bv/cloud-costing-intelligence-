import boto3
from botocore.exceptions import ClientError

def terminate_or_stop_resource(instance_id, action="STOP"):
    """
    Connects to AWS and executes a cost-saving action.
    action: "STOP" (pauses billing) or "TERMINATE" (deletes the server)
    """
    # 1. Initialize the EC2 'Resource' (Higher level than 'client')
    ec2 = boto3.resource('ec2', region_name='us-east-1') # Use your region
    instance = ec2.Instance(instance_id)

    try:
        if action == "STOP":
            print(f"--- 🚨 Initiating STOP for {instance_id} ---")
            instance.stop()
            print(f"✅ Status: Stop command sent successfully.")
        
        elif action == "TERMINATE":
            print(f"--- ⚠️ Initiating TERMINATION for {instance_id} ---")
            instance.terminate()
            print(f"✅ Status: Termination command sent.")

    except ClientError as e:
        # This catches errors like "Instance not found" or "No Permissions"
        print(f"❌ AWS Error: {e.response['Error']['Message']}")

# --- Testing the Real Action ---
if __name__ == "__main__":
    # Replace this with your ACTUAL instance ID from the AWS Console
    MY_INSTANCE_ID = "i-0123456789abcdef" 
    terminate_or_stop_resource(MY_INSTANCE_ID, action="STOP")

# Inside execute_cost_optimization
if not dry_run:
    # Logic to calculate hours left in the month
    hours_saved = 720 # assuming it stayed off for a month
    money_saved = hours_saved * 0.0116
    return money_saved    