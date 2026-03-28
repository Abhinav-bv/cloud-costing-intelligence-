"""
src/data_cleaner.py
Data cleaning and preparation pipeline for ML model input.
"""

import logging
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Tuple

from config import LOCAL_DB_CONFIG, OUTPUT_DIR, ML_READY_CSV

logger = logging.getLogger(__name__)


class DataCleaner:
    """Clean and prepare raw metrics data for ML models"""
    
    def __init__(self):
        self.db_file = LOCAL_DB_CONFIG["file"]
    
    def load_raw_metrics(self) -> pd.DataFrame:
        """
        Load raw metrics from SQLite database.
        
        Returns:
            DataFrame with columns: resource_id, metric_name, metric_value, timestamp
        """
        try:
            conn = sqlite3.connect(self.db_file)
            query = "SELECT resource_id, metric_name, metric_value, timestamp FROM metrics ORDER BY timestamp"
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            logger.info(f"Loaded {len(df)} raw metric records")
            return df
            
        except Exception as e:
            logger.error(f"Error loading raw metrics: {e}")
            return pd.DataFrame()
    
    def load_billing_data(self) -> pd.DataFrame:
        """
        Load billing data from SQLite database.
        
        Returns:
            DataFrame with columns: resource_id, service, cost, date
        """
        try:
            conn = sqlite3.connect(self.db_file)
            query = "SELECT resource_id, service, cost, date FROM billing ORDER BY date"
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            logger.info(f"Loaded {len(df)} billing records")
            return df
            
        except Exception as e:
            logger.error(f"Error loading billing data: {e}")
            return pd.DataFrame()
    
    def clean_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and normalize metrics data.
        
        Steps:
        - Convert timestamp to datetime
        - Handle missing values
        - Detect and remove outliers
        - Normalize values
        
        Args:
            df: Raw metrics DataFrame
        
        Returns:
            Cleaned DataFrame
        """
        if df.empty:
            logger.warning("No data to clean")
            return df
        
        df = df.copy()
        
        # Convert timestamp to datetime (handle mixed formats + timezone offsets)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', utc=True)
        
        logger.info("Cleaning metrics data...")
        
        # 1. Handle missing values - forward fill then backward fill
        logger.info(f"  - Missing values before: {df['metric_value'].isna().sum()}")
        df['metric_value'] = df['metric_value'].ffill().bfill()
        logger.info(f"  - Missing values after: {df['metric_value'].isna().sum()}")
        
        # 2. Detect and remove outliers using IQR method
        logger.info(f"  - Removing outliers...")
        try:
            # Group by metric_name and remove outliers for each metric
            outliers_mask = pd.Series([False] * len(df), index=df.index)
            
            for metric in df['metric_name'].unique():
                metric_data = df[df['metric_name'] == metric]
                Q1 = metric_data['metric_value'].quantile(0.25)
                Q3 = metric_data['metric_value'].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Mark outliers for this metric
                outlier_indices = metric_data[
                    (metric_data['metric_value'] < lower_bound) | 
                    (metric_data['metric_value'] > upper_bound)
                ].index
                
                outlier_count = len(outlier_indices)
                if outlier_count > 0:
                    logger.info(f"    - Removed {outlier_count} outliers from {metric}")
                    outliers_mask[outlier_indices] = True
            
            original_len = len(df)
            df = df[~outliers_mask].copy()
            removed = original_len - len(df)
            logger.info(f"  - Total removed: {removed} outlier records")
        except Exception as e:
            logger.warning(f"  - Error removing outliers: {e}")
        
        # 3. Normalize values to 0-100 range per metric
        logger.info(f"  - Normalizing metrics to 0-100 range...")
        try:
            for metric in df['metric_name'].unique():
                metric_mask = df['metric_name'] == metric
                min_val = df.loc[metric_mask, 'metric_value'].min()
                max_val = df.loc[metric_mask, 'metric_value'].max()
                
                if max_val > min_val:
                    df.loc[metric_mask, 'metric_value'] = (
                        (df.loc[metric_mask, 'metric_value'] - min_val) / 
                        (max_val - min_val) * 100
                    )
        except Exception as e:
            logger.warning(f"  - Error normalizing: {e}")
        
        logger.info(f"Cleaned: {len(df)} records")
        return df
    
    def clean_billing(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean billing data.
        
        Args:
            df: Raw billing DataFrame
        
        Returns:
            Cleaned DataFrame
        """
        if df.empty:
            logger.warning("No billing data to clean")
            return df
        
        df = df.copy()
        
        logger.info("Cleaning billing data...")
        
        # Convert date to datetime (handle mixed formats)
        df['date'] = pd.to_datetime(df['date'], format='mixed', utc=True)
        
        # Handle missing costs
        logger.info(f"  - Missing costs before: {df['cost'].isna().sum()}")
        df['cost'] = df['cost'].fillna(0)
        logger.info(f"  - Missing costs after: {df['cost'].isna().sum()}")
        
        # Remove negative costs (refunds shouldn't be counted as costs here)
        negative_count = (df['cost'] < 0).sum()
        if negative_count > 0:
            logger.info(f"  - Removed {negative_count} negative cost entries (refunds)")
            df = df[df['cost'] >= 0]
        
        logger.info(f"Cleaned: {len(df)} billing records")
        return df
    
    def aggregate_metrics_hourly(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate metrics to hourly averages for ML model input.
        
        Args:
            df: Cleaned metrics DataFrame
        
        Returns:
            Hourly aggregated DataFrame
        """
        if df.empty:
            return df
        
        logger.info("Aggregating metrics to hourly...")
        
        # Round timestamp to nearest hour
        df['hour'] = df['timestamp'].dt.floor('h')
        
        # Group by resource, metric, and hour - calculate mean
        agg_df = df.groupby(['resource_id', 'metric_name', 'hour']).agg({
            'metric_value': ['mean', 'min', 'max', 'std']
        }).reset_index()
        
        # Flatten column names
        agg_df.columns = ['resource_id', 'metric_name', 'hour', 'mean', 'min', 'max', 'std']
        
        logger.info(f"Aggregated to {len(agg_df)} hourly records")
        return agg_df
    
    def pivot_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pivot metrics so each metric becomes a column (for ML model).
        
        Args:
            df: Aggregated metrics DataFrame
        
        Returns:
            Pivoted DataFrame with metrics as columns
        """
        if df.empty:
            return df
        
        logger.info("Pivoting metrics to columns...")
        
        # Pivot metric_name to columns
        pivot_df = df.pivot_table(
            index=['resource_id', 'hour'],
            columns='metric_name',
            values='mean',
            aggfunc='first'
        ).reset_index()
        
        logger.info(f"Pivoted to {len(pivot_df)} records with {len(pivot_df.columns)} columns")
        return pivot_df
    
    def prepare_ml_dataset(self, output_path: str = None) -> pd.DataFrame:
        """
        Complete pipeline: load -> clean -> aggregate -> pivot -> export to CSV.
        
        Args:
            output_path: Path to save CSV file (default from config)
        
        Returns:
            ML-ready DataFrame
        """
        if output_path is None:
            output_path = f"{OUTPUT_DIR}/{ML_READY_CSV}"
        
        logger.info("=" * 60)
        logger.info("STARTING DATA CLEANING PIPELINE")
        logger.info("=" * 60)
        
        # Load raw data
        raw_metrics = self.load_raw_metrics()
        if raw_metrics.empty:
            logger.error("No metrics data to process")
            return pd.DataFrame()
        
        # Clean metrics
        clean_metrics = self.clean_metrics(raw_metrics)
        
        # Aggregate to hourly
        hourly_metrics = self.aggregate_metrics_hourly(clean_metrics)
        
        # Pivot to columns
        ml_ready_df = self.pivot_metrics(hourly_metrics)
        
        # Fill remaining NaN with forward fill then backward fill
        ml_ready_df = ml_ready_df.ffill().bfill()
        
        # Save to CSV
        import os
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        ml_ready_df.to_csv(output_path, index=False)
        logger.info(f"Saved ML-ready data to {output_path}")
        
        # Print dataset info
        logger.info("\nDATASET STATISTICS:")
        logger.info(f"  - Records: {len(ml_ready_df)}")
        logger.info(f"  - Features: {len(ml_ready_df.columns)}")
        logger.info(f"  - Date range: {ml_ready_df['hour'].min()} to {ml_ready_df['hour'].max()}")
        logger.info(f"  - Missing values: {ml_ready_df.isna().sum().sum()}")
        logger.info("\n" + "=" * 60)
        
        return ml_ready_df
    
    def generate_summary(self, df: pd.DataFrame) -> str:
        """Generate summary statistics of cleaned data"""
        if df.empty:
            return "No data to summarize"
        
        summary = f"""
CLEANED DATA SUMMARY
==================
Records: {len(df)}
Resources: {df['resource_id'].nunique() if 'resource_id' in df.columns else 'N/A'}
Date Range: {df['hour'].min() if 'hour' in df.columns else 'N/A'} to {df['hour'].max() if 'hour' in df.columns else 'N/A'}
Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB

Columns: {', '.join(df.columns.tolist())}
        """
        return summary
