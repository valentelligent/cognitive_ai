"""
Test script for the interaction tracker.
Includes error recovery and validation.
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
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
        logging.FileHandler(log_dir / 'test_tracker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check and validate all required dependencies"""
    required_packages = [
        'keyboard',
        'mouse',
        'psutil',
        'win32gui',
        'win32process'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
            
    if missing:
        logger.error("Missing dependencies: %s", ', '.join(missing))
        return False
    return True

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
                logger.info("Created directory: %s", dir_path)
                
        return True
    except Exception as e:
        logger.error("Environment validation failed: %s", e)
        return False

class InteractionTracker:
    def __init__(self, log_dir: str = "interaction_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_session = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.events = []
        self.last_event_time = time.time()
        
    def _get_active_window_info(self):
        try:
            import win32gui
            import win32process
            import psutil
            
            window = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(window)
            process = psutil.Process(pid)
            return {
                'window_title': win32gui.GetWindowText(window),
                'application': process.name(),
                'pid': pid
            }
        except Exception as e:
            logger.error("Error getting window info: %s", e)
            return {'window_title': 'unknown', 'application': 'unknown', 'pid': 0}
            
    def _get_system_metrics(self):
        import psutil
        
        return {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent
        }
        
    def _log_event(self, event_type, context):
        current_time = time.time()
        window_info = self._get_active_window_info()
        system_metrics = self._get_system_metrics()
        
        event = {
            'timestamp': current_time,
            'event_type': event_type,
            'context': context,
            'window_title': window_info['window_title'],
            'application': window_info['application'],
            'cpu_usage': system_metrics['cpu_usage'],
            'memory_usage': system_metrics['memory_usage'],
            'time_since_last_event': current_time - self.last_event_time
        }
        
        self.events.append(event)
        self.last_event_time = current_time
        
        # Write to file periodically
        if len(self.events) >= 100:
            self._flush_events()
            
    def _flush_events(self):
        if not self.events:
            return
            
        log_file = self.log_dir / f"interaction_log_{self.current_session}.jsonl"
        with open(log_file, 'a') as f:
            for event in self.events:
                f.write(json.dumps(event) + '\n')
        
        self.events.clear()
        
    def _handle_keyboard_event(self, event):
        if event.event_type == 'down':
            self._log_event('keyboard', {
                'key': event.name,
                'scan_code': event.scan_code
            })
            
    def _handle_mouse_click(self, x, y, button, pressed):
        if pressed:
            self._log_event('mouse_click', {
                'x': x,
                'y': y,
                'button': button
            })
            
    def _handle_mouse_move(self, x, y):
        current_time = time.time()
        if current_time - self.last_event_time >= 0.1:  # Log every 100ms
            self._log_event('mouse_move', {
                'x': x,
                'y': y
            })
            
    def start(self):
        logger.info("Starting interaction tracking...")
        import keyboard
        import mouse
        
        keyboard.on_press(self._handle_keyboard_event)
        mouse.on_click(self._handle_mouse_click)
        mouse.on_move(self._handle_mouse_move)
        
    def stop(self):
        logger.info("Stopping interaction tracking...")
        import keyboard
        import mouse
        
        keyboard.unhook_all()
        mouse.unhook_all()
        self._flush_events()
        
    def get_current_stats(self):
        return {
            'total_events': len(self.events),
            'session_duration': time.time() - self.last_event_time,
            'current_window': self._get_active_window_info(),
            'system_metrics': self._get_system_metrics()
        }

def main():
    """Main test function with error recovery"""
    logger.info("Starting interaction tracker test")
    
    if not check_dependencies():
        logger.error("Dependency check failed")
        return False
        
    if not validate_environment():
        logger.error("Environment validation failed")
        return False
        
    try:
        tracker = InteractionTracker()
        
        logger.info("Starting interaction tracking test...")
        tracker.start()
        
        test_duration = 60  # Test for 60 seconds
        start_time = time.time()
        
        while time.time() - start_time < test_duration:
            stats = tracker.get_current_stats()
            logger.info("Current stats: %s", repr(stats))
            time.sleep(5)
            
        tracker.stop()
        logger.info("Test completed successfully")
        return True
        
    except Exception as e:
        logger.error("Test failed: %s", traceback.format_exc())
        return False
        
if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
