"""
PHASE 3: Task Block 2 - Model Serving (FastAPI REST API)
REST API for transaction risk prediction inference using Phase 1 model.
"""

import os
import joblib
import json
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import numpy as np
import pandas as pd

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn

# ============================================================
# Configuration
# ============================================================
MODEL_PATH = "final_model.pkl"
LOG_DIR = "prediction_logs"
os.makedirs(LOG_DIR, exist_ok=True)

# ============================================================
# Pydantic Models for Request/Response Validation
# ============================================================

class TransactionData(BaseModel):
    """Schema for individual transaction input."""
    TransactionAmt: float = Field(..., description="Transaction amount")
    card1: int = Field(..., description="Card identifier 1")
    card2: int = Field(..., description="Card identifier 2")
    addr1: int = Field(..., description="Address identifier 1")
    addr2: int = Field(..., description="Address identifier 2")
    # Add other required features based on Phase 1 model
    # This is a sample - adjust based on actual model features
    
    class Config:
        schema_extra = {
            "example": {
                "TransactionAmt": 150.50,
                "card1": 12345,
                "card2": 67890,
                "addr1": 111,
                "addr2": 222
            }
        }


class PredictionResponse(BaseModel):
    """Schema for prediction response."""
    transaction_id: Optional[str] = None
    risk_flag: int = Field(..., description="0: legitimate, 1: fraudulent")
    risk_score: float = Field(..., description="Fraud probability [0-1]")
    confidence: float = Field(..., description="Model confidence")
    timestamp: str = Field(..., description="Prediction timestamp")
    model_version: str = Field(..., description="Model version used")


class BatchPredictionRequest(BaseModel):
    """Schema for batch prediction requests."""
    transactions: List[Dict] = Field(..., description="List of transaction data")


class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str
    model_loaded: bool
    timestamp: str


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="Transaction Risk Prediction API",
    description="Phase 3 - Model Serving API for fraud risk predictions",
    version="1.0.0"
)

# Global model reference
loaded_model = None
MODEL_VERSION = "phase1-v1"


# ============================================================
# Startup & Shutdown Events
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Load model on application startup."""
    global loaded_model
    
    print("=" * 60)
    print("STARTING API SERVER")
    print("=" * 60)
    
    try:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
        
        loaded_model = joblib.load(MODEL_PATH)
        print(f"✓ Model loaded successfully from {MODEL_PATH}")
        print(f"  Model type: {type(loaded_model)}")
        print(f"  Model version: {MODEL_VERSION}")
    
    except Exception as e:
        print(f"✗ Failed to load model: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("Shutting down API server...")


# ============================================================
# Health Check Endpoint
# ============================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health and model availability."""
    return HealthResponse(
        status="healthy" if loaded_model is not None else "unhealthy",
        model_loaded=loaded_model is not None,
        timestamp=datetime.utcnow().isoformat()
    )


# ============================================================
# Metadata Endpoint
# ============================================================

@app.get("/metadata")
async def get_metadata():
    """Get model and API metadata."""
    return {
        "api_name": "Transaction Risk Prediction",
        "api_version": "1.0.0",
        "phase": "Phase 3 - Deployment & Monitoring",
        "model_version": MODEL_VERSION,
        "model_loaded": loaded_model is not None,
        "model_path": MODEL_PATH,
        "server_time": datetime.utcnow().isoformat()
    }


# ============================================================
# Single Prediction Endpoint
# ============================================================

@app.post("/predict", response_model=PredictionResponse)
async def predict(transaction: Dict, background_tasks: BackgroundTasks):
    """
    Generate fraud risk prediction for a single transaction.
    
    Returns:
        - risk_flag: 0 (legitimate) or 1 (fraudulent)
        - risk_score: Probability of fraud [0-1]
        - confidence: Model confidence
    """
    
    if loaded_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Convert transaction dict to DataFrame
        # Ensure feature order matches training data
        tx_df = pd.DataFrame([transaction])
        
        # Generate predictions
        risk_flag = loaded_model.predict(tx_df)[0]
        risk_score = loaded_model.predict_proba(tx_df)[0, 1]  # Probability of fraud
        confidence = max(loaded_model.predict_proba(tx_df)[0])
        
        response = PredictionResponse(
            risk_flag=int(risk_flag),
            risk_score=float(risk_score),
            confidence=float(confidence),
            timestamp=datetime.utcnow().isoformat(),
            model_version=MODEL_VERSION
        )
        
        # Log prediction in background
        background_tasks.add_task(
            log_prediction,
            transaction,
            risk_flag,
            risk_score
        )
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")


# ============================================================
# Batch Prediction Endpoint
# ============================================================

@app.post("/predict/batch")
async def predict_batch(request: BatchPredictionRequest, background_tasks: BackgroundTasks):
    """
    Generate fraud risk predictions for multiple transactions.
    """
    
    if loaded_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if not request.transactions:
        raise HTTPException(status_code=400, detail="No transactions provided")
    
    try:
        # Convert batch to DataFrame
        tx_df = pd.DataFrame(request.transactions)
        
        # Generate predictions
        risk_flags = loaded_model.predict(tx_df)
        risk_scores = loaded_model.predict_proba(tx_df)[:, 1]
        
        results = []
        for idx, (flag, score) in enumerate(zip(risk_flags, risk_scores)):
            results.append({
                "transaction_index": idx,
                "risk_flag": int(flag),
                "risk_score": float(score),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Log batch in background
        background_tasks.add_task(
            log_batch_prediction,
            request.transactions,
            risk_flags,
            risk_scores
        )
        
        return {
            "batch_size": len(results),
            "predictions": results,
            "model_version": MODEL_VERSION,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Batch prediction error: {str(e)}")


# ============================================================
# Logging Functions
# ============================================================

def log_prediction(transaction: Dict, risk_flag: int, risk_score: float):
    """Log individual prediction for monitoring."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "transaction": transaction,
        "risk_flag": int(risk_flag),
        "risk_score": float(risk_score),
        "model_version": MODEL_VERSION
    }
    
    log_file = os.path.join(LOG_DIR, f"predictions_{datetime.utcnow().strftime('%Y%m%d')}.jsonl")
    
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def log_batch_prediction(transactions: List[Dict], risk_flags: np.ndarray, risk_scores: np.ndarray):
    """Log batch prediction for monitoring."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "batch_size": len(transactions),
        "risk_flags": risk_flags.tolist(),
        "risk_scores": risk_scores.tolist(),
        "model_version": MODEL_VERSION
    }
    
    log_file = os.path.join(LOG_DIR, f"batch_predictions_{datetime.utcnow().strftime('%Y%m%d')}.jsonl")
    
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


# ============================================================
# Error Handlers
# ============================================================

@app.exception_handler(Exception)
async def general_exception_handler(exc: Exception):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


# ============================================================
# Main Execution
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PHASE 3: TASK BLOCK 2 - MODEL SERVING (REST API)")
    print("=" * 60)
    print("Starting FastAPI server...")
    print("API Documentation available at: http://localhost:8000/docs")
    print("=" * 60 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
