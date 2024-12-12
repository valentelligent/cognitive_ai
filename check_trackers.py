"""
Check and manage tracker processes
"""

import os
import psutil
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
import time
import subprocess

def setup_logging():
    log_dir = Path(__file__).parent / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'check_trackers.log'),
            logging.StreamHandler()
        ]
    )

def check_python_processes():
    logger = logging.getLogger(__name__)
    trackers = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info['cmdline']
                if cmdline and any(x and ('tracker.py' in x) for x in cmdline):
                    trackers.append({
                        'pid': proc.info['pid'],
                        'cmdline': cmdline,
                        'create_time': datetime.fromtimestamp(proc.create_time())
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return trackers

def start_trackers():
    logger = logging.getLogger(__name__)
    project_root = Path(__file__).parent
    python_exe = sys.executable
    
    if not python_exe:
        logger.error("Could not find Python executable")
        return False
        
    try:
        # Start cognitive tracker
        cognitive_tracker = project_root / 'core' / 'monitoring' / 'cognitive_tracker.py'
        if cognitive_tracker.exists():
            subprocess.Popen([python_exe, str(cognitive_tracker)], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            logger.info("Started cognitive tracker")
            
        # Start interaction tracker
        interaction_tracker = project_root / 'core' / 'monitoring' / 'interaction_tracker.py'
        if interaction_tracker.exists():
            subprocess.Popen([python_exe, str(interaction_tracker)],
                           creationflags=subprocess.CREATE_NO_WINDOW)
            logger.info("Started interaction tracker")
            
        return True
    except Exception as e:
        logger.error(f"Error starting trackers: {e}")
        return False

def check_tracker_health():
    logger = logging.getLogger(__name__)
    trackers = check_python_processes()
    current_time = datetime.now()
    
    for tracker in trackers:
        runtime = current_time - tracker['create_time']
        if runtime > timedelta(hours=12):
            logger.warning(f"Tracker (PID: {tracker['pid']}) running for {runtime.total_seconds()/3600:.1f} hours. Consider restarting.")
            
    return len(trackers) > 0

if __name__ == '__main__':
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Checking for running trackers...")
    trackers = check_python_processes()
    
    if trackers:
        logger.info("\nFound running tracker processes:")
        for proc in trackers:
            logger.info(f"PID: {proc['pid']}")
            logger.info(f"Command: {proc['cmdline']}")
            logger.info(f"Running since: {proc['create_time']}\n")
    else:
        logger.info("No tracker processes found running")
        logger.info("\nAttempting to start trackers...")
        if start_trackers():
            logger.info("\nTrackers started successfully. Checking again in 3 seconds...")
            time.sleep(3)
            
            # Check if they're running
            trackers = check_python_processes()
            if trackers:
                logger.info("\nConfirmed trackers are now running:")
                for proc in trackers:
                    logger.info(f"PID: {proc['pid']}")
                    logger.info(f"Command: {proc['cmdline']}")
                    logger.info(f"Started at: {proc['create_time']}\n")
            else:
                logger.warning("\nWarning: Trackers may not have started properly")
