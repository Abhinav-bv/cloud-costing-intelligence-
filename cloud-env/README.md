\# Cloud Environment Setup



\## What this does

Provisions real AWS resources and simulates cost anomalies

for the ML and dashboard teammates to consume.



\## Setup

1\. Install dependencies:

&#x20;  pip install boto3 requests python-dotenv



2\. Create a .env file in this folder:

&#x20;  AWS\_ACCESS\_KEY\_ID=your\_key

&#x20;  AWS\_SECRET\_ACCESS\_KEY=your\_secret

&#x20;  AWS\_DEFAULT\_REGION=us-east-1



\## Running the simulations

Run each script from the simulate/ folder:



\- Idle server anomaly:

&#x20; python simulate/idle\_server.py



\- Traffic spike anomaly:

&#x20; python simulate/spike.py



\- Lambda loop anomaly:

&#x20; python simulate/loop.py



\## Collecting metrics

Run this to get all data as JSON:

&#x20; python telemetry/collect\_metrics.py



Output: telemetry/metrics\_output.json



\## CloudWatch Details

\- Namespace: HackathonMetrics

\- Metrics: IdleCPU, NetworkTraffic, LambdaInvocations

\- Region: us-east-1

