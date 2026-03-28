import json
from datetime import datetime
import boto3
from dotenv import load_dotenv
import os

load_dotenv('../.env')

# ── Real AWS Pricing Rates (us-east-1) ──────────────────────────────
EC2_HOURLY_RATE = 0.0116       # t3.micro per hour
LAMBDA_PER_INVOCATION = 0.0000002  # per invocation
LAMBDA_PER_GB_SECOND = 0.0000166125
CLOUDWATCH_PER_METRIC = 0.30   # per custom metric per month

# ── Your Real Resource IDs ───────────────────────────────────────────
EC2_INSTANCE_ID = os.getenv('EC2_INSTANCE_ID', 'i-0f5e312cdb1ea9b00')
LAMBDA_FUNCTION = 'hackathon-loop-function'

# ── Simulate Before/After Scenarios ─────────────────────────────────

def calculate_before_costs():
    """
    BEFORE optimization:
    - EC2 running 24/7 doing nothing (idle)
    - Lambda invoked 1000 times (runaway)
    - No monitoring or cleanup
    """
    # EC2 idle 24/7 for a month
    ec2_hours = 24 * 30  # 720 hours/month
    ec2_cost = ec2_hours * EC2_HOURLY_RATE

    # Runaway Lambda - 10000 invocations
    lambda_invocations = 10000
    lambda_cost = lambda_invocations * LAMBDA_PER_INVOCATION

    # CloudWatch metrics
    cloudwatch_cost = 3 * CLOUDWATCH_PER_METRIC

    total = ec2_cost + lambda_cost + cloudwatch_cost

    return {
        'scenario': 'BEFORE Optimization',
        'resources': {
            'EC2 (idle 24/7)': {
                'hours': ec2_hours,
                'rate': f'${EC2_HOURLY_RATE}/hour',
                'cost': round(ec2_cost, 4)
            },
            'Lambda (runaway)': {
                'invocations': lambda_invocations,
                'rate': f'${LAMBDA_PER_INVOCATION}/invocation',
                'cost': round(lambda_cost, 4)
            },
            'CloudWatch (3 metrics)': {
                'metrics': 3,
                'rate': f'${CLOUDWATCH_PER_METRIC}/metric/month',
                'cost': round(cloudwatch_cost, 4)
            }
        },
        'total_monthly_cost': round(total, 4)
    }


def calculate_after_costs():
    """
    AFTER optimization:
    - EC2 stopped when idle (only runs 2hrs/day)
    - Lambda invocations controlled (max 100)
    - Monitoring in place
    """
    # EC2 only runs 2 hours/day after optimization
    ec2_hours = 2 * 30  # 60 hours/month
    ec2_cost = ec2_hours * EC2_HOURLY_RATE

    # Lambda controlled - only 100 invocations
    lambda_invocations = 100
    lambda_cost = lambda_invocations * LAMBDA_PER_INVOCATION

    # CloudWatch metrics (same)
    cloudwatch_cost = 3 * CLOUDWATCH_PER_METRIC

    total = ec2_cost + lambda_cost + cloudwatch_cost

    return {
        'scenario': 'AFTER Optimization',
        'resources': {
            'EC2 (stopped when idle)': {
                'hours': ec2_hours,
                'rate': f'${EC2_HOURLY_RATE}/hour',
                'cost': round(ec2_cost, 4)
            },
            'Lambda (controlled)': {
                'invocations': lambda_invocations,
                'rate': f'${LAMBDA_PER_INVOCATION}/invocation',
                'cost': round(lambda_cost, 4)
            },
            'CloudWatch (3 metrics)': {
                'metrics': 3,
                'rate': f'${CLOUDWATCH_PER_METRIC}/metric/month',
                'cost': round(cloudwatch_cost, 4)
            }
        },
        'total_monthly_cost': round(total, 4)
    }


def generate_cost_report():
    """Generate full before/after cost analysis report"""
    
    before = calculate_before_costs()
    after = calculate_after_costs()
    
    savings = before['total_monthly_cost'] - after['total_monthly_cost']
    savings_percent = (savings / before['total_monthly_cost']) * 100

    report = {
        'generated_at': str(datetime.utcnow()),
        'currency': 'USD',
        'period': 'Monthly',
        'before': before,
        'after': after,
        'savings': {
            'monthly_savings': round(savings, 4),
            'annual_savings': round(savings * 12, 4),
            'percentage_reduction': round(savings_percent, 2)
        }
    }

    # Save to JSON
    with open('cost_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n" + "="*50)
    print("💰 CLOUD COST ANALYSIS REPORT")
    print("="*50)
    print(f"\n📊 BEFORE Optimization:")
    print(f"   EC2 (idle 24/7):      ${before['resources']['EC2 (idle 24/7)']['cost']}/month")
    print(f"   Lambda (runaway):     ${before['resources']['Lambda (runaway)']['cost']}/month")
    print(f"   CloudWatch:           ${before['resources']['CloudWatch (3 metrics)']['cost']}/month")
    print(f"   TOTAL:                ${before['total_monthly_cost']}/month")
    
    print(f"\n✅ AFTER Optimization:")
    print(f"   EC2 (stopped idle):   ${after['resources']['EC2 (stopped when idle)']['cost']}/month")
    print(f"   Lambda (controlled):  ${after['resources']['Lambda (controlled)']['cost']}/month")
    print(f"   CloudWatch:           ${after['resources']['CloudWatch (3 metrics)']['cost']}/month")
    print(f"   TOTAL:                ${after['total_monthly_cost']}/month")
    
    print(f"\n💵 SAVINGS:")
    print(f"   Monthly savings:      ${report['savings']['monthly_savings']}")
    print(f"   Annual savings:       ${report['savings']['annual_savings']}")
    print(f"   Cost reduction:       {report['savings']['percentage_reduction']}%")
    print("="*50)
    print("\n✅ Full report saved to cost_report.json")

    # Upload to S3
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_DEFAULT_REGION')
    )
    
    s3.upload_file('cost_report.json', 'hackathon-cost-reports-457563661765-us-east-1-an', 'cost_report.json')
    print("✅ Uploaded cost_report.json to S3!")

    return report

if __name__ == "__main__":
    generate_cost_report()