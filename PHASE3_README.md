# PHASE 3: Model Deployment & Monitoring - Complete Guide

## Overview

Phase 3 operationalizes the trained fraud detection model from Phase 1 into a production-ready system with monitoring, versioning, and deployment capabilities. This phase focuses on MLOps practices rather than model improvement.

## Phase 3 Objectives

✓ **Deploy Phase 1 Model**: Move from development to production  
✓ **Version Control**: Track models using MLflow  
✓ **REST API**: Expose predictions via FastAPI  
✓ **Monitor Drift**: Detect data and model behavior changes  
✓ **Containerize**: Package service as Docker image  
✓ **Scale**: Deploy on Kubernetes with auto-scaling  

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│   Phase 1 Model (final_model.pkl)                      │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
    ┌───▼────────┐          ┌────▼──────────┐
    │   MLflow   │          │  Monitoring   │
    │  Registry  │          │  & Logging    │
    └───┬────────┘          └────┬──────────┘
        │                        │
        └────────────┬───────────┘
                     ▼
            ┌────────────────────┐
            │  FastAPI Server    │
            │  (REST API)        │
            │  Port: 8000        │
            └────────┬───────────┘
                     │
            ┌────────▼───────────┐
            │  Docker Container  │
            └────────┬───────────┘
                     │
            ┌────────▼───────────┐
            │  Kubernetes        │
            │  - Load Balancer   │
            │  - Auto-Scaling    │
            │  - Persistent Vol. │
            └────────────────────┘
```

---

## Files Included

### Core Implementation Files

| File | Purpose |
|------|---------|
| `phase3_mlflow_registration.py` | Load Phase 1 model, register in MLflow |
| `phase3_fastapi_inference.py` | REST API server for predictions |
| `phase3_evidently_monitoring.py` | Data drift & behavior monitoring |
| `phase3_config.py` | Configuration management |
| `phase3_setup.py` | Interactive setup assistant |

### Deployment Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Container image definition |
| `k8s-deployment.yaml` | Kubernetes manifests |
| `phase3_requirements.txt` | Python dependencies |

---

## Quick Start

### 1. Setup Environment

```bash
# Run interactive setup
python phase3_setup.py

# Or manual step-by-step:
pip install -r phase3_requirements.txt
```

### 2. Test Locally

**Terminal 1 - MLflow Server:**
```bash
mlflow ui --host 0.0.0.0 --port 5000
# Access: http://localhost:5000
```

**Terminal 2 - FastAPI Server:**
```bash
python phase3_fastapi_inference.py
# Access: http://localhost:8000
# Interactive docs: http://localhost:8000/docs
```

### 3. Register Model

```bash
python phase3_mlflow_registration.py
```

### 4. Test API

```bash
# Health check
curl http://localhost:8000/health

# Get metadata
curl http://localhost:8000/metadata

# Make prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"TransactionAmt": 150.50, "card1": 12345, ...}'
```

---

## TASK BLOCK 1: Model Registration & Versioning

### Objectives
- ✓ Load Phase 1 trained model
- ✓ Log to MLflow for versioning
- ✓ Register in Model Registry
- ✓ Transition to staging/production

### Implementation

```python
from phase3_mlflow_registration import *

# Load model
model = load_phase1_artifacts()

# Setup MLflow
setup_mlflow()

# Register with metrics
metrics = {"roc_auc": 0.92, "accuracy": 0.88}
run_id = register_model(model, None, None, metrics)

# Transition stage
version = transition_model_stage("transaction-risk-prediction", "Staging")
```

### Key Features
- **Version Tracking**: Every model version tracked
- **Metrics Logging**: Performance metrics stored
- **Artifact Storage**: Preprocessors and pipelines saved
- **Stage Management**: Control deployment stages

---

## TASK BLOCK 2: Model Serving (REST API)

### Objectives
- ✓ Create REST API for predictions
- ✓ Handle single & batch requests
- ✓ Log predictions for monitoring
- ✓ Implement health checks

### Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/metadata` | GET | API metadata |
| `/predict` | POST | Single prediction |
| `/predict/batch` | POST | Batch predictions |

### Example Usage

```python
import requests

# Single prediction
response = requests.post(
    "http://localhost:8000/predict",
    json={"TransactionAmt": 150.50, "card1": 12345, ...}
)
result = response.json()
# {"risk_flag": 1, "risk_score": 0.85, "confidence": 0.92}

# Batch predictions
response = requests.post(
    "http://localhost:8000/predict/batch",
    json={"transactions": [tx1, tx2, tx3, ...]}
)
```

---

## TASK BLOCK 3: Monitoring & Drift Detection

### Objectives
- ✓ Log predictions in real-time
- ✓ Detect data drift vs training data
- ✓ Monitor model behavior anomalies
- ✓ Generate monitoring reports

### Components

#### 3.1 Prediction Logging
```python
from phase3_evidently_monitoring import PredictionLogger

logger = PredictionLogger()
logger.log_prediction(
    transaction_id="tx_001",
    transaction_data={"amount": 100, ...},
    prediction=0,
    probability=0.15
)
```

#### 3.2 Data Drift Detection
```python
from phase3_evidently_monitoring import DataDriftMonitor

monitor = DataDriftMonitor(reference_data)
report, summary = monitor.detect_data_drift(current_data)
# Compares distributions, detects feature drift
```

#### 3.3 Model Behavior Monitoring
```python
from phase3_evidently_monitoring import ModelBehaviorMonitor

behavior_monitor = ModelBehaviorMonitor()
analysis = behavior_monitor.analyze_prediction_distribution(predictions_df)
# Tracks fraud rate, confidence, anomalies
```

### Monitoring Artifacts
- **prediction_logs/**: Daily prediction logs (JSONL format)
- **monitoring_reports/**: HTML and JSON drift reports
- **Alerts**: Anomaly detection and fraud rate spikes

---

## TASK BLOCK 4: Containerization & Deployment

### 4.1 Docker

**Build Image:**
```bash
docker build -t transaction-risk-api:latest .
```

**Run Container:**
```bash
docker run -p 8000:8000 \
  -v $(pwd)/prediction_logs:/app/prediction_logs \
  transaction-risk-api:latest
```

**Verify:**
```bash
docker ps
curl http://localhost:8000/health
```

### 4.2 Kubernetes

**Deploy:**
```bash
kubectl apply -f k8s-deployment.yaml
```

**Verify:**
```bash
# Check pods
kubectl get pods -n transaction-risk-pred

# Check services
kubectl get svc -n transaction-risk-pred

# View logs
kubectl logs deployment/transaction-risk-api -n transaction-risk-pred
```

**Access Service:**
```bash
# Port forward
kubectl port-forward svc/transaction-risk-api-service 8000:80 \
  -n transaction-risk-pred

# Access
curl http://localhost:8000/health
```

**Scale Deployment:**
```bash
kubectl scale deployment transaction-risk-api --replicas=5 \
  -n transaction-risk-pred
```

---

## TASK BLOCK 5: System Validation & Summary

### Validation Checklist

- [ ] Model loads without errors
- [ ] MLflow registration successful
- [ ] FastAPI server starts
- [ ] API endpoints respond correctly
- [ ] Predictions logged properly
- [ ] Docker image builds
- [ ] Kubernetes deployment runs
- [ ] Monitoring reports generated
- [ ] Drift detection working
- [ ] Scaling and HA verified

### Deployment Architecture

```
User Requests
       │
       ▼
┌─────────────────┐
│ Load Balancer   │ (K8s Service)
└────────┬────────┘
         │
    ┌────┴────┬────┬────┐
    │          │    │    │
    ▼          ▼    ▼    ▼
┌─────────────────────────────┐
│  API Pods (3-10 replicas)   │
│  - FastAPI + Model          │
│  - Request Handling         │
│  - Result Return            │
└────────┬────────────────────┘
         │
    ┌────┴────┬────────────┐
    │          │            │
    ▼          ▼            ▼
┌──────────┬──────────┬──────────────┐
│  Logs    │ Metrics  │  Monitoring  │
│  Storage │ (Prom)   │  (Evidently) │
└──────────┴──────────┴──────────────┘
```

---

## Configuration

### Configuration File (phase3_config.json)

```json
{
  "model": {
    "model_path": "final_model.pkl",
    "model_version": "phase1-v1"
  },
  "api": {
    "host": "0.0.0.0",
    "port": 8000
  },
  "mlflow": {
    "tracking_uri": "http://localhost:5000"
  },
  "monitoring": {
    "enabled": true,
    "drift_detection_enabled": true
  },
  "kubernetes": {
    "namespace": "transaction-risk-pred",
    "replicas": 3
  }
}
```

---

## Monitoring & Alerts

### Key Metrics to Track

1. **Prediction Volume**: Requests per second
2. **Fraud Rate**: % of transactions flagged as fraud
3. **Model Confidence**: Average prediction probability
4. **Data Drift**: Feature distribution changes
5. **Latency**: API response time
6. **Error Rate**: Failed predictions

### Alert Conditions

- Fraud rate ±50% from baseline
- Data drift detected in >3 features
- Model confidence drops below 0.6
- API latency >1 second
- Error rate >5%

---

## Production Deployment Checklist

### Pre-Deployment
- [ ] All tests pass
- [ ] Code reviewed
- [ ] Configuration validated
- [ ] Monitoring dashboards ready
- [ ] Runbooks prepared

### Deployment
- [ ] Build Docker image
- [ ] Push to registry
- [ ] Deploy to staging
- [ ] Smoke tests pass
- [ ] Deploy to production

### Post-Deployment
- [ ] Monitor metrics
- [ ] Check prediction logs
- [ ] Verify drift reports
- [ ] Test auto-scaling
- [ ] Document any issues

---

## Troubleshooting

### Issue: Model not found
```bash
# Check file exists
ls final_model.pkl

# Copy from Phase 1
cp ../phase1/final_model.pkl .
```

### Issue: API connection refused
```bash
# Check if server running
ps aux | grep fastapi

# Start server
python phase3_fastapi_inference.py
```

### Issue: Kubernetes pods not starting
```bash
# Check logs
kubectl logs pod/...  -n transaction-risk-pred

# Describe pod
kubectl describe pod/... -n transaction-risk-pred

# Check events
kubectl get events -n transaction-risk-pred
```

### Issue: Docker build fails
```bash
# Clean build
docker build --no-cache -t transaction-risk-api:latest .

# Check Dockerfile
cat Dockerfile
```

---

## Performance Optimization

### API Optimization
- Use async handlers
- Implement request batching
- Add caching for repeated predictions
- Monitor response times

### Resource Management
- Set appropriate CPU/memory limits
- Enable auto-scaling
- Use persistent volumes for logs
- Implement log rotation

### Monitoring Optimization
- Use sampling for high-volume logs
- Archive old logs
- Optimize database queries
- Use efficient storage

---

## Next Steps

1. **Production Deployment**
   - Deploy to production K8s cluster
   - Set up monitoring dashboards
   - Configure alerting

2. **Advanced Monitoring**
   - Integrate with Prometheus/Grafana
   - Set up distributed tracing
   - Implement custom metrics

3. **Model Updates**
   - Set up automated retraining
   - Implement canary deployments
   - Create rollback procedures

4. **Security**
   - Add authentication/authorization
   - Implement rate limiting
   - Use TLS/SSL

---

## Resources

- MLflow Documentation: https://mlflow.org/docs/
- FastAPI Documentation: https://fastapi.tiangolo.com/
- Kubernetes Documentation: https://kubernetes.io/docs/
- Evidently AI: https://evidentlyai.com/

---

## Support

For issues or questions:
1. Check troubleshooting section
2. Review logs in prediction_logs/
3. Check monitoring_reports/
4. Consult Phase 1 documentation

---

## Summary

Phase 3 successfully:
✓ Productionized Phase 1 model  
✓ Implemented versioning and tracking  
✓ Created REST API for serving  
✓ Set up comprehensive monitoring  
✓ Containerized service  
✓ Deployed on Kubernetes  

The transaction risk prediction system is now ready for production deployment with full monitoring, versioning, and scaling capabilities.
