import numpy as np
import pandas as pd

class CostAnomalyDetector:
    def __init__(self, contamination=0.05):
        self.contamination = contamination
        self.feature_column = 'cpuutilization'
        self.trained = False
        self.mean_ = 0.0
        self.std_ = 1.0

    def train_model(self, data):
        df = pd.DataFrame(data)
        if self.feature_column not in df.columns:
            raise ValueError(f'Missing required feature column: {self.feature_column}')

        values = pd.to_numeric(df[self.feature_column], errors='coerce').fillna(0.0)
        self.mean_ = float(values.mean())
        self.std_ = float(values.std(ddof=0)) if float(values.std(ddof=0)) != 0 else 1.0
        self.trained = True

    def detect(self, data):
        if not self.trained:
            raise RuntimeError('Model has not been trained')

        df = pd.DataFrame(data)
        if self.feature_column not in df.columns:
            raise ValueError(f'Missing required feature column: {self.feature_column}')

        values = pd.to_numeric(df[self.feature_column], errors='coerce').fillna(0.0)
        z_scores = (values - self.mean_) / self.std_
        anomaly_mask = (values < 5) | (values > 95) | (z_scores.abs() >= 3.0)

        predictions = np.where(anomaly_mask, -1, 1)
        confidence = np.clip(z_scores.abs() / 5.0, 0.0, 1.0)

        return predictions.tolist(), confidence.tolist()
