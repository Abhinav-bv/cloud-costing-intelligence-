import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib  # Standard library for saving ML models
import os

class CostAnomalyDetector:
    def __init__(self, contamination=0.05):
        self.contamination = contamination
        self.model = IsolationForest(contamination=contamination, random_state=42)
        
    def train_model(self, data):
        self.model.fit(data)
        print("Model trained successfully.")

    def detect(self, current_data):
        # Ensure input is a DataFrame/2D array
        prediction = self.model.predict(current_data)
        scores = self.model.decision_function(current_data)
        return prediction, scores

    def save_model(self, filename='trained_cost_model.pkl'):
        """Saves the trained model to a file."""
        joblib.dump(self, filename)
        print(f"Model saved to {filename}")

    @staticmethod
    def load_model(filename='trained_cost_model.pkl'):
        """Loads a model from a file."""
        if os.path.exists(filename):
            print(f"Loading model from {filename}...")
            return joblib.load(filename)
        else:
            print("No saved model found. Please train a new one.")
            return None

# --- Updated Integration Example ---
if __name__ == "__main__":
    # 1. Create Data
    data = pd.DataFrame({
        'cpu_usage': [12.5, 14.2, 11.8, 15.0, 13.2, 12.1, 95.0, 14.5]
    })

    # 2. Train and Save
    detector = CostAnomalyDetector(contamination=0.1)
    detector.train_model(data)
    detector.save_model() # Saves the 'detector' object to your folder

    # 3. Demonstrate Loading (This is what you'll do in your Main Controller)
    print("\n--- Testing Load Logic ---")
    new_detector = CostAnomalyDetector.load_model()
    
    if new_detector:
        predictions, confidence = new_detector.detect(data)
        print("Detection using loaded model successful!")
        print(predictions)