"""
PHASE 3: Configuration and Utility Functions
Centralized configuration and helper functions for Phase 3 deployment.
"""

import os
from dataclasses import dataclass
from typing import Dict, Any, Optional
import json
from pathlib import Path

# ============================================================
# Configuration Classes
# ============================================================

@dataclass
class ModelConfig:
    """Model configuration parameters."""
    model_path: str = "final_model.pkl"
    preprocessor_path: str = "preprocessor.pkl"
    model_name: str = "transaction-risk-prediction"
    model_version: str = "phase1-v1"
    phase: str = "Phase 3 - Deployment & Monitoring"


@dataclass
class APIConfig:
    """FastAPI configuration parameters."""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    log_level: str = "info"
    reload: bool = False
    cors_origins: list = None
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]


@dataclass
class MLFlowConfig:
    """MLflow configuration parameters."""
    tracking_uri: str = "http://localhost:5000"
    experiment_name: str = "Phase3-Deployment"
    registry_uri: str = "sqlite:///mlflow.db"
    artifact_location: str = "./mlflow_artifacts"


@dataclass
class MonitoringConfig:
    """Monitoring configuration parameters."""
    enabled: bool = True
    prediction_log_dir: str = "prediction_logs"
    monitoring_report_dir: str = "monitoring_reports"
    drift_detection_enabled: bool = True
    drift_check_interval: int = 3600  # seconds
    anomaly_threshold: float = 0.5


@dataclass
class KubernetesConfig:
    """Kubernetes configuration parameters."""
    namespace: str = "transaction-risk-pred"
    deployment_name: str = "transaction-risk-api"
    service_name: str = "transaction-risk-api-service"
    replicas: int = 3
    image: str = "transaction-risk-api:latest"
    image_pull_policy: str = "IfNotPresent"


# ============================================================
# Environment Configuration Manager
# ============================================================

class ConfigManager:
    """Centralized configuration management."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager."""
        self.model_config = ModelConfig()
        self.api_config = APIConfig()
        self.mlflow_config = MLFlowConfig()
        self.monitoring_config = MonitoringConfig()
        self.k8s_config = KubernetesConfig()
        
        # Load from file if provided
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
        
        # Load from environment variables
        self.load_from_env()
    
    def load_from_file(self, config_file: str):
        """Load configuration from JSON file."""
        print(f"Loading configuration from {config_file}")
        
        with open(config_file, "r") as f:
            config_dict = json.load(f)
        
        if "model" in config_dict:
            self.model_config = ModelConfig(**config_dict["model"])
        if "api" in config_dict:
            self.api_config = APIConfig(**config_dict["api"])
        if "mlflow" in config_dict:
            self.mlflow_config = MLFlowConfig(**config_dict["mlflow"])
        if "monitoring" in config_dict:
            self.monitoring_config = MonitoringConfig(**config_dict["monitoring"])
        if "kubernetes" in config_dict:
            self.k8s_config = KubernetesConfig(**config_dict["kubernetes"])
    
    def load_from_env(self):
        """Load configuration from environment variables."""
        # Model config
        self.model_config.model_path = os.getenv("MODEL_PATH", self.model_config.model_path)
        self.model_config.model_version = os.getenv("MODEL_VERSION", self.model_config.model_version)
        
        # API config
        self.api_config.host = os.getenv("API_HOST", self.api_config.host)
        self.api_config.port = int(os.getenv("API_PORT", self.api_config.port))
        self.api_config.workers = int(os.getenv("API_WORKERS", self.api_config.workers))
        
        # MLflow config
        self.mlflow_config.tracking_uri = os.getenv("MLFLOW_TRACKING_URI", self.mlflow_config.tracking_uri)
        
        # Monitoring config
        self.monitoring_config.enabled = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
        
        # K8s config
        self.k8s_config.namespace = os.getenv("K8S_NAMESPACE", self.k8s_config.namespace)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "model": self.model_config.__dict__,
            "api": self.api_config.__dict__,
            "mlflow": self.mlflow_config.__dict__,
            "monitoring": self.monitoring_config.__dict__,
            "kubernetes": self.k8s_config.__dict__
        }
    
    def save_to_file(self, config_file: str):
        """Save configuration to JSON file."""
        os.makedirs(os.path.dirname(config_file) or ".", exist_ok=True)
        
        with open(config_file, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        
        print(f"✓ Configuration saved to {config_file}")
    
    def print_config(self):
        """Print current configuration."""
        print("\n" + "=" * 60)
        print("PHASE 3 CONFIGURATION")
        print("=" * 60)
        
        config_dict = self.to_dict()
        for section, values in config_dict.items():
            print(f"\n{section.upper()}:")
            for key, value in values.items():
                print(f"  {key}: {value}")


# ============================================================
# Path Management
# ============================================================

class PathManager:
    """Manage file paths and directories."""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create required directories."""
        directories = [
            "prediction_logs",
            "monitoring_reports",
            "mlflow_artifacts",
            "data",
            "models"
        ]
        
        for dir_name in directories:
            dir_path = self.base_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get_path(self, path_type: str) -> Path:
        """Get commonly used paths."""
        paths = {
            "predictions": self.base_dir / "prediction_logs",
            "monitoring": self.base_dir / "monitoring_reports",
            "mlflow": self.base_dir / "mlflow_artifacts",
            "data": self.base_dir / "data",
            "models": self.base_dir / "models"
        }
        
        return paths.get(path_type, self.base_dir)


# ============================================================
# Logging Configuration
# ============================================================

import logging

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('phase3.log')
        ]
    )
    
    return logging.getLogger("Phase3-Deployment")


# ============================================================
# Default Configuration
# ============================================================

def get_default_config() -> ConfigManager:
    """Get default configuration."""
    return ConfigManager()


def create_sample_config_file(filepath: str = "phase3_config.json"):
    """Create sample configuration file."""
    config = ConfigManager()
    config.save_to_file(filepath)
    print(f"\n✓ Sample configuration created at {filepath}")
    print("  Edit this file to customize Phase 3 settings")


# ============================================================
# Example Usage
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PHASE 3: Configuration Management")
    print("=" * 60)
    
    # Create and display default configuration
    config = ConfigManager()
    config.print_config()
    
    # Save to file
    create_sample_config_file()
