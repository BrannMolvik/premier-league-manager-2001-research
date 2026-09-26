param(
    [switch]$Remove
)

$ErrorActionPreference = "Stop"
$TaskName = "FM2001 ChatGPT Auto Continue Watchdog"
$SourceWatchdog = Join-Path $PSScriptRoot "watchdog.ps1"
$InstallDir = Join-Path $env:LOCALAPPDATA "FM2001AutoContinue"
$InstalledWatchdog = Join-Path $InstallDir "watchdog.ps1"
$LauncherPath = Join-Path $InstallDir "watchdog-launcher.vbs"

if ($Remove) {
    schtasks.exe /Delete /TN $TaskName /F 2>$null | Out-Null
    Write-Host "Removed scheduled task: $TaskName"
    exit 0
}

if (-not (Test-Path $SourceWatchdog)) {
    throw "watchdog.ps1 was not found next to this installer."
}

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Copy-Item -Force $SourceWatchdog $InstalledWatchdog

$escapedWatchdog = $InstalledWatchdog.Replace('"', '""')
$launcher = @'
Set shell = CreateObject("WScript.Shell")
command = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""__WATCHDOG__"" -Once"
shell.Run command, 0, False
'@
$launcher = $launcher.Replace("__WATCHDOG__", $escapedWatchdog)
Set-Content -Path $LauncherPath -Value $launcher -Encoding ASCII

$wscript = Join-Path $env:WINDIR "System32\wscript.exe"
$taskCommand = '"' + $wscript + '" "' + $LauncherPath + '"'
schtasks.exe /Create /F /SC MINUTE /MO 3 /TN $TaskName /TR $taskCommand | Out-Null

Write-Host ""
Write-Host "Installed: $TaskName"
Write-Host "Watchdog copy: $InstalledWatchdog"
Write-Host "Hidden launcher: $LauncherPath"
Write-Host "Runs every 3 minutes while Windows Task Scheduler is available without opening a console window."
Write-Host ""
Write-Host "Browser extension still needs to be loaded once in Chrome:"
Write-Host "  $PSScriptRoot\chrome-extension"
Write-Host ""
Write-Host "To test the Windows detector without opening ChatGPT:"
Write-Host '  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "' + $InstalledWatchdog + '" -Once -DryRun'
