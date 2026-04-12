# PHASE 3: Quick Start Commands Reference

## Installation & Setup

### Install Dependencies
```bash
pip install -r phase3_requirements.txt
```

### Generate Configuration
```bash
python phase3_setup.py
# Select option 1 for full setup
```

---

## Local Testing

### Start MLflow Server
```bash
mlflow ui --host 0.0.0.0 --port 5000
# Access: http://localhost:5000
```

### Start FastAPI Server
```bash
python phase3_fastapi_inference.py
# Access: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Test API Health
```bash
curl http://localhost:8000/health
```

### Register Model with MLflow
```bash
python phase3_mlflow_registration.py
```

---

## Docker

### Build Image
```bash
docker build -t transaction-risk-api:latest .
```

### Run Container
```bash
docker run -p 8000:8000 \
  -v $(pwd)/prediction_logs:/app/prediction_logs \
  transaction-risk-api:latest
```

### Docker Compose (All Services)
```bash
docker-compose up -d
# Services: MLflow, FastAPI, PostgreSQL, Prometheus, Grafana
```

### View Container Logs
```bash
docker logs -f <container-id>
docker-compose logs -f api
```

### Stop All Containers
```bash
docker-compose down
```

---

## Kubernetes

### Deploy to Cluster
```bash
kubectl apply -f k8s-deployment.yaml
```

### Check Deployment Status
```bash
kubectl get pods -n transaction-risk-pred
kubectl get svc -n transaction-risk-pred
kubectl describe deployment transaction-risk-api -n transaction-risk-pred
```

### View Logs
```bash
kubectl logs deployment/transaction-risk-api -n transaction-risk-pred
kubectl logs -f pod/<pod-name> -n transaction-risk-pred
```

### Port Forward to Local Machine
```bash
kubectl port-forward svc/transaction-risk-api-service \
  8000:80 -n transaction-risk-pred
```

### Scale Deployment
```bash
kubectl scale deployment transaction-risk-api \
  --replicas=5 -n transaction-risk-pred
```

### Update Deployment
```bash
kubectl set image deployment/transaction-risk-api \
  api-server=transaction-risk-api:v2 -n transaction-risk-pred
```

### Check Auto-Scaling
```bash
kubectl get hpa -n transaction-risk-pred
kubectl describe hpa transaction-risk-api-hpa -n transaction-risk-pred
```

### Delete Deployment
```bash
kubectl delete -f k8s-deployment.yaml
```

---

## Monitoring

### View Prediction Logs
```bash
# Today's logs
tail -f prediction_logs/predictions_*.jsonl

# Specific date
cat prediction_logs/predictions_20240101.jsonl | head -10

# Count predictions
wc -l prediction_logs/predictions_*.jsonl
```

### Run Monitoring Pipeline
```bash
python phase3_evidently_monitoring.py
```

### View Monitoring Reports
```bash
# List reports
ls -lh monitoring_reports/

# Open HTML report in browser
open monitoring_reports/drift_report_*.html
```

### Check Prediction Statistics
```bash
python -c "
import json
import pandas as pd

# Load and analyze logs
logs = []
with open('prediction_logs/predictions_20240101.jsonl') as f:
    for line in f:
        logs.append(json.loads(line))

df = pd.DataFrame(logs)
print(df.describe())
print(f'Fraud rate: {df[\"prediction\"].mean():.2%}')
print(f'Avg probability: {df[\"probability\"].mean():.3f}')
"
```

---

## Testing

### Health Check
```bash
curl -X GET http://localhost:8000/health
```

### Get Metadata
```bash
curl -X GET http://localhost:8000/metadata
```

### Single Prediction
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "TransactionAmt": 150.50,
    "card1": 12345,
    "card2": 67890,
    "addr1": 111,
    "addr2": 222
  }'
```

### Batch Predictions
```bash
curl -X POST http://localhost:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [
      {"TransactionAmt": 100, "card1": 111, ...},
      {"TransactionAmt": 200, "card1": 222, ...}
    ]
  }'
```

---

## MLflow

### View Models
```bash
mlflow models list
```

### Get Model Details
```bash
mlflow models describe transaction-risk-prediction
```

### View Experiment Runs
```bash
mlflow experiments list
mlflow runs list --experiment-name "Phase3-Deployment"
```

### Promote Model
```bash
mlflow models alias set --name transaction-risk-prediction \
  --alias production --version 1
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000
kill -9 <PID>
```

### Permission Denied (Docker)
```bash
sudo usermod -aG docker $USER
```

### Model Not Found
```bash
# Check file exists
ls -la final_model.pkl

# Check working directory
pwd
```

### API Connection Refused
```bash
# Check if API is running
ps aux | grep fastapi

# Check logs
tail -f *.log
```

### Kubernetes Pod Stuck
```bash
# Get pod details
kubectl describe pod <pod-name> -n transaction-risk-pred

# Check events
kubectl get events -n transaction-risk-pred

# Delete and recreate
kubectl delete pod <pod-name> -n transaction-risk-pred
```

### Out of Memory
```bash
# Check resource usage
docker stats
kubectl top nodes
kubectl top pods -n transaction-risk-pred
```

---

## Performance Tuning

### Increase API Workers
Edit Dockerfile:
```
CMD ["python", "-m", "uvicorn", "phase3_fastapi_inference:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "4"]
```

### Enable Caching
In phase3_fastapi_inference.py:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_prediction(features):
    return model.predict(features)
```

### Optimize Docker Image
```bash
# Use smaller base image
FROM python:3.11-slim

# Multi-stage build already implemented in Dockerfile
```

### K8s Resource Limits
Adjust in k8s-deployment.yaml:
```yaml
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 2000m
    memory: 2Gi
```

---

## Backup & Restore

### Backup Model Artifacts
```bash
tar -czf model_backup_$(date +%Y%m%d).tar.gz \
  final_model.pkl prediction_logs monitoring_reports
```

### Backup MLflow Data
```bash
cp -r mlflow_artifacts mlflow_artifacts_backup
```

### Restore from Backup
```bash
tar -xzf model_backup_20240101.tar.gz
```

---

## Cleanup

### Remove Docker Images
```bash
docker rmi transaction-risk-api:latest
docker system prune -a
```

### Remove Kubernetes Resources
```bash
kubectl delete namespace transaction-risk-pred
```

### Clean Local Files
```bash
rm -rf prediction_logs/* monitoring_reports/* mlflow_artifacts/*
```

---

## Environment Variables

### MLflow
```bash
export MLFLOW_TRACKING_URI=http://localhost:5000
export MLFLOW_BACKEND_STORE_URI=sqlite:///mlflow.db
```

### FastAPI
```bash
export API_HOST=0.0.0.0
export API_PORT=8000
export API_WORKERS=4
```

### Monitoring
```bash
export MONITORING_ENABLED=true
export DRIFT_DETECTION_ENABLED=true
```

---

## Useful Links

- MLflow UI: http://localhost:5000
- FastAPI Docs: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- Kubernetes Dashboard: (requires kubectl proxy)

---

## Additional Resources

- [MLflow Documentation](https://mlflow.org/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Kubernetes Docs](https://kubernetes.io/docs/)
- [Evidently AI](https://evidentlyai.com/)
- [Docker Documentation](https://docs.docker.com/)

---

## Support

For detailed information, see:
- PHASE3_README.md: Complete guide
- phase3_config.py: Configuration details
- Individual Python files: Code documentation
