# FM2001 ChatGPT Auto Continue

This folder contains the local recovery layer for long-running FM2001 work.

It has two parts:

- `watchdog.ps1`: Windows-side lease monitor. It checks GitHub every three minutes through Task Scheduler and opens a recovery ChatGPT page when a session marked `working` has stopped checkpointing.
- `chrome-extension/`: watches the ChatGPT page for explicit interruption / conversation-length errors and submits the canonical repository handoff into a fresh chat.

GitHub remains the source of truth. The recovery system does not try to scrape the previous conversation transcript.

## Install on Windows

First pull the latest `main` branch in the local repository.

### 1. Load the Chrome extension

1. Open `chrome://extensions/`.
2. Turn on **Developer mode**.
3. Click **Load unpacked**.
4. Select:
   `tools\auto_continue\chrome-extension`
5. Leave the extension enabled.

The extension only has access to `chatgpt.com`, the public GitHub API/raw files, local extension storage, alarms, and tabs.

### 2. Install the Windows watchdog

From PowerShell in the repository root:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\auto_continue\Install-AutoContinue.ps1
```

This copies the watchdog to:

`%LOCALAPPDATA%\FM2001AutoContinue\watchdog.ps1`

and creates a Task Scheduler entry named:

`FM2001 ChatGPT Auto Continue Watchdog`

It checks every three minutes.

### 3. Verify installation

Open Task Scheduler and confirm the task exists, or run:

```powershell
Get-ScheduledTask -TaskName "FM2001 ChatGPT Auto Continue Watchdog"
```

The log is written to:

`%LOCALAPPDATA%\FM2001AutoContinue\watchdog.log`

A harmless detector-only test is:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$env:LOCALAPPDATA\FM2001AutoContinue\watchdog.ps1" -Once -DryRun
```

When runtime state is `waiting_for_user`, `paused`, or `completed`, the test should report that monitoring is idle and must not open a new chat.

## Runtime behavior

Runtime control lives on the separate `agent-runtime` branch in:

`research/AUTO_CONTINUE_STATE.json`

Automatic recovery occurs only when:

- `enabled` is true;
- `mode` is `continuous`;
- `status` is `working`.

Normal project commits on `main` act as heartbeats. The default checkpoint target is 10 minutes and stale threshold is 15 minutes.

If ChatGPT explicitly displays a connection interruption or conversation-length failure, the extension may recover immediately rather than waiting for the lease timeout.

If the page disappears silently, the Windows watchdog notices the missing repository heartbeat, opens a new ChatGPT page, and the extension submits the recovery prompt there.

## Safety

The system has two loop guards:

- recovery cooldown (default 20 minutes);
- maximum recovery attempts (default 3 per hour).

The browser extension also stores its own recovery history, independent of the Windows watchdog.

It never auto-recovers while the runtime state says `waiting_for_user`, `paused`, or `completed`.

## Disable / uninstall

To stop automatic recovery without uninstalling it, set runtime status to `paused` or mode to `manual`.

To remove the scheduled task:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\auto_continue\Install-AutoContinue.ps1 -Remove
```

Then remove the unpacked extension from `chrome://extensions/` if desired.
