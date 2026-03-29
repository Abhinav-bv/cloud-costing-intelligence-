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
    # Determine unique active resource ids from the CSV
    unique_resources = set(df['resource_id'].unique()) if 'resource_id' in df.columns else set()

    total_saved = 0.0
    history = []
    stopped_resources = set()
    if os.path.exists(LOG_FILE):
        h_df = pd.read_csv(LOG_FILE)
        # Sum savings if column exists
        if 'savings_usd' in h_df.columns:
            # coerce to numeric and ignore NaNs
            total_saved = float(pd.to_numeric(h_df['savings_usd'], errors='coerce').fillna(0).sum())

        # Build history (last 10)
        history = h_df.tail(10).to_dict(orient='records')

        # If the log contains action indicators for stopped resources, exclude them
        action_cols = [c for c in h_df.columns if c.lower() in ('action_type', 'action', 'actiontype')]
        if action_cols:
            # look for keywords indicating a stop
            for col in action_cols:
                stopped = h_df[h_df[col].astype(str).str.lower().str.contains('stop')]
                if 'resource_id' in stopped.columns:
                    stopped_resources.update(stopped['resource_id'].astype(str).tolist())

    # active resources are those in the CSV minus any stopped resources recorded in the log
    active_resources = unique_resources - stopped_resources
    active_count = len(active_resources)

    return {
        'total_savings': round(total_saved, 2),
        'current_run_rate': round(active_count * HOURLY_RATE, 4),
        'active_assets': int(active_count),
        'history': history,
    }
