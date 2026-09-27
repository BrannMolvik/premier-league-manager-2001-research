# FM2001 ChatGPT Auto Continue

This folder contains the local recovery layer for long-running FM2001 work.

It has two parts:

- `watchdog.ps1`: Windows-side lease monitor. It checks GitHub commit Atom feeds every three minutes through Task Scheduler, logs stale sessions, and deliberately never launches or focuses Chrome.
- `chrome-extension/`: checks the same non-REST commit feeds every three minutes while Chrome is running, watches ChatGPT for explicit interruption / Retry / conversation-length errors, and performs same-chat or background recovery according to the failure type.

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

The extension only has access to `chatgpt.com`, GitHub commit pages/Atom feeds, raw GitHub files, local extension storage, alarms, and tabs. It does not depend on the rate-limited public GitHub REST branch endpoint for heartbeat checks. Recovery tabs are created inactive so Chrome does not intentionally take foreground focus.

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

If ChatGPT explicitly displays a transient connection interruption/stall or **Retry / Try again** state, the extension first recovers **in the same worker chat**. It stops a live generation if present. If the page is stuck on Retry and the composer is unavailable, it briefly activates Retry only to expose the Stop control, cancels that generation, then submits the canonical continuation prompt. A new chat is reserved for a confirmed conversation-length/max-length condition.

If the page disappears silently while Chrome is running, the extension notices the missing repository heartbeat and first reuses its recorded worker tab. It stops any still-running generation and submits a continuation prompt in that same conversation. Only if no usable worker tab remains does it create a new ChatGPT recovery tab with `active: false`.

If Chrome is completely closed, the Windows watchdog records the stale condition but **does not launch Chrome**. Recovery resumes after Chrome is opened again. This focus-safe behavior is intentional so auto-continue cannot interrupt a fullscreen game or other foreground work.

## Safety

The system has two loop guards:

- recovery cooldown (default 20 minutes);
- maximum recovery attempts (default 3 per hour).

The browser extension owns both explicit UI-error recovery and silent/stale-session recovery, with one shared cooldown/rate limit. The Windows watchdog is detector/logging-only and never opens the browser.

It never auto-recovers while the runtime state says `waiting_for_user`, `paused`, or `completed`.

## Disable / uninstall

To stop automatic recovery without uninstalling it, set runtime status to `paused` or mode to `manual`.

To remove the scheduled task:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\auto_continue\Install-AutoContinue.ps1 -Remove
```

Then remove the unpacked extension from `chrome://extensions/` if desired.


## Recovery policy from version 0.3.1

- Transient timeout / connection interruption / Retry / Try again: reuse the existing worker conversation.
- Silent stale repository heartbeat: reuse the recorded worker conversation first.
- True conversation-length / maximum-length limit: create a fresh background conversation using the canonical GitHub handoff.
- Missing/closed worker tab: a fresh background conversation is an allowed fallback.
- Extension reload/update clears any stale pending recovery prompt from the previous version.


Version 0.3.1 also scans already-rendered error controls on page load, so reloading a ChatGPT tab that is already sitting on Retry can trigger recovery without waiting for a new DOM mutation. Heartbeat polling uses GitHub commit Atom feeds instead of repeated REST branch calls to avoid unauthenticated API throttling.
