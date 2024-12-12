# PowerShell script to watch for file changes and update documentation

$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $env:CONDA_PREFIX "python.exe"

# Add robust logging and file protection
$logPath = Join-Path $projectRoot "logs/documentation_watcher.log"
$lockFile = Join-Path $projectRoot "tools/.watcher.lock"

# Ensure single instance
if (Test-Path $lockFile) {
    $lockContent = Get-Content $lockFile
    $existingPid = $lockContent -as [int]
    if ($existingPid -and (Get-Process -Id $existingPid -ErrorAction SilentlyContinue)) {
        Write-Host "Watcher is already running with PID: $existingPid"
        exit
    }
}
$PID | Set-Content $lockFile

# Set up logging
function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Add-Content $logPath
    Write-Host "$timestamp - $Message"
}

# Function to generate documentation
function Update-Documentation {
    try {
        Write-Log "Starting documentation update..."
        
        # Verify file integrity
        $integrityCheck = @(
            (Join-Path $projectRoot "tools/changelog_generator.py"),
            (Join-Path $projectRoot "tools/code_metrics.py"),
            (Join-Path $projectRoot "tools/structure_viz.py")
        )
        
        foreach ($file in $integrityCheck) {
            if (-not (Test-Path $file)) {
                throw "Critical file missing: $file"
            }
        }
        
        Write-Log "Generating documentation..."
        & $pythonPath (Join-Path $projectRoot "tools/changelog_generator.py") $projectRoot
        
        # Generate code metrics
        Write-Log "Generating code metrics..."
        & $pythonPath (Join-Path $projectRoot "tools/code_metrics.py")
        
        # Generate project structure visualization
        Write-Log "Generating project structure visualization..."
        & $pythonPath (Join-Path $projectRoot "tools/structure_viz.py")
        
        # Run sphinx-build if available
        $sphinxBuild = Join-Path $env:CONDA_PREFIX "Scripts/sphinx-build.exe"
        if (Test-Path $sphinxBuild) {
            Write-Log "Building Sphinx documentation..."
            & $sphinxBuild -b html (Join-Path $projectRoot "docs") (Join-Path $projectRoot "docs/_build/html")
        }
        
        Write-Log "Documentation update completed successfully"
    }
    catch {
        Write-Log "Error during documentation update: $_"
        # Retry logic
        Start-Sleep -Seconds 5
        try {
            Write-Log "Retrying documentation update..."
            & $pythonPath (Join-Path $projectRoot "tools/changelog_generator.py") $projectRoot
            & $pythonPath (Join-Path $projectRoot "tools/code_metrics.py")
            & $pythonPath (Join-Path $projectRoot "tools/structure_viz.py")
            if (Test-Path $sphinxBuild) {
                & $sphinxBuild -b html (Join-Path $projectRoot "docs") (Join-Path $projectRoot "docs/_build/html")
            }
        }
        catch {
            Write-Log "Retry failed: $_"
            # Alert via Windows Event Log
            Write-EventLog -LogName Application -Source "CognitiveAIDocWatcher" -EventId 1001 -EntryType Error -Message "Documentation update failed after retry: $_"
        }
    }
}

# Initial documentation generation
Update-Documentation

# Watch for changes
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $projectRoot
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true
$watcher.NotifyFilter = [System.IO.NotifyFilters]::LastWrite -bor [System.IO.NotifyFilters]::FileName

# Enhanced file watcher with debouncing
$script:lastRun = [DateTime]::MinValue
$script:debounceSeconds = 5

$action = {
    $path = $Event.SourceEventArgs.FullPath
    $changeType = $Event.SourceEventArgs.ChangeType
    $timeStamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    
    # Debounce logic
    $now = [DateTime]::Now
    if (($now - $script:lastRun).TotalSeconds -lt $script:debounceSeconds) {
        Write-Log "Debouncing change event for: $path"
        return
    }
    
    Write-Log "[$timeStamp] $changeType detected in: $path"
    $script:lastRun = $now
    
    # File protection check
    try {
        $criticalPaths = @(
            (Join-Path $projectRoot "tools"),
            (Join-Path $projectRoot "docs"),
            (Join-Path $projectRoot "core")
        )
        
        if ($changeType -eq "Deleted" -and ($criticalPaths | Where-Object { $path.StartsWith($_) })) {
            Write-Log "WARNING: Critical file deletion detected: $path"
            # Alert via Windows Event Log
            Write-EventLog -LogName Application -Source "CognitiveAIDocWatcher" -EventId 1002 -EntryType Warning -Message "Critical file deletion detected: $path"
            return
        }
        
        Update-Documentation
    }
    catch {
        Write-Log "Error handling file change: $_"
    }
}

# Create Event Log source if it doesn't exist
if (-not [System.Diagnostics.EventLog]::SourceExists("CognitiveAIDocWatcher")) {
    New-EventLog -LogName Application -Source "CognitiveAIDocWatcher"
}

# Register event handlers
Register-ObjectEvent $watcher "Created" -Action $action
Register-ObjectEvent $watcher "Changed" -Action $action
Register-ObjectEvent $watcher "Deleted" -Action $action
Register-ObjectEvent $watcher "Renamed" -Action $action

Write-Log "Watching for changes in $projectRoot..."
Write-Log "Press Ctrl+C to stop"

# Cleanup on exit
$exitHandler = {
    Write-Log "Stopping documentation watcher..."
    Remove-Item $lockFile -Force -ErrorAction SilentlyContinue
}
Register-EngineEvent PowerShell.Exiting -Action $exitHandler | Out-Null

# Keep the script running
while ($true) { Start-Sleep -Seconds 1 }
