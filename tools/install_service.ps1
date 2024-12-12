# Run this script as Administrator to install the documentation watcher as a service
$serviceName = "CognitiveAIDocWatcher"
$projectRoot = Split-Path -Parent $PSScriptRoot
$serviceScript = Join-Path $projectRoot "tools\watch_changes.ps1"

# Create service wrapper
$wrapper = @"
using System.ServiceProcess;
using System.Diagnostics;
using System;

public class DocWatcherService : ServiceBase
{
    private Process watcherProcess;

    public DocWatcherService()
    {
        this.ServiceName = "$serviceName";
    }

    protected override void OnStart(string[] args)
    {
        watcherProcess = new Process();
        watcherProcess.StartInfo.FileName = "powershell.exe";
        watcherProcess.StartInfo.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$serviceScript`"";
        watcherProcess.StartInfo.UseShellExecute = false;
        watcherProcess.StartInfo.RedirectStandardOutput = true;
        watcherProcess.StartInfo.CreateNoWindow = true;
        watcherProcess.Start();
    }

    protected override void OnStop()
    {
        if (watcherProcess != null && !watcherProcess.HasExited)
        {
            watcherProcess.Kill();
            watcherProcess.WaitForExit();
        }
    }
}
"@

# Compile service wrapper
Add-Type -TypeDefinition $wrapper -OutputAssembly "$projectRoot\tools\DocWatcherService.exe" -OutputType ConsoleApplication -ReferencedAssemblies "System.ServiceProcess"

# Install service
New-Service -Name $serviceName `
            -BinaryPathName "$projectRoot\tools\DocWatcherService.exe" `
            -DisplayName "Cognitive AI Documentation Watcher" `
            -Description "Maintains real-time documentation updates for Cognitive AI project" `
            -StartupType Automatic

# Set recovery options
$action = New-SC-RecoveryAction -Type "RestartService" -Delay 60000
Set-ServiceRecoveryOption -Name $serviceName -RecoveryAction $action

Write-Host "Service installed successfully. Starting service..."
Start-Service -Name $serviceName
