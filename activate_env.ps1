# Activate Conda environment and set up monitoring
param(
    [switch]$StartTrackers = $false
)

# Activate Conda environment
conda activate cog_ai

# Set CUDA paths
$env:CUDA_PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1"
$env:CUDA_HOME = $env:CUDA_PATH
$env:PATH = "$env:CUDA_PATH\bin;$env:PATH"

# Set Python path
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"

# Create necessary directories
$dirs = @(
    "logs",
    "interaction_logs",
    "test_logs"
)
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir
        Write-Host "Created directory: $dir"
    }
}

# Configure Git (optional)
git config --local core.autocrlf true
git config --local core.eol lf

# Print environment info
Write-Host "Environment activated! Current settings:"
Write-Host "Python: $env:CONDA_PREFIX\python.exe"
Write-Host "CUDA: $env:CUDA_PATH"
Write-Host ""
Write-Host "Available functions:"
Write-Host "- Start-Trackers: Start interaction tracking"
Write-Host "- Stop-Trackers: Stop interaction tracking"
Write-Host "- Run-Tests: Run the test suite"
Write-Host "- Setup-Dev: Set up development environment"
Write-Host "- Clean-Temp: Clean temporary files"
Write-Host ""

# Create PowerShell functions for common commands
function Start-Trackers {
    $python = "$env:CONDA_PREFIX\python.exe"
    Write-Host "Starting trackers..."
    & $python check_trackers.py
}

function Stop-Trackers {
    $processes = Get-Process | Where-Object { $_.ProcessName -like "*python*" -and $_.CommandLine -like "*tracker.py*" }
    foreach ($proc in $processes) {
        Stop-Process -Id $proc.Id -Force
        Write-Host "Stopped tracker process: $($proc.Id)"
    }
}

function Run-Tests { 
    $python = "$env:CONDA_PREFIX\python.exe"
    & $python -m pytest tests/ 
}

function Setup-Dev { 
    pre-commit install
    pip install -e .
}

function Clean-Temp { 
    Get-ChildItem -Path . -Filter "*.pyc" -Recurse | Remove-Item
    Get-ChildItem -Path . -Filter "__pycache__" -Recurse | Remove-Item -Recurse
}

# Optionally start trackers
if ($StartTrackers) {
    Start-Trackers
}
