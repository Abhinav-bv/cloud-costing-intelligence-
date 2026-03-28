import os
from datetime import datetime

import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', '..'))
LOG_FILE = os.path.join(PROJECT_ROOT, 'intervention_history.csv')
HOURLY_RATE = 0.0116


def ensure_log_file():
    if not os.path.exists(LOG_FILE):
        pd.DataFrame(
            columns=['timestamp', 'resource_id', 'action_type', 'anomaly_score', 'savings_usd']
        ).to_csv(LOG_FILE, index=False)


def log_intervention(resource_id, action_type, anomaly_score, savings_usd=0.0):
    ensure_log_file()
    timestamp = datetime.utcnow().isoformat() + 'Z'
    entry = {
        'timestamp': timestamp,
        'resource_id': resource_id,
        'action_type': action_type,
        'anomaly_score': float(anomaly_score),
        'savings_usd': float(savings_usd),
    }
    history_df = pd.read_csv(LOG_FILE)
    history_df = pd.concat([history_df, pd.DataFrame([entry])], ignore_index=True)
    history_df.to_csv(LOG_FILE, index=False)
    return entry


def get_dashboard_stats(csv_path):
    df = pd.read_csv(csv_path)
    active_count = df['resource_id'].nunique() if 'resource_id' in df.columns else len(df)

    total_saved = 0.0
    history = []
    if os.path.exists(LOG_FILE):
        h_df = pd.read_csv(LOG_FILE)
        if 'savings_usd' in h_df.columns:
            total_saved = float(h_df['savings_usd'].sum())
        history = h_df.tail(10).to_dict(orient='records')

    return {
        'total_savings': round(total_saved, 2),
        'current_run_rate': round(active_count * HOURLY_RATE, 4),
        'active_assets': int(active_count),
        'history': history,
    }
