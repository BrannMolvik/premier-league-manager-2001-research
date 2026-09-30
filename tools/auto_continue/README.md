# FM2001 ChatGPT Auto Continue

This folder contains the local recovery layer for long-running FM2001 work.

It has two parts:

- `watchdog.ps1`: Windows-side lease monitor. It checks GitHub commit Atom feeds every three minutes through Task Scheduler, logs stale sessions, and deliberately never launches or focuses Chrome.
- `chrome-extension/`: checks the independent worker-owned `agent-runtime` commit feed every three minutes while Chrome is running, and handles recovery of the designated ChatGPT worker.

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


## Recovery policy from version 0.3.2

- Transient timeout / connection interruption / Retry / Try again: reuse the existing worker conversation.
- Silent stale repository heartbeat: reuse the recorded worker conversation first. If that recovery produces no repository activity for 30 minutes, open one fresh inactive recovery tab.
- True conversation-length / maximum-length limit: create a fresh background conversation using the canonical GitHub handoff.
- Missing/closed worker tab: a fresh background conversation is an allowed fallback.
- Extension reload/update clears any stale pending recovery prompt from the previous version.


Version 0.3.1 also scans already-rendered error controls on page load, so reloading a ChatGPT tab that is already sitting on Retry can trigger recovery without waiting for a new DOM mutation. Heartbeat polling uses GitHub commit Atom feeds instead of repeated REST branch calls to avoid unauthenticated API throttling.


Version 0.3.2 adds a timed escalation guard. The first same-chat recovery starts a 30-minute progress window (configurable through `same_chat_fallback_minutes`). Repeated same-chat attempts do not reset that window. Any new `main` or `agent-runtime` commit clears it. If the window expires with no repository progress, the extension may open a fresh `active: false` ChatGPT recovery tab even when the old worker tab still exists.

## Active-generation protection (version 0.3.3)

A GitHub heartbeat can already be stale when a new/manual worker response begins.
A three-minute alarm must not interpret that existing silence as permission to
click ChatGPT's Stop button while a response is actively generating.

Before *repository-inactivity* recovery, the extension now queries its tracked
worker tab for a live Stop control. When it detects one, stale recovery is
deferred for up to 60 minutes of continuous quiet generation. A new repository
checkpoint resets that quiet-generation window. Explicit ChatGPT network,
Retry, or true chat-length errors retain immediate error-specific recovery.
When no live generation can be verified, the existing 15-minute stale threshold,
20-minute cooldown, and 30-minute no-progress escalation remain in effect.

This is a protective guard, **not a mechanism for forcing ChatGPT to keep
generating**. A worker that voluntarily finishes early, or cannot proceed due
to an execution-container outage, needs a task-level solution rather than
repeatedly restarting the same blocked task.

To activate the change on a PC with an unpacked extension, pull the updated
repository and click **Reload** for the extension at `chrome://extensions/`.
The new version should read `0.3.3`. The Windows watchdog itself is unchanged.

## Full-mission handoff (version 0.3.4)

Both short same-chat and full new-chat watchdog recovery prompts now explicitly
state the durable objective: complete all remaining gates through Gate 17 and
its final Windows 11 release audit. The active Gate-13 subtask is just the
immediate next action. Neither a successful checkpoint nor a finished worker
response marks the mission complete. Continue successive useful work within
each feasible session and preserve the next action for later recoveries.

This does not create an indefinitely running ChatGPT process: sessions still
have finite execution windows, the watchdog still depends on Chrome being
available, and legitimate execution-environment outages must be reported.
After pulling the new branch/main changes, reload the extension in
`chrome://extensions/` and verify version `0.3.4`.


## Register the designated worker tab (version 0.3.5)

The content script is present on all ChatGPT pages, but only the designated
FM2001 worker conversation can trigger an interruption/recovery. This prevents
unrelated ChatGPT conversations from being mistaken for failed FM2001 workers.

1. Pull the newest `main` and click **Reload** on the unpacked extension in
   `chrome://extensions/`. Confirm version **0.3.5**.
2. Open the actual FM2001 worker conversation and select its tab.
3. Click the **FM2001 ChatGPT Auto Continue** icon in Chrome's toolbar
   (pin the extension from the puzzle-piece menu if necessary).
4. An **FM** badge appears on the extension icon for that tab. This records
   the intended worker tab persistently. A replacement chat launched by the
   watchdog is also registered automatically once its recovery prompt is sent.

Clicking the icon from an unrelated website does not register that tab.
Errors on other ChatGPT conversations are ignored; they cannot replace the
recorded worker or initiate an FM2001 recovery.

If Chrome's extension details show a red **Errors** indicator, open its error
details to see the exact message/stack trace. Historical errors may remain
visible even after updating; do not infer the cause from the indicator alone.

## Version 0.3.6: actual worker health diagnostics

Unrelated `main` commits no longer count as a live-worker heartbeat. The
worker must update the `agent-runtime` branch after meaningful `main` checkpoints
and normally within ten minutes while active. The Windows watchdog now agrees.

After pulling `main`, reload the extension and **refresh the actual ChatGPT
worker tab** so stale content scripts do not keep running. On that tab, click
the extension toolbar icon to register it. Open the extension **Details** page,
choose **Extension options**, then **Run health checks** to see GitHub connectivity,
worker liveness, registered tab connectivity and recovery cooldown. No billable
GitHub Actions or ChatGPT prompts are triggered by diagnostics.

A red Chrome Errors indicator can contain historical entries. Click it to view
the exact message; the new diagnostics page can capture future background
service-worker errors but cannot read old Chrome Errors records.

Keep Chrome running, the PC awake and ChatGPT signed in. Browser recovery remains
best-effort and cannot guarantee progress through service outages or unavailable
original source-byte execution.

## 0.3.7 content-script invalidation hardening

An unpacked extension reload does not replace content scripts in already-open
ChatGPT tabs. Old scripts can report `content.js:402` / `onMessage` undefined
and repeated `Extension context invalidated` errors. Version 0.3.7 guards
listener registration and stops the old script's polling interval and
observer after detecting context loss.

**Deployment:** pull `main`, reload the extension, then refresh *all*
already-open ChatGPT tabs, including the FM2001 worker tab. On that tab click
the FM2001 toolbar icon to register it again. Only then clear historical
errors from Chrome's extension Errors page. If new errors appear, capture them.
