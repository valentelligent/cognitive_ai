# PowerShell script to start the cognitive and interaction trackers
$ErrorActionPreference = "Stop"
$VerbosePreference = "Continue"

Write-Verbose "Starting tracker initialization..."

# Initialize conda - Check both common installation paths
$condaPaths = @(
    "C:\Users\$env:USERNAME\anaconda3",
    "C:\ProgramData\anaconda3",
    "C:\Users\$env:USERNAME\miniconda3"
)

$condaCmd = $null
foreach ($path in $condaPaths) {
    $testPath = Join-Path $path "Scripts\conda.exe"
    if (Test-Path $testPath) {
        $condaCmd = $testPath
        $condaPath = $path
        break
    }
}

if (-not $condaCmd) {
    Write-Error "Conda not found in any of the standard locations. Please ensure Anaconda/Miniconda is installed."
    exit 1
}

Write-Verbose "Found conda at: $condaCmd"

# Set environment variables first
Write-Verbose "Setting up environment variables..."
$env:CUDA_PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1"
$env:PATH = "$condaPath;$condaPath\Scripts;$condaPath\Library\bin;$env:PATH"
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"
$env:PYTHONIOENCODING = "utf-8"

# Create directories if they don't exist
$directories = @(
    "logs",
    "data",
    "temp",
    "core\monitoring"
)

foreach ($dir in $directories) {
    $dirPath = Join-Path $PWD $dir
    if (-not (Test-Path $dirPath)) {
        New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
        Write-Verbose "Created directory: $dirPath"
    }
}

# Get the project root and Python path
$projectRoot = $PWD
$pythonPath = Join-Path $condaPath "envs\cog_ai\python.exe"
if (-not (Test-Path $pythonPath)) {
    $pythonPath = Join-Path $condaPath "python.exe"
}
Write-Verbose "Using Python: $pythonPath"

Write-Host "`n=== Starting Trackers ===" -ForegroundColor Green
try {
    # First, let's check if the core monitoring module exists
    $trackerManagerPath = Join-Path $PWD "core\monitoring\tracker_manager.py"
    if (-not (Test-Path $trackerManagerPath)) {
        Write-Verbose "Creating tracker manager module..."
        $trackerManagerCode = @"
import logging
import time
from pathlib import Path
import psutil
import json
from datetime import datetime
import threading
import queue

class BaseTracker(threading.Thread):
    def __init__(self, name: str, log_dir: Path):
        super().__init__(daemon=True)
        self.name = name
        self.log_dir = log_dir
        self.running = False
        self.queue = queue.Queue()
        self.logger = logging.getLogger(f"tracker.{name}")
        
    def run(self):
        self.running = True
        self.logger.info(f"{self.name} tracker started")
        
        while self.running:
            try:
                # Process events from queue with timeout
                try:
                    event = self.queue.get(timeout=1.0)
                    self.process_event(event)
                except queue.Empty:
                    continue
            except Exception as e:
                self.logger.error(f"Error in {self.name} tracker: {e}")
                time.sleep(1)
    
    def process_event(self, event):
        # Override in subclasses
        pass
    
    def stop(self):
        self.running = False
        self.join(timeout=5.0)

class CognitiveTracker(BaseTracker):
    def process_event(self, event):
        # Process cognitive events
        pass

class InteractionTracker(BaseTracker):
    def process_event(self, event):
        # Process interaction events
        pass

class DevelopmentTracker(BaseTracker):
    def process_event(self, event):
        # Process development events
        pass

class TrackerManager:
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.log_dir = self.project_root / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self.trackers = {}
        
        # Initialize trackers
        self.trackers['cognitive'] = CognitiveTracker('cognitive', self.log_dir)
        self.trackers['interaction'] = InteractionTracker('interaction', self.log_dir)
        self.trackers['development'] = DevelopmentTracker('development', self.log_dir)
        
    def start_all_trackers(self) -> bool:
        try:
            for name, tracker in self.trackers.items():
                self.logger.info(f"Starting {name} tracker...")
                tracker.start()
            return True
        except Exception as e:
            self.logger.error(f"Failed to start trackers: {e}")
            return False
    
    def check_tracker_status(self) -> dict:
        status = {}
        for name, tracker in self.trackers.items():
            if tracker.is_alive():
                status[name] = 'running'
            else:
                status[name] = 'stopped'
        return status
    
    def stop_all_trackers(self):
        for name, tracker in self.trackers.items():
            self.logger.info(f"Stopping {name} tracker...")
            tracker.stop()
        return True
"@
        New-Item -ItemType File -Path $trackerManagerPath -Force
        Set-Content -Path $trackerManagerPath -Value $trackerManagerCode -Encoding UTF8
    }

    # Create __init__.py files
    $initPaths = @(
        (Join-Path $PWD "core\__init__.py"),
        (Join-Path $PWD "core\monitoring\__init__.py")
    )
    foreach ($path in $initPaths) {
        if (-not (Test-Path $path)) {
            New-Item -ItemType File -Path $path -Force | Out-Null
        }
    }

    # Create and run the Python script to start trackers
    $startScript = @"
from pathlib import Path
import logging
import os
import sys
import traceback

# Setup logging
log_dir = Path('logs')
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'tracker_manager.log'),
        logging.StreamHandler()
    ]
)

# Add project root to Python path
project_root = Path(r'$projectRoot')
sys.path.insert(0, str(project_root))

try:
    from core.monitoring.tracker_manager import TrackerManager
except ImportError as e:
    logging.error(f"Failed to import TrackerManager: {e}")
    logging.error(f"Traceback: {traceback.format_exc()}")
    sys.exit(1)

try:
    logging.info("Initializing TrackerManager...")
    manager = TrackerManager(project_root)

    logging.info("Starting all trackers...")
    success = manager.start_all_trackers()

    logging.info("Checking tracker status...")
    status = manager.check_tracker_status()
    logging.info(f'Tracker status: {status}')
except Exception as e:
    logging.error(f"Error running tracker manager: {e}")
    logging.error(f"Traceback: {traceback.format_exc()}")
    sys.exit(1)
"@

    # Save and run the temporary script
    $tempScript = Join-Path $PWD "temp\temp_start_trackers.py"
    Write-Verbose "Creating temporary script: $tempScript"
    $startScript | Out-File -FilePath $tempScript -Encoding utf8
    
    Write-Host "`nStarting TrackerManager..." -ForegroundColor Cyan
    & $pythonPath $tempScript
    
    # Clean up
    Remove-Item $tempScript -ErrorAction SilentlyContinue
    
    Write-Host "`n=== Verifying Tracker Status ===" -ForegroundColor Green
    Write-Host "Running detailed status check..."
    & $pythonPath (Join-Path $PWD "check_status.py")
    
}
catch {
    Write-Error "Error starting trackers: $_"
    exit 1
}

Write-Host "`nDone!" -ForegroundColor Green