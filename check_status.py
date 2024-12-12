"""
Quick script to check if trackers are running and creating logs
"""
import os
import time
from pathlib import Path
import psutil
import glob
from datetime import datetime
import logging

def check_tracker_status():
    print("\n=== Tracker Status Check ===")
    
    # Check for Python processes
    python_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe':
                cmdline = proc.info['cmdline']
                if cmdline and any('tracker' in str(cmd).lower() for cmd in cmdline):
                    python_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    print(f"\nRunning Tracker Processes: {len(python_processes)}")
    for proc in python_processes:
        try:
            print(f"- PID {proc.pid}: {' '.join(proc.info['cmdline'])}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Check logs directory
    log_dir = Path("logs")
    if not log_dir.exists():
        print("\nLogs directory not found!")
        return
        
    # Check different types of logs
    log_patterns = {
        "Interaction": "interaction_*.log",
        "Cognitive": "cognitive_*.log",
        "Development": "development_*.log",
        "Manager": "tracker_manager.log"
    }
    
    print("\nLog Files Status:")
    for log_type, pattern in log_patterns.items():
        log_files = sorted(glob.glob(str(log_dir / pattern)))
        if not log_files:
            print(f"\n{log_type} Logs: No log files found")
            continue
            
        latest_log = log_files[-1]
        latest_log_path = Path(latest_log)
        
        # Get file stats
        try:
            mtime = datetime.fromtimestamp(latest_log_path.stat().st_mtime)
            size = latest_log_path.stat().st_size
            
            print(f"\n{log_type} Latest Log:")
            print(f"- File: {latest_log_path.name}")
            print(f"- Last Modified: {mtime}")
            print(f"- Size: {size:,} bytes")
            
            # Check if recently modified (within last 30 seconds)
            if (datetime.now() - mtime).total_seconds() < 30:
                print("- Status: ACTIVE - recently modified")
            else:
                print("- Status: INACTIVE - no recent changes")
        except Exception as e:
            print(f"Error reading {log_type} log: {e}")

if __name__ == "__main__":
    check_tracker_status()
