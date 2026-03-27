# AWS Integration Guide

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and fill in your AWS RDS details:
```bash
cp .env.example .env
```

```env
AWS_RDS_HOST=your-rds-instance.region.rds.amazonaws.com
AWS_RDS_PORT=5432
AWS_RDS_DB_NAME=cloud_costing
AWS_RDS_USER=admin
AWS_RDS_PASSWORD=your_password
AWS_RDS_ENGINE=postgres  # or mysql, mariadb

# Database mode
SYNC_MODE=both  # local, aws, or both
```

## Usage Examples

### Load Sample Data

#### Local SQLite Only
```bash
python scripts/seed_db.py --local
```

#### AWS RDS Only
```bash
python scripts/seed_db.py --aws
```

#### Both (Default)
```bash
python scripts/seed_db.py --both
```

#### Load JSON Data from Local File
```bash
python scripts/load_aws_data.py --local-file data/sample_data.json
```

#### Load JSON Data from AWS S3
```bash
python scripts/load_aws_data.py --s3-bucket my-bucket --s3-key metrics/data.json
```

### Sync Local SQLite to AWS RDS
```bash
python scripts/seed_db.py --sync
```

### Collect Metrics
```python
# Uses configuration from .env
SYNC_MODE=both means it writes to both databases
```

```bash
python src/collect_metrics.py
```

## Database Architecture

### SQLite (Local)
- `resources` - Cloud provider resources
- `metrics` - Time-series metric data
- `aws_metrics` - Legacy CloudWatch metrics

### AWS RDS (Cloud)
- `resources` - Same structure as SQLite
- `metrics` - Same structure as SQLite
- Full relational database with foreign keys

## JSON Data Format

```json
{
  "resources": [
    {
      "resource_id": "res-001",
      "cloud_provider": "AWS",
      "instance_type": "t3.medium",
      "region": "us-east-1"
    }
  ],
  "metrics": [
    {
      "resource_id": "res-001",
      "metric_name": "cpu_usage",
      "metric_value": 45.5,
      "timestamp": "2026-03-28T10:00:00"
    }
  ]
}
```

## Integration Points

### Config Module (`config.py`)
- Centralized configuration management
- Supports multiple database engines
- Environment variable overrides

### AWS Utils Module (`aws_utils.py`)
- `RDSConnection` - Connection management
- `create_rds_tables()` - Schema initialization
- `import_json_to_rds()` - Bulk data import
- `sync_sqlite_to_rds()` - Bidirectional sync

### Data Loader (`scripts/load_aws_data.py`)
- Load from local JSON files
- Load from AWS S3
- Support for multiple database targets

## Supported Databases

- **PostgreSQL** - Default, recommended
- **MySQL** - Community edition
- **MariaDB** - Maria's fork of MySQL
- **SQLite** - Local development

## Next Steps

1. Set up AWS RDS instance (https://aws.amazon.com/rds/)
2. Configure `.env` with RDS credentials
3. Run `python scripts/seed_db.py --aws` to create tables
4. Load your data with `scripts/load_aws_data.py`
5. Update collection logic in `src/collect_metrics.py` to pull from CloudWatch

## Troubleshooting

### Can't connect to RDS
- Check security group allows your IP on port 5432 (PostgreSQL) or 3306 (MySQL)
- Verify credentials in `.env`
- Test: `python -c "from aws_utils import RDSConnection; RDSConnection().connect()"`

### JSON import fails
- Verify JSON format matches `data/sample_data.json`
- Check file encoding is UTF-8
- Ensure resource_ids exist before inserting metrics

### Sync issues
- Run `python scripts/seed_db.py --local` first
- Then run `python scripts/seed_db.py --sync`
