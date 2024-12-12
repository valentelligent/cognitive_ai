"""
Test script for the cognitive interaction tracker.
Includes validation and error recovery.
"""

import time as time_module
import logging
import sys
import os
from datetime import datetime, time
from pathlib import Path
import json
import traceback

# Get the absolute path to the project root
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Configure logging
log_dir = Path(project_root) / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'test_cognitive_tracker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_cuda_availability():
    """Check if CUDA is available"""
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            logger.info(f"CUDA available: {torch.cuda.get_device_name(0)}")
            logger.info(f"Memory allocated: {torch.cuda.memory_allocated(0)/(1024**2):.1f} MB")
        else:
            logger.warning("CUDA is not available")
        return cuda_available
    except ImportError:
        logger.warning("PyTorch not installed - CUDA check skipped")
        return False

def validate_environment():
    """Validate the environment setup"""
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            logger.error("Python 3.8 or higher is required")
            return False
            
        # Check CUDA setup
        cuda_path = os.environ.get('CUDA_PATH')
        if not cuda_path:
            logger.warning("CUDA_PATH not set - GPU features may be limited")
            
        # Check directory structure
        required_dirs = ['logs', 'interaction_logs', 'test_logs']
        for dir_name in required_dirs:
            dir_path = Path(project_root) / dir_name
            if not dir_path.exists():
                dir_path.mkdir(parents=True)
                logger.info(f"Created directory: {dir_path}")
                
        return True
    except Exception as e:
        logger.error(f"Environment validation failed: {e}")
        return False

def main():
    """Main test function with error recovery"""
    logger.info("Starting cognitive interaction tracker test")
    
    if not validate_environment():
        logger.error("Environment validation failed")
        return False
        
    # Check CUDA availability
    cuda_available = check_cuda_availability()
    
    try:
        from core.monitoring.cognitive_tracker import CognitiveInteractionTracker
        
        # Define a schedule for different task types
        schedule = {
            "coding": [time(9, 0), time(12, 0)],  # 9 AM to 12 PM
            "reading": [time(13, 0), time(15, 0)], # 1 PM to 3 PM
            "research": [time(15, 0), time(17, 0)] # 3 PM to 5 PM
        }
        
        # Initialize tracker with GPU settings
        tracker = CognitiveInteractionTracker(
            schedule=schedule,
            gpu_memory_limit=0.8 if cuda_available else 0.0
        )
        
        logger.info("Starting cognitive interaction tracking test...")
        logger.info(f"Available tasks: {tracker.task_types}")
        
        # Start with coding task
        tracker.start_task("coding")
        tracker.start()
        
        test_duration = 60  # Test for 60 seconds
        start_time = time_module.time()
        
        while time_module.time() - start_time < test_duration:
            try:
                stats = tracker.get_current_stats()
                cognitive_load = tracker._calculate_cognitive_load()
                
                logger.info(
                    f"Window: {stats['current_window']['window_title']} | "
                    f"Task: {tracker.current_task} | "
                    f"Typing Speed: {cognitive_load['typing_speed']:.1f} WPM | "
                    f"Focus Score: {cognitive_load['focus_score']:.1f}"
                )
                
                time_module.sleep(5)
            except Exception as e:
                logger.error(f"Error during monitoring: {e}")
                continue
        
        tracker.stop_task()
        tracker.stop()
        logger.info("Test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
