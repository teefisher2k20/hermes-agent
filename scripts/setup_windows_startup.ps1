# Setup Hermes Agent Dashboard auto-start on Windows startup
Param(
    [switch]$Uninstall,
    [int]$Port = 9119
)

$ErrorActionPreference = "Stop"
$TaskName = "HermesAgentDashboard"
$RepoPath = (Resolve-Path "$PSScriptRoot\..").Path

if ($Uninstall) {
    Write-Host "Removing $TaskName startup task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    $StartupFile = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup\HermesDashboard.vbs"
    if (Test-Path $StartupFile) { Remove-Item $StartupFile -Force }
    Write-Host "Uninstalled successfully." -ForegroundColor Green
    exit 0
}

Write-Host "Configuring Hermes Agent Dashboard for Windows startup..." -ForegroundColor Cyan

# Find python executable
$PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $PythonExe) {
    Write-Error "Python executable not found in PATH."
    exit 1
}

# 1. Register Scheduled Task for AtLogOn
try {
    $Action = New-ScheduledTaskAction -Execute $PythonExe -Argument "-m hermes_cli.main dashboard --port $Port --tui --no-open --skip-build" -WorkingDirectory $RepoPath
    $Trigger = New-ScheduledTaskTrigger -AtLogOn
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 0)

    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Launches Hermes Agent Dashboard on Windows startup" -Force | Out-Null
    Write-Host "Registered Scheduled Task '$TaskName' to run at logon." -ForegroundColor Green
} catch {
    Write-Warning "Could not register Scheduled Task: $_. Falling back to Startup folder script."
}

# 2. Create VBScript launcher in Windows Startup folder
$StartupFile = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup\HermesDashboard.vbs"
$VbsContent = @"
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "$RepoPath"
WshShell.Run "$PythonExe -m hermes_cli.main dashboard --port $Port --tui --no-open --skip-build", 0, False
"@
Set-Content -Path $StartupFile -Value $VbsContent -Encoding UTF8
Write-Host "Created Startup shortcut at: $StartupFile" -ForegroundColor Green

Write-Host "Hermes Agent Dashboard is now configured to load on Windows startup!" -ForegroundColor Green
