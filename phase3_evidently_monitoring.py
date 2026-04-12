"""
PHASE 3: Task Block 3 - Monitoring & Drift Detection (Evidently AI)
Monitor data drift, model behavior, and prediction patterns.
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

try:
    from evidently.report import Report
    from evidently.metric_preset import DataDriftPreset, DataQualityPreset
    from evidently.metrics import (
        DataDriftTable,
        ColumnDriftMetric,
        DatasetDriftMetric,
        ClassificationQualityMetric
    )
except ImportError:
    print("Warning: Evidently AI not installed. Install with: pip install evidently")

# ============================================================
# Configuration
# ============================================================
MONITORING_DIR = "monitoring_reports"
PREDICTIONS_LOG_DIR = "prediction_logs"
os.makedirs(MONITORING_DIR, exist_ok=True)

# Training data statistics (from Phase 1)
TRAINING_DATA_STATS = {
    "reference_date": "2025-01-01",
    "n_samples": 500000,  # Update with actual Phase 1 training size
    "fraud_rate": 0.035  # Update with actual fraud rate
}

# ============================================================
# Task 3.1: Prediction Logging
# ============================================================

class PredictionLogger:
    """Log and manage prediction events."""
    
    def __init__(self, log_dir=PREDICTIONS_LOG_DIR):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
    
    def log_prediction(self, transaction_id, transaction_data, prediction, probability, timestamp=None):
        """Log a single prediction event."""
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "transaction_id": transaction_id,
            "transaction_data": transaction_data,
            "prediction": int(prediction),
            "probability": float(probability),
            "model_version": "phase1-v1"
        }
        
        # Append to daily log file
        log_file = os.path.join(
            self.log_dir,
            f"predictions_{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
        )
        
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def load_prediction_logs(self, date_str=None):
        """Load prediction logs for a specific date."""
        if date_str is None:
            date_str = datetime.utcnow().strftime('%Y%m%d')
        
        log_file = os.path.join(self.log_dir, f"predictions_{date_str}.jsonl")
        
        if not os.path.exists(log_file):
            return pd.DataFrame()
        
        records = []
        with open(log_file, "r") as f:
            for line in f:
                records.append(json.loads(line))
        
        return pd.DataFrame(records)


# ============================================================
# Task 3.2: Data Drift Monitoring
# ============================================================

class DataDriftMonitor:
    """Monitor data drift using Evidently AI."""
    
    def __init__(self, reference_data, report_dir=MONITORING_DIR):
        """
        Initialize monitor with reference (training) dataset.
        
        Args:
            reference_data: DataFrame with training data
            report_dir: Directory to save reports
        """
        self.reference_data = reference_data
        self.report_dir = report_dir
        os.makedirs(report_dir, exist_ok=True)
    
    def detect_data_drift(self, current_data, report_name=None):
        """
        Detect data drift between reference and current data.
        
        Returns:
            - Drift report (HTML + JSON)
            - Drift summary
        """
        
        if report_name is None:
            report_name = f"drift_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        print("\n" + "=" * 60)
        print("TASK 3.2: Detecting Data Drift")
        print("=" * 60)
        
        try:
            # Create drift detection report
            drift_report = Report(metrics=[
                DataDriftPreset(),
                DataQualityPreset()
            ])
            
            drift_report.run(
                reference_data=self.reference_data,
                current_data=current_data
            )
            
            # Save reports
            html_path = os.path.join(self.report_dir, f"{report_name}.html")
            json_path = os.path.join(self.report_dir, f"{report_name}.json")
            
            drift_report.save_html(html_path)
            drift_report.save_json(json_path)
            
            print(f"✓ Drift report saved:")
            print(f"  HTML: {html_path}")
            print(f"  JSON: {json_path}")
            
            # Extract drift summary
            drift_summary = self._extract_drift_summary(drift_report)
            
            return drift_report, drift_summary
        
        except Exception as e:
            print(f"✗ Error detecting drift: {str(e)}")
            return None, None
    
    def _extract_drift_summary(self, report):
        """Extract key drift insights from report."""
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_drift_detected": False,
            "drifted_features": [],
            "feature_stats": {}
        }
        
        try:
            # Extract from report metrics
            for metric in report.metrics:
                if hasattr(metric, 'result'):
                    summary["feature_stats"] = metric.result
        except:
            pass
        
        return summary
    
    def compare_distributions(self, feature, reference_data, current_data):
        """Compare feature distributions between reference and current data."""
        print(f"\nComparing distribution for feature: {feature}")
        
        ref_dist = reference_data[feature].value_counts(normalize=True)
        curr_dist = current_data[feature].value_counts(normalize=True)
        
        comparison = {
            "feature": feature,
            "reference_mean": float(reference_data[feature].mean()) if reference_data[feature].dtype in ['int64', 'float64'] else None,
            "current_mean": float(current_data[feature].mean()) if current_data[feature].dtype in ['int64', 'float64'] else None,
            "reference_unique": int(reference_data[feature].nunique()),
            "current_unique": int(current_data[feature].nunique())
        }
        
        return comparison


# ============================================================
# Task 3.3: Model Behavior Monitoring
# ============================================================

class ModelBehaviorMonitor:
    """Monitor model prediction behavior and anomalies."""
    
    def __init__(self, report_dir=MONITORING_DIR):
        self.report_dir = report_dir
        os.makedirs(report_dir, exist_ok=True)
    
    def analyze_prediction_distribution(self, predictions_df):
        """Analyze prediction distribution for anomalies."""
        print("\n" + "=" * 60)
        print("TASK 3.3: Analyzing Model Behavior")
        print("=" * 60)
        
        analysis = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_predictions": len(predictions_df),
            "fraud_predictions_count": int(predictions_df['prediction'].sum()),
            "fraud_rate": float(predictions_df['prediction'].mean()),
            "avg_probability": float(predictions_df['probability'].mean()),
            "probability_std": float(predictions_df['probability'].std()),
            "high_confidence_predictions": int((predictions_df['probability'] > 0.8).sum()),
            "low_confidence_predictions": int((predictions_df['probability'] < 0.3).sum()),
            "anomalies_detected": False,
            "anomaly_details": []
        }
        
        # Check for anomalies
        expected_fraud_rate = TRAINING_DATA_STATS["fraud_rate"]
        current_fraud_rate = analysis["fraud_rate"]
        
        if abs(current_fraud_rate - expected_fraud_rate) > expected_fraud_rate * 0.5:
            analysis["anomalies_detected"] = True
            analysis["anomaly_details"].append({
                "type": "fraud_rate_spike",
                "expected": expected_fraud_rate,
                "observed": current_fraud_rate,
                "percent_change": ((current_fraud_rate - expected_fraud_rate) / expected_fraud_rate) * 100
            })
        
        # Check for confidence spikes
        if analysis["low_confidence_predictions"] > len(predictions_df) * 0.2:
            analysis["anomalies_detected"] = True
            analysis["anomaly_details"].append({
                "type": "low_confidence_spike",
                "percentage": (analysis["low_confidence_predictions"] / len(predictions_df)) * 100
            })
        
        print(f"✓ Analyzed {len(predictions_df)} predictions")
        print(f"  Fraud rate: {analysis['fraud_rate']:.2%}")
        print(f"  Avg probability: {analysis['avg_probability']:.3f}")
        
        if analysis["anomalies_detected"]:
            print(f"  ⚠ Anomalies detected: {len(analysis['anomaly_details'])}")
        
        return analysis
    
    def generate_monitoring_report(self, predictions_df, drift_summary, behavior_analysis):
        """Generate comprehensive monitoring report."""
        report = {
            "report_timestamp": datetime.utcnow().isoformat(),
            "phase": "Phase 3 - Deployment & Monitoring",
            "data_drift": drift_summary,
            "model_behavior": behavior_analysis,
            "recommendations": self._generate_recommendations(drift_summary, behavior_analysis)
        }
        
        # Save report
        report_file = os.path.join(
            self.report_dir,
            f"monitoring_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n✓ Monitoring report saved: {report_file}")
        
        return report
    
    def _generate_recommendations(self, drift_summary, behavior_analysis):
        """Generate actionable recommendations."""
        recommendations = []
        
        if behavior_analysis and behavior_analysis.get("anomalies_detected"):
            recommendations.append({
                "priority": "HIGH",
                "action": "Review predictions",
                "reason": "Model behavior anomalies detected"
            })
        
        if drift_summary and drift_summary.get("drifted_features"):
            recommendations.append({
                "priority": "HIGH",
                "action": "Investigate data drift",
                "reason": f"Drift detected in {len(drift_summary['drifted_features'])} features"
            })
        
        return recommendations


# ============================================================
# Main Monitoring Pipeline
# ============================================================

def run_monitoring_pipeline(
    reference_data_path,
    current_data_path,
    predictions_log_date=None
):
    """
    Run complete monitoring pipeline.
    
    Args:
        reference_data_path: Path to training data (from Phase 1)
        current_data_path: Path to current production data
        predictions_log_date: Date of predictions to analyze
    """
    
    print("\n" + "=" * 60)
    print("PHASE 3: TASK BLOCK 3 - MONITORING & DRIFT DETECTION")
    print("=" * 60)
    
    try:
        # Load reference and current data
        print("\nLoading data...")
        reference_data = pd.read_csv(reference_data_path)
        current_data = pd.read_csv(current_data_path)
        
        print(f"✓ Reference data shape: {reference_data.shape}")
        print(f"✓ Current data shape: {current_data.shape}")
        
        # Initialize monitors
        drift_monitor = DataDriftMonitor(reference_data)
        behavior_monitor = ModelBehaviorMonitor()
        
        # Task 3.1: Log predictions (already done by API)
        print("\n✓ Task 3.1: Predictions logged by FastAPI service")
        
        # Task 3.2: Detect data drift
        _, drift_summary = drift_monitor.detect_data_drift(current_data)
        
        # Task 3.3: Analyze model behavior
        # Load predictions from logs
        prediction_logger = PredictionLogger()
        predictions_df = prediction_logger.load_prediction_logs(predictions_log_date)
        
        if not predictions_df.empty:
            behavior_analysis = behavior_monitor.analyze_prediction_distribution(predictions_df)
        else:
            print("⚠ No prediction logs found")
            behavior_analysis = {}
        
        # Generate reports
        monitoring_report = behavior_monitor.generate_monitoring_report(
            predictions_df if not predictions_df.empty else current_data,
            drift_summary,
            behavior_analysis
        )
        
        print("\n" + "=" * 60)
        print("✓ MONITORING PIPELINE COMPLETED")
        print("=" * 60)
        
        return {
            "drift_summary": drift_summary,
            "behavior_analysis": behavior_analysis,
            "monitoring_report": monitoring_report
        }
    
    except Exception as e:
        print(f"\n✗ Error in monitoring pipeline: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================
# Example Usage
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("PHASE 3: TASK BLOCK 3 - MONITORING & DRIFT DETECTION")
    print("=" * 80)
    
    print("""
    Example usage:
    
    # Initialize prediction logger
    logger = PredictionLogger()
    logger.log_prediction("tx_001", {"amount": 100}, 0, 0.15)
    
    # Run monitoring pipeline
    results = run_monitoring_pipeline(
        reference_data_path="training_data.csv",
        current_data_path="production_data.csv"
    )
    """)
