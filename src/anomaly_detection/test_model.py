import pandas as pd
import numpy as np
from model import CostAnomalyDetector

def generate_fake_data():
    # 1. Generate 100 'Normal' points (CPU between 10% and 25%)
    normal_cpu = np.random.uniform(10, 25, 100)
    df = pd.DataFrame({'cpu_usage': normal_cpu})

    # 2. Inject Villain #1: The "Runaway Script" (Huge Spike)
    df.loc[101] = [98.5] 

    # 3. Inject Villain #2: The "Zombie Server" (Stuck at ~0%)
    df.loc[102] = [0.2]

    return df

def run_test():
    # Load data
    data = generate_fake_data()
    
    # Initialize your detector (% sensitivity)
    detector = CostAnomalyDetector(contamination=0.02)
    
    # Train on the first 100 "normal" points
    detector.train_model(data.iloc[:100])
    
    # Test on the whole set (including the anomalies)
    predictions, scores = detector.detect(data)
    
    data['is_anomaly'] = predictions
    data['confidence'] = scores

    # 4. Filter to see what the Brain caught
    anomalies = data[data['is_anomaly'] == -1]
    
    print("-" * 30)
    print(f"TEST COMPLETE: Found {len(anomalies)} anomalies.")
    print("-" * 30)
    print(anomalies)

if __name__ == "__main__":
    run_test()