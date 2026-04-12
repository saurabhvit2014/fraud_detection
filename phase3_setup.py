"""
PHASE 3: Setup and Deployment Script
Complete setup guide for Phase 3 Model Deployment & Monitoring
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional

# ============================================================
# Color codes for terminal output
# ============================================================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# ============================================================
# Setup Functions
# ============================================================

def print_header(title):
    """Print formatted header."""
    print("\n" + Colors.HEADER + "=" * 60 + Colors.ENDC)
    print(Colors.HEADER + Colors.BOLD + title + Colors.ENDC)
    print(Colors.HEADER + "=" * 60 + Colors.ENDC)


def print_step(step_num, description):
    """Print numbered step."""
    print(f"\n{Colors.CYAN}Step {step_num}: {description}{Colors.ENDC}")


def print_success(message):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")


def print_error(message):
    """Print error message."""
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")


def print_warning(message):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")


def print_command(command):
    """Print command to run."""
    print(f"{Colors.BLUE}$ {command}{Colors.ENDC}")


# ============================================================
# Installation Functions
# ============================================================

def install_dependencies():
    """Install Phase 3 dependencies."""
    print_step(1, "Install Phase 3 Dependencies")
    
    # Check if requirements file exists
    if not os.path.exists("phase3_requirements.txt"):
        print_error("phase3_requirements.txt not found")
        return False
    
    try:
        print_command("pip install -r phase3_requirements.txt")
        subprocess.run(
            ["pip", "install", "-r", "phase3_requirements.txt"],
            check=True
        )
        print_success("Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {str(e)}")
        return False


def check_phase1_artifacts():
    """Check if Phase 1 artifacts exist."""
    print_step(2, "Verify Phase 1 Artifacts")
    
    required_files = ["final_model.pkl"]
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print_success(f"Found: {file}")
        else:
            print_warning(f"Missing: {file}")
            missing_files.append(file)
    
    if missing_files:
        print_error(f"Missing Phase 1 artifacts: {missing_files}")
        print("  Please ensure Phase 1 notebook has been executed")
        return False
    
    return True


def create_directories():
    """Create required directories."""
    print_step(3, "Create Directories")
    
    directories = [
        "prediction_logs",
        "monitoring_reports",
        "mlflow_artifacts",
        "data",
        "models"
    ]
    
    for dir_name in directories:
        os.makedirs(dir_name, exist_ok=True)
        print_success(f"Created directory: {dir_name}")
    
    return True


def generate_config():
    """Generate default configuration."""
    print_step(4, "Generate Configuration")
    
    try:
        from phase3_config import ConfigManager
        
        config = ConfigManager()
        config.save_to_file("phase3_config.json")
        print_success("Configuration saved: phase3_config.json")
        return True
    except Exception as e:
        print_error(f"Failed to generate config: {str(e)}")
        return False


# ============================================================
# Docker Functions
# ============================================================

def build_docker_image():
    """Build Docker image."""
    print_step(5, "Build Docker Image")
    
    if not os.path.exists("Dockerfile"):
        print_error("Dockerfile not found")
        return False
    
    try:
        print_command("docker build -t transaction-risk-api:latest .")
        subprocess.run(
            ["docker", "build", "-t", "transaction-risk-api:latest", "."],
            check=True
        )
        print_success("Docker image built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to build Docker image: {str(e)}")
        print_warning("Make sure Docker is installed and running")
        return False
    except FileNotFoundError:
        print_error("Docker not found. Install Docker to build images.")
        return False


def run_docker_container():
    """Run Docker container locally."""
    print_step(6, "Run Docker Container")
    
    try:
        print_command("docker run -p 8000:8000 -v $(pwd)/prediction_logs:/app/prediction_logs transaction-risk-api:latest")
        
        # Create command for cross-platform
        volume_path = os.path.abspath("prediction_logs")
        cmd = [
            "docker", "run",
            "-p", "8000:8000",
            "-v", f"{volume_path}:/app/prediction_logs",
            "transaction-risk-api:latest"
        ]
        
        subprocess.run(cmd, check=False)
        print_success("Container started")
        return True
    except FileNotFoundError:
        print_error("Docker not found.")
        return False


# ============================================================
# Kubernetes Functions
# ============================================================

def deploy_to_kubernetes():
    """Deploy to Kubernetes."""
    print_step(7, "Deploy to Kubernetes")
    
    if not os.path.exists("k8s-deployment.yaml"):
        print_error("k8s-deployment.yaml not found")
        return False
    
    try:
        print_command("kubectl apply -f k8s-deployment.yaml")
        subprocess.run(
            ["kubectl", "apply", "-f", "k8s-deployment.yaml"],
            check=True
        )
        print_success("Kubernetes resources deployed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to deploy: {str(e)}")
        return False
    except FileNotFoundError:
        print_error("kubectl not found. Install kubectl to deploy to Kubernetes.")
        return False


def check_kubernetes_deployment():
    """Check Kubernetes deployment status."""
    print_step(8, "Check Deployment Status")
    
    try:
        # Check pods
        print("\nPods in transaction-risk-pred namespace:")
        print_command("kubectl get pods -n transaction-risk-pred")
        subprocess.run(
            ["kubectl", "get", "pods", "-n", "transaction-risk-pred"],
            check=False
        )
        
        # Check services
        print("\nServices in transaction-risk-pred namespace:")
        print_command("kubectl get svc -n transaction-risk-pred")
        subprocess.run(
            ["kubectl", "get", "svc", "-n", "transaction-risk-pred"],
            check=False
        )
        
        return True
    except FileNotFoundError:
        print_error("kubectl not found.")
        return False


# ============================================================
# MLflow Functions
# ============================================================

def start_mlflow_server():
    """Start MLflow tracking server."""
    print_step(9, "Start MLflow Server")
    
    try:
        print_command("mlflow ui --host 0.0.0.0 --port 5000")
        subprocess.run(
            ["mlflow", "ui", "--host", "0.0.0.0", "--port", "5000"],
            check=False
        )
        print_success("MLflow server running at http://localhost:5000")
        return True
    except FileNotFoundError:
        print_error("MLflow not found. Install with: pip install mlflow")
        return False


# ============================================================
# FastAPI Functions
# ============================================================

def start_fastapi_server():
    """Start FastAPI server."""
    print_step(10, "Start FastAPI Server")
    
    if not os.path.exists("phase3_fastapi_inference.py"):
        print_error("phase3_fastapi_inference.py not found")
        return False
    
    try:
        print_command("python phase3_fastapi_inference.py")
        subprocess.run(
            ["python", "phase3_fastapi_inference.py"],
            check=False
        )
        print_success("FastAPI server running at http://localhost:8000")
        return True
    except Exception as e:
        print_error(f"Failed to start FastAPI: {str(e)}")
        return False


# ============================================================
# Monitoring Functions
# ============================================================

def run_monitoring_pipeline():
    """Run monitoring pipeline."""
    print_step(11, "Run Monitoring Pipeline")
    
    if not os.path.exists("phase3_evidently_monitoring.py"):
        print_error("phase3_evidently_monitoring.py not found")
        return False
    
    try:
        print_command("python phase3_evidently_monitoring.py")
        subprocess.run(
            ["python", "phase3_evidently_monitoring.py"],
            check=False
        )
        print_success("Monitoring pipeline executed")
        return True
    except Exception as e:
        print_error(f"Failed to run monitoring: {str(e)}")
        return False


# ============================================================
# Interactive Menu
# ============================================================

def show_menu():
    """Display interactive menu."""
    print_header("PHASE 3: MODEL DEPLOYMENT & MONITORING - SETUP")
    
    print("\n" + Colors.BOLD + "Setup Options:" + Colors.ENDC)
    print(f"\n  {Colors.CYAN}1{Colors.ENDC} - Full Setup (All steps)")
    print(f"  {Colors.CYAN}2{Colors.ENDC} - Install Dependencies Only")
    print(f"  {Colors.CYAN}3{Colors.ENDC} - Build Docker Image")
    print(f"  {Colors.CYAN}4{Colors.ENDC} - Deploy to Kubernetes")
    print(f"  {Colors.CYAN}5{Colors.ENDC} - Start FastAPI Server")
    print(f"  {Colors.CYAN}6{Colors.ENDC} - Start MLflow Server")
    print(f"  {Colors.CYAN}7{Colors.ENDC} - Run Monitoring Pipeline")
    print(f"  {Colors.CYAN}8{Colors.ENDC} - Show Deployment Guide")
    print(f"  {Colors.CYAN}9{Colors.ENDC} - Exit")
    
    return input("\nSelect option (1-9): ").strip()


def show_deployment_guide():
    """Show deployment guide."""
    guide = """
╔════════════════════════════════════════════════════════════════╗
║         PHASE 3 DEPLOYMENT GUIDE                              ║
╚════════════════════════════════════════════════════════════════╝

STEP 1: SETUP ENVIRONMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$ python phase3_setup.py
→ Installs dependencies
→ Creates required directories
→ Generates configuration

STEP 2: LOCAL TESTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Terminal 1: MLflow Server
$ mlflow ui --host 0.0.0.0 --port 5000
→ Access at http://localhost:5000

Terminal 2: FastAPI Server
$ python phase3_fastapi_inference.py
→ Access at http://localhost:8000
→ Interactive docs at http://localhost:8000/docs

STEP 3: TEST API
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$ curl http://localhost:8000/health
$ curl http://localhost:8000/metadata

STEP 4: CONTAINERIZATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Build Docker image:
$ docker build -t transaction-risk-api:latest .

Run container:
$ docker run -p 8000:8000 transaction-risk-api:latest

STEP 5: KUBERNETES DEPLOYMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Deploy to cluster:
$ kubectl apply -f k8s-deployment.yaml

Verify deployment:
$ kubectl get pods -n transaction-risk-pred
$ kubectl get svc -n transaction-risk-pred

Port forward to local:
$ kubectl port-forward svc/transaction-risk-api-service 8000:80 -n transaction-risk-pred

STEP 6: MONITORING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
View prediction logs:
$ ls prediction_logs/

Check monitoring reports:
$ ls monitoring_reports/

Run monitoring pipeline:
$ python -c "from phase3_evidently_monitoring import run_monitoring_pipeline; \
run_monitoring_pipeline('training_data.csv', 'production_data.csv')"

USEFUL COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
View MLflow models:
$ mlflow models list

Kubernetes pod logs:
$ kubectl logs deployment/transaction-risk-api -n transaction-risk-pred

Scale deployment:
$ kubectl scale deployment transaction-risk-api --replicas=5 -n transaction-risk-pred

Delete deployment:
$ kubectl delete -f k8s-deployment.yaml

FILES CREATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ phase3_mlflow_registration.py     - MLflow registration
✓ phase3_fastapi_inference.py       - REST API
✓ phase3_evidently_monitoring.py    - Drift detection
✓ phase3_config.py                  - Configuration
✓ Dockerfile                         - Docker image
✓ k8s-deployment.yaml               - K8s manifests
✓ phase3_requirements.txt            - Dependencies
✓ phase3_setup.py                   - Setup script

NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Execute setup script
2. Test locally with FastAPI
3. Build Docker image
4. Deploy to Kubernetes
5. Monitor predictions and drift
6. Set up alerts and dashboards
"""
    print(guide)


# ============================================================
# Main Execution
# ============================================================

def main():
    """Main setup flow."""
    
    while True:
        choice = show_menu()
        
        if choice == "1":
            # Full setup
            print_header("PHASE 3: FULL SETUP")
            install_dependencies()
            check_phase1_artifacts()
            create_directories()
            generate_config()
            print_header("✓ SETUP COMPLETE")
            print("\nNext steps:")
            print(f"  {Colors.CYAN}1{Colors.ENDC} - Run: python phase3_mlflow_registration.py")
            print(f"  {Colors.CYAN}2{Colors.ENDC} - Run: python phase3_fastapi_inference.py")
            print(f"  {Colors.CYAN}3{Colors.ENDC} - Access: http://localhost:8000/docs")
            
        elif choice == "2":
            install_dependencies()
            
        elif choice == "3":
            build_docker_image()
            
        elif choice == "4":
            deploy_to_kubernetes()
            check_kubernetes_deployment()
            
        elif choice == "5":
            start_fastapi_server()
            
        elif choice == "6":
            start_mlflow_server()
            
        elif choice == "7":
            run_monitoring_pipeline()
            
        elif choice == "8":
            show_deployment_guide()
            
        elif choice == "9":
            print_success("Exiting setup")
            break
            
        else:
            print_error("Invalid option")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\nSetup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)
