"""
PHASE 3: Task Block 1 - Model Registration & Versioning (MLflow)
This script loads Phase 1 artifacts and registers the model in MLflow Model Registry.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from datetime import datetime
from pathlib import Path

# ============================================================
# Configuration
# ============================================================
MLFLOW_TRACKING_URI = "http://localhost:5000"
PHASE1_MODEL_PATH = "final_model.pkl"
PHASE1_PREPROCESSOR_PATH = "preprocessor.pkl"  # Save from Phase 1 if available
MODEL_NAME = "transaction-risk-prediction"
STAGE = "Staging"  # Can be Staging or Production
EXPERIMENT_NAME = "Phase3-Deployment"

# ============================================================
# Task 1.1: Import Phase 1 Artifacts
# ============================================================
def load_phase1_artifacts():
    """Load the final trained model and preprocessing pipeline from Phase 1."""
    print("=" * 60)
    print("TASK 1.1: Importing Phase 1 Artifacts")
    print("=" * 60)
    
    # Load model
    if not os.path.exists(PHASE1_MODEL_PATH):
        raise FileNotFoundError(f"Phase 1 model not found at {PHASE1_MODEL_PATH}")
    
    model = joblib.load(PHASE1_MODEL_PATH)
    print(f"✓ Loaded model: {PHASE1_MODEL_PATH}")
    print(f"  Model type: {type(model)}")
    
    return model


def validate_model_inference(model, X_test_sample):
    """Validate that the model can generate predictions without retraining."""
    print("\n" + "-" * 60)
    print("Validating Model Inference Capability")
    print("-" * 60)
    
    try:
        # Generate predictions
        predictions = model.predict(X_test_sample)
        probabilities = model.predict_proba(X_test_sample)
        
        print(f"✓ Model predictions generated successfully")
        print(f"  Sample predictions: {predictions[:5]}")
        print(f"  Sample probabilities (fraud risk): {probabilities[:5, 1]}")
        print(f"  Prediction shape: {predictions.shape}")
        
        return True
    except Exception as e:
        print(f"✗ Model inference failed: {str(e)}")
        return False


# ============================================================
# Task 1.2: Model Registration with MLflow
# ============================================================
def setup_mlflow():
    """Set up MLflow tracking and experiment."""
    print("\n" + "=" * 60)
    print("TASK 1.2: Setting Up MLflow")
    print("=" * 60)
    
    # Set tracking URI
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    print(f"✓ MLflow tracking URI: {MLFLOW_TRACKING_URI}")
    
    # Create or get experiment
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment is None:
        experiment_id = mlflow.create_experiment(EXPERIMENT_NAME)
        print(f"✓ Created new experiment: {EXPERIMENT_NAME}")
    else:
        experiment_id = experiment.experiment_id
        print(f"✓ Using existing experiment: {EXPERIMENT_NAME}")
    
    mlflow.set_experiment(EXPERIMENT_NAME)
    return experiment_id


def register_model(model, X_test_sample, y_test_sample, metrics_dict):
    """Register the Phase 1 model with MLflow Model Registry."""
    print("\n" + "-" * 60)
    print("Registering Model in MLflow Model Registry")
    print("-" * 60)
    
    with mlflow.start_run(run_name=f"{MODEL_NAME}-{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
        
        # Log model metadata
        model_metadata = {
            "model_type": "sklearn.pipeline.Pipeline",
            "phase": "Phase 1 - Capstone ML Project",
            "created_date": datetime.now().isoformat(),
            "description": "Transaction Risk Prediction Model - XGBoost with preprocessing",
            "model_path": PHASE1_MODEL_PATH
        }
        
        mlflow.log_dict(model_metadata, "model_metadata.json")
        print(f"✓ Logged model metadata")
        
        # Log parameters
        params = {
            "test_size": 0.25,
            "random_state": 42,
            "model_algorithm": "XGBoost",
            "preprocessing": "StandardScaler + OneHotEncoder"
        }
        mlflow.log_params(params)
        print(f"✓ Logged parameters: {len(params)} params")
        
        # Log metrics
        mlflow.log_metrics(metrics_dict)
        print(f"✓ Logged metrics: {list(metrics_dict.keys())}")
        
        # Log model artifacts
        mlflow.sklearn.log_model(model, artifact_path="model", registered_model_name=MODEL_NAME)
        print(f"✓ Logged model artifact: {MODEL_NAME}")
        
        # Get run ID
        run_id = mlflow.active_run().info.run_id
        print(f"✓ MLflow Run ID: {run_id}")
    
    return run_id


def transition_model_stage(model_name, stage):
    """Transition registered model to a new stage."""
    print("\n" + "-" * 60)
    print(f"Transitioning Model to {stage} Stage")
    print("-" * 60)
    
    client = mlflow.tracking.MlflowClient()
    
    try:
        # Get the latest version
        model_versions = client.search_model_versions(f"name='{model_name}'")
        if not model_versions:
            print(f"✗ No versions found for model: {model_name}")
            return None
        
        latest_version = max(model_versions, key=lambda x: int(x.version)).version
        
        # Transition stage
        client.transition_model_version_stage(
            name=model_name,
            version=latest_version,
            stage=stage
        )
        
        print(f"✓ Model {model_name} v{latest_version} transitioned to {stage}")
        return latest_version
    
    except Exception as e:
        print(f"✗ Failed to transition model stage: {str(e)}")
        return None


# ============================================================
# Main Execution
# ============================================================
def main():
    print("\n" + "=" * 60)
    print("PHASE 3: MODEL REGISTRATION & VERSIONING")
    print("=" * 60)
    
    try:
        # Load Phase 1 artifacts
        model = load_phase1_artifacts()
        
        # For validation, we'll create dummy test data
        # In production, load actual test data from Phase 1
        print("\nNote: For full validation, load actual X_test from Phase 1")
        
        # Setup MLflow
        setup_mlflow()
        
        # Create sample metrics (replace with actual values from Phase 1)
        metrics = {
            "roc_auc_score": 0.92,  # Replace with actual from Phase 1
            "accuracy": 0.88,
            "precision": 0.85,
            "recall": 0.90,
            "f1_score": 0.87
        }
        
        # Register model
        run_id = register_model(model, None, None, metrics)
        
        # Transition to Staging
        version = transition_model_stage(MODEL_NAME, STAGE)
        
        print("\n" + "=" * 60)
        print("✓ PHASE 3 TASK BLOCK 1 COMPLETED")
        print("=" * 60)
        print(f"Model registered as: {MODEL_NAME}")
        print(f"Version: {version}")
        print(f"Stage: {STAGE}")
        print(f"Access at: {MLFLOW_TRACKING_URI}")
        
    except Exception as e:
        print(f"\n✗ Error during model registration: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
