import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os

class CostAnomalyDetector:
    def __init__(self, contamination=0.1):
        # contamination is the % of data we expect to be anomalies (Zombies)
        self.model = IsolationForest(contamination=contamination, random_state=42)
        # These columns match your ml_ready_data.csv exactly
        self.feature_cols = ['cpuutilization', 'networkin', 'networkout']
        
    def train_model(self, data):
        """Trains the AI on provided CSV data."""
        # Fill missing values with 0 so the model doesn't crash
        train_data = data[self.feature_cols].fillna(0)
        self.model.fit(train_data)
        print("✅ AI Model trained on Cloud Metrics.")

    def detect(self, current_row_df):
        """Returns -1 if anomaly, 1 if normal, and the score."""
        data_cleaned = current_row_df[self.feature_cols].fillna(0)
        prediction = self.model.predict(data_cleaned)
        score = self.model.decision_function(data_cleaned)
        return prediction[0], score[0]