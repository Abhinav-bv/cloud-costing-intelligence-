import os
import sys
import time
import pandas as pd

# --- PATH FIX: Ensures Python finds the 'anomaly_detection' folder ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from anomaly_detection.model import CostAnomalyDetector
from anomaly_detection.actions import execute_cost_optimization

# --- CSV PATH FIX: Finds the CSV in the root folder ---
CSV_PATH = os.path.join(BASE_DIR, '..', 'ml_ready_data.csv')

def run_system():
    if not os.path.exists(CSV_PATH):
        print(f"❌ Error: {CSV_PATH} not found. Move it to the root folder!")
        return

    # 1. Load data and train
    data = pd.read_csv(CSV_PATH)
    detector = CostAnomalyDetector(contamination=0.1)
    detector.train_model(data)
    
    print("\n🚀 Starting Autonomous Monitoring Loop...")
    
    # 2. Iterate through instances in the CSV
    for index, row in data.iterrows():
        instance_id = row['resource_id']
        current_df = pd.DataFrame([row])
        
        prediction, score = detector.detect(current_df)
        
        # Logic: If anomaly (-1) AND low CPU usage (Zombie check)
        if prediction[0] == -1 and row['cpuutilization'] < 10:
            print(f"🚨 ALERT: Zombie Asset Detected: {instance_id}")
            # dry_run=True means it won't actually stop your AWS instance yet
            execute_cost_optimization(instance_id, score[0], dry_run=True)
            
        time.sleep(1) # For demo visibility

if __name__ == "__main__":
    run_system()