import os
import sys
import time
import pandas as pd

# Add current folder to path for internal imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from model import CostAnomalyDetector
from actions import execute_cost_optimization

PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', '..'))
CSV_PATH = os.path.join(PROJECT_ROOT, 'ml_ready_data.csv')

def run_loop():
    # 1. Initialize and Train
    data = pd.read_csv(CSV_PATH)
    detector = CostAnomalyDetector()
    detector.train_model(data)
    
    print("\n🕵️ Monitoring Cloud Assets for Financial Anomalies...")
    
    # 2. Simulate "Live" Stream from the CSV
    for _, row in data.iterrows():
        prediction, score = detector.detect(pd.DataFrame([row]))
        
        # Logic: If AI says Anomaly (-1) AND CPU is very low (Zombie)
        if prediction == -1 and row['cpuutilization'] < 5:
            print(f"🚩 Found Zombie: {row['resource_id']}")
            execute_cost_optimization(row['resource_id'], score, dry_run=True)
            
        time.sleep(1) # Slow down so you can see it in the terminal

if __name__ == "__main__":
    run_loop()