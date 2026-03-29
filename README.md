# ☁️ Cloud Cost Intelligence System

> A real-time cloud cost intelligence system connected to AWS that monitors live resource usage, detects genuine cost anomalies using ML, and automatically executes optimizations via cloud APIs.

Built for **Manipal Institute of Technology Bengaluru Hackathon 2026**

---

## 🏗️ System Architecture

```
AWS Cloud Infrastructure (EC2, Lambda, CloudWatch, S3)
                    ↓
        Data Pipeline & Monitoring
        (CloudWatch Collector → SQLite → Data Cleaner)
                    ↓
          ML Anomaly Detection
          (Isolation Forest Model)
                    ↓
        Real-time React Dashboard
        (Live metrics, anomalies, cost savings)
```

---

## 👥 Team Roles

| Role | Responsibility |
|---|---|
| ☁️ Cloud Infrastructure | AWS setup, EC2/Lambda provisioning, anomaly simulation, cost analysis |
| 🔧 Data Pipeline | CloudWatch collection, data cleaning, ML-ready CSV export |
| 🤖 ML Model | Isolation Forest anomaly detection, anomaly classification |
| 📊 Dashboard | Real-time React frontend, metric visualization, cost display |

---

## ☁️ Cloud Infrastructure

### AWS Resources
| Resource | Details |
|---|---|
| EC2 Instance | `i-0f5e312cdb1ea9b00` — t3.micro, Amazon Linux, us-east-1 |
| Lambda Function | `hackathon-loop-function` — Python 3.12 |
| CloudWatch Namespace | `HackathonMetrics` — us-east-1 |
| S3 Bucket | `hackathon-cost-reports-457563661765-us-east-1-an` |

### 3 Anomaly Simulations

| Script | CloudWatch Metric | Anomaly Simulated |
|---|---|---|
| `cloud-env/simulate/idle_server.py` | `IdleCPU` | EC2 server idle at 2% CPU — wasting money |
| `cloud-env/simulate/spike.py` | `NetworkTraffic` | Traffic spike from 10 → 950 requests |
| `cloud-env/simulate/loop.py` | `LambdaInvocations` | 50 rapid Lambda invocations — runaway function |

### Cost Analysis Results
| | Monthly Cost |
|---|---|
| ❌ Before Optimization | $9.254 |
| ✅ After Optimization | $1.596 |
| 💰 Monthly Savings | $7.658 |
| 📅 Annual Savings | $91.896 |
| 📉 Cost Reduction | **82.75%** |

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Cloud Platform | AWS Free Tier (us-east-1) |
| Cloud Services | EC2, Lambda, CloudWatch, S3, IAM |
| Language | Python 3.11+ |
| AWS SDK | boto3 |
| Database | SQLite |
| Data Processing | pandas, numpy |
| ML Model | Isolation Forest |
| Frontend | React + Vite |
| Styling | CSS |
| Version Control | Git + GitHub |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js v20+
- AWS Account (Free Tier)
- Git

### 1. Clone the repository
```bash
git clone https://github.com/Abhinav-bv/cloud-costing-intelligence-
cd cloud-costing-intelligence-
```

### 2. Set up environment variables
Copy `.env.example` to `.env` and fill in your AWS credentials:
```bash
cp .env.example .env
```

```
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_DEFAULT_REGION=us-east-1
EC2_INSTANCE_ID=your_ec2_instance_id
```

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize the database
```bash
python scripts/seed_db.py
```

### 5. Run the anomaly simulations
Open 3 separate terminals:
```bash
# Terminal 1 — Idle server (runs continuously)
cd cloud-env/simulate
python idle_server.py

# Terminal 2 — Traffic spike
cd cloud-env/simulate
python spike.py

# Terminal 3 — Lambda loop
cd cloud-env/simulate
python loop.py
```

### 6. Collect metrics & generate cost report
```bash
cd cloud-env/telemetry
python collect_metrics.py
python cost_analysis.py
```

### 7. Run the data pipeline
```bash
python scripts/run_data_pipeline.py --full
```

### 8. Start the frontend dashboard
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173/** in your browser.

---

## 📁 Project Structure

```
cloud-costing-intelligence/
├── cloud-env/                        # ☁️ Cloud Infrastructure
│   ├── simulate/
│   │   ├── idle_server.py            # Idle server anomaly (CPU: 2%)
│   │   ├── spike.py                  # Traffic spike anomaly (10→950)
│   │   └── loop.py                   # Lambda loop anomaly (50 invocations)
│   ├── telemetry/
│   │   ├── collect_metrics.py        # CloudWatch metrics collector
│   │   └── cost_analysis.py          # Before/after cost report
│   └── setup/
│       └── test_connection.py        # AWS connection verification
│
├── scripts/                          # 🔧 Data Pipeline
│   ├── run_data_pipeline.py          # Main pipeline orchestrator
│   ├── watch_s3_and_run.py           # Auto S3 watcher
│   └── seed_db.py                    # Database schema setup
│
├── src/                              # 🔧 Core Modules
│   ├── cloudwatch_collector.py       # CloudWatch metrics reader
│   ├── billing_collector.py          # Cost Explorer integration
│   ├── collect_metrics.py            # SQLite integration layer
│   ├── data_cleaner.py               # ML data preparation
│   └── anomaly_detection/
│       └── model.py                  # 🤖 Isolation Forest ML model
│
├── output/                           # Generated outputs
│   ├── ml_ready_data.csv             # Cleaned ML-ready dataset
│   ├── anomalies.json                # Detected anomalies
│   └── cost_report.json              # Cost analysis results
│
├── frontend/                         # 📊 React Dashboard
├── data/                             # Raw data storage
├── docs/                             # Documentation
├── tests/                            # Test suite
│
├── config.py                         # Centralized configuration
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment variables template
└── .gitignore                        # Git ignore rules
```

---

## 📊 CloudWatch Metrics

| Metric | Namespace | Unit | Description |
|---|---|---|---|
| `IdleCPU` | HackathonMetrics | Percent | EC2 CPU at 2% — idle anomaly |
| `NetworkTraffic` | HackathonMetrics | Count | Traffic 10→950 — spike anomaly |
| `LambdaInvocations` | HackathonMetrics | Count | 50 rapid calls — loop anomaly |

**Region:** `us-east-1` | **Account ID:** `457563661765`

---

## 🤖 ML Anomaly Detection

Uses **Isolation Forest** to detect 3 anomaly types from `ml_ready_data.csv`:

| Anomaly | Signal | Real World Cause |
|---|---|---|
| Idle Server | CPU stuck at 2% | Forgotten server running 24/7 |
| Traffic Spike | Requests jump 95x | Viral moment or DDoS attack |
| Runaway Lambda | 50 invocations in 20s | Bug causing recursive calls |

Results exported to `output/anomalies.json`

---

## 🔧 Data Pipeline Commands

```bash
# Run full pipeline
python scripts/run_data_pipeline.py --full

# Collect CloudWatch metrics only
python scripts/run_data_pipeline.py --collect-cloudwatch

# Collect billing data only
python scripts/run_data_pipeline.py --collect-billing

# Clean and process data only
python scripts/run_data_pipeline.py --clean-data

# Watch S3 and auto-run pipeline
python scripts/watch_s3_and_run.py
```

---

## 💰 AWS Free Tier Usage

| Service | Free Tier Limit | Used | Cost |
|---|---|---|---|
| EC2 (t3.micro) | 750 hrs/month | ~12 hrs | $0.00 |
| Lambda | 1M invocations/month | ~100 | $0.00 |
| CloudWatch Metrics | 10 custom metrics | 3 | $0.00 |
| S3 Storage | 5GB/month | <1MB | $0.00 |
| **Total** | | | **$0.00** |

---

## 🔐 Security

- **IAM User** — dedicated `hackathon-user` with minimal permissions
- **No root credentials** in code — all via IAM access keys
- **`.env` file** — gitignored, never committed to GitHub
- **`.pem` key file** — gitignored, stored locally only
- **S3 bucket** — private access only

---

## 📋 Problem Statement

> *"Build a real cloud cost intelligence system connected to an actual AWS/GCP free tier account that monitors live resource usage, detects genuine cost anomalies using ML, and automatically executes optimizations via cloud APIs."*
>
> — Manipal Institute of Technology Bengaluru

### How we met every requirement:

| Requirement | What we built |
|---|---|
| Real AWS account | ✅ Free tier, us-east-1 |
| Live resource usage | ✅ EC2 + Lambda running now |
| Cloud SDKs | ✅ boto3 throughout |
| Time-series store | ✅ CloudWatch + SQLite |
| ML anomaly detection | ✅ Isolation Forest |
| Automatic optimizations | ✅ Cloud API interventions |
| Real-time dashboard | ✅ React + Vite frontend |
| Before/after impact | ✅ 82.75% cost reduction |

---

## 📄 License

Built for educational purposes at MIT Bengaluru Hackathon 2026.
