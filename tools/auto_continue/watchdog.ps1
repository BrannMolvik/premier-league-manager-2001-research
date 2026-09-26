param(
    [switch]$Once,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$Repo = "BrannMolvik/premier-league-manager-2001-research"
$RuntimeBranch = "agent-runtime"
$MainBranch = "main"
$PollSeconds = 180
$StateDir = Join-Path $env:LOCALAPPDATA "FM2001AutoContinue"
$LocalStatePath = Join-Path $StateDir "watchdog-state.json"
$LogPath = Join-Path $StateDir "watchdog.log"

New-Item -ItemType Directory -Force -Path $StateDir | Out-Null

function Write-WatchdogLog([string]$Message) {
    $line = "[{0}] {1}" -f (Get-Date).ToString("o"), $Message
    Add-Content -Path $LogPath -Value $line
    Write-Host $line
}

function Get-JsonUrl([string]$Url) {
    Invoke-RestMethod -Uri $Url -Headers @{
        "User-Agent" = "FM2001-AutoContinue-Watchdog"
        "Accept" = "application/vnd.github+json"
    } -TimeoutSec 20
}

function Get-RuntimeState {
    $url = "https://raw.githubusercontent.com/$Repo/$RuntimeBranch/research/AUTO_CONTINUE_STATE.json?ts=$([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds())"
    Invoke-RestMethod -Uri $url -Headers @{ "User-Agent" = "FM2001-AutoContinue-Watchdog" } -TimeoutSec 20
}

function Get-BranchActivity([string]$Branch) {
    $url = "https://api.github.com/repos/$Repo/branches/$Branch"
    $data = Get-JsonUrl $url
    $dateText = $data.commit.commit.committer.date
    if (-not $dateText) { $dateText = $data.commit.commit.author.date }
    [PSCustomObject]@{
        Sha = $data.commit.sha
        Timestamp = if ($dateText) { [DateTimeOffset]::Parse($dateText) } else { [DateTimeOffset]::MinValue }
    }
}

function Load-LocalState {
    if (-not (Test-Path $LocalStatePath)) {
        return [PSCustomObject]@{
            lastRecoveryAt = $null
            recoveryHistory = @()
        }
    }
    try {
        return Get-Content -Raw -Path $LocalStatePath | ConvertFrom-Json
    } catch {
        return [PSCustomObject]@{
            lastRecoveryAt = $null
            recoveryHistory = @()
        }
    }
}

function Save-LocalState($State) {
    $State | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 -Path $LocalStatePath
}

function Test-RecoveryGuard($RuntimeState) {
    $local = Load-LocalState
    $now = [DateTimeOffset]::UtcNow
    $cooldown = [int]($RuntimeState.recovery_cooldown_minutes ?? 20)
    $maxPerHour = [int]($RuntimeState.max_recoveries_per_hour ?? 3)

    $history = @()
    foreach ($value in @($local.recoveryHistory)) {
        if (-not $value) { continue }
        try {
            $stamp = [DateTimeOffset]::Parse([string]$value)
            if (($now - $stamp).TotalMinutes -lt 60) { $history += $stamp }
        } catch {}
    }

    if ($local.lastRecoveryAt) {
        try {
            $last = [DateTimeOffset]::Parse([string]$local.lastRecoveryAt)
            if (($now - $last).TotalMinutes -lt $cooldown) {
                return $null
            }
        } catch {}
    }

    if ($history.Count -ge $maxPerHour) {
        return $null
    }

    [PSCustomObject]@{
        Local = $local
        Now = $now
        History = $history
    }
}

function Request-Recovery([string]$Reason, [int]$StaleMinutes, $RuntimeState) {
    $guard = Test-RecoveryGuard $RuntimeState
    if (-not $guard) {
        Write-WatchdogLog "Recovery suppressed by cooldown/rate limit."
        return
    }

    $encodedReason = [Uri]::EscapeDataString($Reason)
    $url = "https://chatgpt.com/?fm2001_auto_recover=1&reason=$encodedReason&stale_minutes=$StaleMinutes"

    if ($DryRun) {
        Write-WatchdogLog "DRY RUN: would open $url"
        return
    }

    Write-WatchdogLog "Recovery requested: $Reason; stale for $StaleMinutes minute(s)."
    Start-Process $url

    $historyStrings = @($guard.History | ForEach-Object { $_.ToString("o") })
    $historyStrings += $guard.Now.ToString("o")
    $newLocal = [PSCustomObject]@{
        lastRecoveryAt = $guard.Now.ToString("o")
        recoveryHistory = $historyStrings
    }
    Save-LocalState $newLocal
}

function Invoke-WatchdogCheck {
    try {
        $runtime = Get-RuntimeState

        $shouldMonitor =
            $runtime.enabled -eq $true -and
            [string]$runtime.mode -eq "continuous" -and
            [string]$runtime.status -eq "working"

        if (-not $shouldMonitor) {
            Write-WatchdogLog "Idle: runtime status=$($runtime.status), mode=$($runtime.mode)."
            return
        }

        $runtimeActivity = Get-BranchActivity $RuntimeBranch
        $mainActivity = Get-BranchActivity $MainBranch
        $latest = if ($runtimeActivity.Timestamp -gt $mainActivity.Timestamp) {
            $runtimeActivity.Timestamp
        } else {
            $mainActivity.Timestamp
        }

        $staleAfter = [int]($runtime.stale_after_minutes ?? 15)
        $staleMinutes = [int][Math]::Floor(([DateTimeOffset]::UtcNow - $latest).TotalMinutes)

        if ($staleMinutes -ge $staleAfter) {
            Request-Recovery "stale-repository-activity" $staleMinutes $runtime
        } else {
            Write-WatchdogLog "Healthy: latest activity $staleMinutes minute(s) ago."
        }
    } catch {
        Write-WatchdogLog "Check failed: $($_.Exception.Message)"
    }
}

do {
    Invoke-WatchdogCheck
    if ($Once) { break }
    Start-Sleep -Seconds $PollSeconds
} while ($true)
