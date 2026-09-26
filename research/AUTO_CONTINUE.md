# Automatic Continuation Protocol

This protocol exists so long-running FM2001 work can recover from a ChatGPT
timeout, connection interruption, or conversation-length limit without relying
on the dead conversation.

GitHub remains the project memory.

## Architecture

Two branches have different responsibilities:

- `main` - canonical technical project state, code, evidence, tests, and normal
  checkpoints.
- `agent-runtime` - ephemeral session-control state only.

The runtime state file is:

`research/AUTO_CONTINUE_STATE.json` on branch `agent-runtime`.

Do not put technical discoveries only on the runtime branch.

## State machine

Relevant runtime fields:

- `enabled`: master switch.
- `mode`: `continuous` allows automatic recovery; `manual` disables it.
- `status`:
  - `working` - an autonomous work session is expected to keep progressing;
  - `waiting_for_user` - work intentionally stopped for user input;
  - `paused` - explicitly paused;
  - `completed` - project/task intentionally finished.
- `checkpoint_target_minutes`: normal maximum interval between recoverable
  project checkpoints.
- `stale_after_minutes`: inactivity interval after which a local watchdog may
  conclude that a `working` session died.
- `recovery_cooldown_minutes`: minimum delay before another recovery launch.
- `max_recoveries_per_hour`: loop guard.

Automatic recovery is allowed only when all are true:

1. `enabled == true`;
2. `mode == "continuous"`;
3. `status == "working"`.

No restart should occur while the state says `waiting_for_user`, `paused`, or
`completed`.

## What counts as a heartbeat

The watchdog treats either of these as recent activity:

1. a new commit on `agent-runtime` (for example a state transition); or
2. a new commit on `main` (normal project checkpoint).

This intentionally reuses the repository's existing persistence rule: during
active investigation, commit every meaningful verified result and checkpoint
roughly every ten minutes if the investigation is still unresolved.

The default stale threshold is 15 minutes, leaving a small grace period beyond
the 10-minute checkpoint target.

## Required ChatGPT / agent behavior

### Starting autonomous work

When the user asks to continue sustained project work:

1. fetch current `main`;
2. read `research/CURRENT_STATE.md`;
3. read this protocol and the runtime state from `agent-runtime`;
4. set runtime `status` to `working` and `mode` to `continuous`;
5. continue the exact active task;
6. checkpoint to `main` at the normal persistence boundaries.

### During autonomous work

Do not rely on the conversation as durable state.

A main-branch checkpoint must contain enough evidence and an exact next step for
a fresh session to continue. If the live resume point changes, update
`CURRENT_STATE.md` / `project_status.json` as already required.

### Intentionally stopping

Before intentionally stopping because user input is required, update the
runtime state to `waiting_for_user`.

If the user explicitly pauses work, use `paused`.

If the relevant autonomous project/task is genuinely finished, use
`completed`.

If the session dies before making this transition, it will remain `working`,
which is exactly what lets the watchdog recover it.

## Local watchdog

The Chromium extension under `tools/auto_continue/chrome-extension/` is the
primary local recovery watcher.

It does two independent checks:

### 1. Explicit ChatGPT UI failure

While a ChatGPT page is open, the content script watches newly inserted
non-message UI elements for interruption/length-limit signals such as:

- connection interruption;
- conversation too long / maximum conversation length;
- prompts to start a new chat to continue.

It deliberately ignores text inside user/assistant message containers so old
messages discussing a timeout do not cause a false recovery.

When such a signal appears while runtime status is `working`, recovery may
start immediately.

### 2. Repository inactivity lease

Every few minutes the extension reads:

- runtime state from `agent-runtime`;
- latest commit time on `agent-runtime`;
- latest commit time on `main`.

If the state is `working` and neither branch has activity within
`stale_after_minutes`, it treats the previous work session as dead even when
the ChatGPT UI never displayed an explicit error.

This catches silent timeouts and disconnected tabs.

## Recovery action

When recovery is triggered, the local watcher:

1. enforces cooldown and per-hour loop limits;
2. fetches the latest `research/HANDOFF_PROMPT.md` from `main`;
3. opens a new `https://chatgpt.com/` tab;
4. inserts an auto-recovery prefix plus the latest handoff prompt;
5. sends it when the ChatGPT composer is available.

The new session is instructed to verify current `main`, read the canonical
state, mark runtime status `working`, and continue without asking the user to
reconstruct the old chat.

If ChatGPT is signed out, the prompt remains pending locally and the extension
keeps retrying after sign-in.

## Loop safety

The default runtime configuration uses:

- checkpoint target: 10 minutes;
- stale threshold: 15 minutes;
- recovery cooldown: 20 minutes;
- maximum recoveries: 3 per hour.

The watchdog stores recovery cooldown/history locally in the browser as a
second guard independent of GitHub.

A recovery must never be triggered solely because a normal conversation became
quiet while runtime status is not `working`.

## Chat-length handling

Conversation-length exhaustion is treated like any other interrupted worker.
The replacement chat does **not** need the old chat transcript. It reconstructs
the project from:

1. current `main` HEAD;
2. `ROADMAP.md`;
3. `research/CURRENT_STATE.md`;
4. `research/CONTINUATION_INSTRUCTIONS.md`;
5. relevant technical research;
6. current test/CI state.

This is why repository state must remain sufficient to resume the project.

## Fallback

The automatic browser restart is best-effort because ChatGPT UI selectors can
change. The repository inactivity signal remains independent of those selectors,
and the extension uses several composer/send-button fallbacks.

If a future ChatGPT UI update breaks automatic prompt insertion, the repository
still contains a complete recovery prompt and exact current state; only the
last local UI step needs repair.
