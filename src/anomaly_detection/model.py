<<<<<<< HEAD
﻿import numpy as np
import pandas as pd

class CostAnomalyDetector:
    def __init__(self, contamination=0.05):
        self.contamination = contamination
        self.feature_column = 'cpuutilization'
        self.trained = False
        self.mean_ = 0.0
        self.std_ = 1.0

	"""
	src/anomaly_detection/model.py
	Anomaly detection utilities.

	Provides:
	- CostAnomalyDetector: simple train/detect API (legacy teammate interface)
	- AnomalyDetector: CSV -> anomalies.json output contract for pipeline integration
	"""

	from __future__ import annotations


from __future__ import annotations

import json
	import numpy as np
import math
from typing import Dict, List

	class CostAnomalyDetector:
		"""Simple z-score detector retained for compatibility."""

		def __init__(self, contamination: float = 0.05):
			self.contamination = contamination
			self.feature_column = "cpuutilization"
			self.trained = False
			self.mean_ = 0.0
			self.std_ = 1.0

		def train_model(self, data):
			df = pd.DataFrame(data)
			if self.feature_column not in df.columns:
				raise ValueError(f"Missing required feature column: {self.feature_column}")

			values = pd.to_numeric(df[self.feature_column], errors="coerce").fillna(0.0)
			self.mean_ = float(values.mean())
			std = float(values.std(ddof=0))
			self.std_ = std if std != 0 else 1.0
			self.trained = True

		def detect(self, data):
			if not self.trained:
				raise RuntimeError("Model has not been trained")

			df = pd.DataFrame(data)
			if self.feature_column not in df.columns:
				raise ValueError(f"Missing required feature column: {self.feature_column}")

			values = pd.to_numeric(df[self.feature_column], errors="coerce").fillna(0.0)
			z_scores = (values - self.mean_) / self.std_
			anomaly_mask = (values < 5) | (values > 95) | (z_scores.abs() >= 3.0)

			predictions = np.where(anomaly_mask, -1, 1)
			confidence = np.clip(z_scores.abs() / 5.0, 0.0, 1.0)
			return predictions.tolist(), confidence.tolist()


import pandas as pd
		"""Detect anomalies using robust z-score by resource and feature."""

		model_name = "robust_zscore_v1"
	"""Detect anomalies using robust z-score by resource and feature."""
		def _numeric_columns(self, df: pd.DataFrame) -> List[str]:
			skip = {"resource_id", "hour"}
			numeric_cols = [
				c for c in df.columns if c not in skip and pd.api.types.is_numeric_dtype(df[c])
			]
			return numeric_cols
			c for c in df.columns if c not in skip and pd.api.types.is_numeric_dtype(df[c])
		def _robust_stats(self, series: pd.Series) -> Dict[str, float]:
			clean = pd.to_numeric(series, errors="coerce").dropna()
			if clean.empty:
				return {"median": float("nan"), "mad": float("nan")}
		clean = pd.to_numeric(series, errors="coerce").dropna()
			median = float(clean.median())
			mad = float((clean - median).abs().median())
			return {"median": median, "mad": mad}
		median = float(clean.median())
		def _robust_z(self, value: float, median: float, mad: float) -> float:
			if math.isnan(value) or math.isnan(median) or math.isnan(mad) or mad == 0.0:
				return 0.0
			return abs(value - median) / (1.4826 * mad)
		if math.isnan(value) or math.isnan(median) or math.isnan(mad) or mad == 0.0:
		def detect_from_dataframe(self, df: pd.DataFrame, threshold: float = 3.0) -> List[Dict]:
			"""Return anomaly records from an ML-ready dataframe."""
			if df.empty:
				return []
		"""Return anomaly records from an ML-ready dataframe."""
			working = df.copy()
			if "resource_id" not in working.columns or "hour" not in working.columns:
				return []
		working = df.copy()
			numeric_cols = self._numeric_columns(working)
			if not numeric_cols:
				return []
		numeric_cols = self._numeric_columns(working)
			records: List[Dict] = []
			return []
			for resource_id, group in working.groupby("resource_id", dropna=False):
				# Compute per-resource robust stats so each resource is compared to itself.
				stats = {col: self._robust_stats(group[col]) for col in numeric_cols}
		for resource_id, group in working.groupby("resource_id", dropna=False):
				for _, row in group.iterrows():
					max_score = 0.0
					max_col = ""
			for _, row in group.iterrows():
					for col in numeric_cols:
						raw_value = pd.to_numeric(row[col], errors="coerce")
						score = self._robust_z(
							float(raw_value) if not pd.isna(raw_value) else float("nan"),
							stats[col]["median"],
							stats[col]["mad"],
						)
						if score > max_score:
							max_score = score
							max_col = col
					if score > max_score:
					is_anomaly = max_score >= threshold
					confidence = min(0.99, max_score / 6.0)
					if not is_anomaly:
						confidence = min(confidence, 0.49)
				confidence = min(0.99, max_score / 6.0)
					if max_col:
						reason = f"{max_col} deviated from normal baseline (score={max_score:.2f})"
					else:
						reason = "Insufficient signal for anomaly reasoning"
					reason = f"{max_col} deviated from normal baseline (score={max_score:.2f})"
					records.append(
						{
							"resource_id": str(resource_id),
							"hour": str(row["hour"]),
							"anomaly": bool(is_anomaly),
							"confidence": round(float(confidence), 4),
							"reason": reason,
							"model_name": self.model_name,
						}
					)
						"model_name": self.model_name,
			records.sort(key=lambda r: (r["resource_id"], r["hour"]))
			return records

		def detect_from_csv(self, input_csv: str, output_json: str, threshold: float = 3.0) -> List[Dict]:
			"""Load ML-ready CSV, detect anomalies, and persist JSON output."""
			df = pd.read_csv(input_csv)
			results = self.detect_from_dataframe(df, threshold=threshold)
		"""Load ML-ready CSV, detect anomalies, and persist JSON output."""
			with open(output_json, "w", encoding="utf-8") as f:
				json.dump(results, f, indent=2)

			return results

		return results
>>>>>>> 9eeca78 (Add anomaly output generation and pipeline integration)
