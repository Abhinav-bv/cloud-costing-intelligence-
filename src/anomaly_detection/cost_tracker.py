import pandas as pd
import os
from datetime import datetime

# Path to the files in the root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, '..', 'intervention_history.csv')
HOURLY_RATE = 0.0116  # Avg cost of a t2.micro

def log_intervention(resource_id, action, score):
    """Calculates potential savings and saves to history."""
    # Assume 30 days (720 hrs) of savings per 'Zombie' killed
    savings = round(HOURLY_RATE * 720, 2)
    
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "resource_id": resource_id,
        "action": action,
        "score": round(score, 4),
        "savings_usd": savings
    }
    
    df = pd.DataFrame([entry])
    df.to_csv(LOG_FILE, mode='a', index=False, header=not os.path.exists(LOG_FILE))

def get_dashboard_stats(csv_path):
    """Reads CSV and History to provide data for the React Dashboard."""
    df = pd.read_csv(csv_path)
    active_count = df['resource_id'].nunique()
    
    total_saved = 0
    history = []
    
    if os.path.exists(LOG_FILE):
        h_df = pd.read_csv(LOG_FILE)
        total_saved = h_df['savings_usd'].sum()
        history = h_df.tail(10).to_dict(orient='records')
        
    return {
        "total_savings": round(total_saved, 2),
        "current_run_rate": round(active_count * HOURLY_RATE, 4),
        "active_assets": active_count,
        "history": history
    }