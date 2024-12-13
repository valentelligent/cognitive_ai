from pydantic import BaseSettings
from typing import Dict, Any
import os

class MonitoringConfig(BaseSettings):
    # Monitoring intervals (in seconds)
    COGNITIVE_MONITOR_INTERVAL: int = 60
    HEALTH_CHECK_INTERVAL: int = 30
    PATTERN_ANALYSIS_INTERVAL: int = 300
    
    # Feature flags
    ENABLE_AUTONOMOUS_MONITORING: bool = True
    ENABLE_PATTERN_ANALYSIS: bool = True
    ENABLE_GRAY_AREA_DETECTION: bool = True
    ENABLE_CONSCIOUSNESS_TRACKING: bool = True
    
    # Logging configuration
    LOG_LEVEL: str = os.getenv('COGNITIVE_LOG_LEVEL', 'INFO')
    DETAILED_LOGGING: bool = os.getenv('COGNITIVE_DETAILED_LOGGING', 'true').lower() == 'true'
    
    # Thresholds
    CPU_ALERT_THRESHOLD: float = 80.0
    MEMORY_ALERT_THRESHOLD: float = 80.0
    DISK_ALERT_THRESHOLD: float = 90.0
    
    # Buffer sizes
    PATTERN_BUFFER_SIZE: int = 1000
    EVENT_BUFFER_SIZE: int = 5000
    
    # Analysis windows (in minutes)
    GRAY_AREA_WINDOW: int = 30
    PATTERN_ANALYSIS_WINDOW: int = 60
    CONSCIOUSNESS_TRACKING_WINDOW: int = 120
    
    # Alert thresholds
    COGNITIVE_LOAD_THRESHOLD: float = 0.8
    UNCERTAINTY_THRESHOLD: float = 0.7
    PATTERN_SIGNIFICANCE_THRESHOLD: float = 0.6
    
    class Config:
        env_prefix = 'COGNITIVE_'
        case_sensitive = True
