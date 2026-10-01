# Automatic Continuation Protocol

This protocol exists so long-running FM2001 work can recover from a ChatGPT
timeout, connection interruption, or conversation-length limit without relying
on the dead conversation.

GitHub remains the project memory.

## Persistent mission and turn boundaries

The autonomous assignment is **finish every remaining roadmap gate through
Gate 17**, including the verified Windows 11 release audit. A currently active
gate or task narrows *what the next action should be*; it never narrows the
assignment's completion condition. Closing a gate, making a commit, passing a
focused test, or completing one ChatGPT response is not project completion.

While meaningful source-backed work remains feasible in a worker response,
continue to the next step without asking the user for another "continue".
Checkpoint roughly every ten minutes, not once per response or as a reason
to end a response. A finite chat/tool session cannot guarantee indefinite
execution; persist the exact next action and keep the runtime in `working`
when a session ends but Gate 17 is not finished. The local recovery extension
may then resume after its normal health/lease checks.

Do not generate unnecessary commits, fabricate recovered source behavior, or
repeatedly run an impossible task merely to keep a session active. If genuine
infrastructure failure blocks all productive work, document the specific
failed operation and preserve the next executable action. Use
`waiting_for_user` only when user intervention is genuinely required, not
simply because a sandbox or tool is temporarily unavailable.

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
  - `completed` - the overall autonomous objective is genuinely finished. Completing a subtask or roadmap gate is **not** enough; advance to the next canonical task/gate when one is defined.
- `checkpoint_target_minutes`: normal maximum interval between recoverable
  project checkpoints.
- `stale_after_minutes`: inactivity interval after which a local watchdog may
  conclude that a `working` session died.
- `recovery_cooldown_minutes`: minimum delay before another recovery launch.
- `max_recoveries_per_hour`: loop guard.
- `active_generation_grace_minutes`: extra protection for a visibly generating response after the repository heartbeat is already stale. The default is 10 minutes, so a stuck Stop-generating UI cannot suppress recovery for an hour.\n- `same_chat_fallback_minutes`: grace period after the first in-place recovery before a no-progress session may escalate to a fresh background chat.

Automatic recovery is allowed only when all are true:

1. `enabled == true`;
2. `mode == "continuous"`;
3. `status == "working"`.

No restart should occur while the state says `waiting_for_user`, `paused`, or
`completed`.

## CI and billing policy

A GitHub `main` or `agent-runtime` commit remains a watchdog heartbeat and
durable progress checkpoint. It does **not** need to start an Actions runner.
CI is intentionally cost-controlled: focused Gate 13 checks are manually
dispatched at meaningful milestones (or run on integration pull requests), the
full reconstruction suite runs manually at gate audits, and unrelated
watchdog/asset checks run on relevant pull requests or manual request.

### Branch-specific workflow guard

GitHub evaluates workflow triggers from the ref being pushed, not from the
latest workflow copy on `main`. The long-lived `agent-runtime` branch
originally retained an older `.github/workflows/asset-policy.yml` with
unconditional `on: push`, so every otherwise cost-controlled worker
heartbeat incorrectly launched an Actions runner despite newer `main`
settings. This was confirmed by GitHub run `36725611674`
(event `push`, branch `agent-runtime`) and corrected on the runtime
branch in commit `2d48b1a3edaf80c782a17ad67bc2a4d16157d9af`.
Its asset-policy workflow now matches the cost-controlled `main` blob
`a01ae95ac39812dc2a740bce0060ce7cfb9a0cd8` and has **no push trigger**.

If recreating or resetting `agent-runtime`, compare its own workflow files
against the current cost-controlled equivalents before starting heartbeats.
Do not assume changes on `main` automatically replace existing workflows
on the runtime branch. Only the runtime state file belongs in ordinary
heartbeat commits.

Never dispatch extra workflows merely as heartbeat signals. If GitHub Actions
included minutes are exhausted, use available local tests and preserve the
unverified CI boundary until another authorized verification opportunity.
Preserve 10-minute checkpoint guidance only when there is useful evidence or
a genuine unresolved investigation to save; avoid commit spam.

## What counts as a heartbeat

The watchdog treats only the worker-owned `agent-runtime` branch as a liveness
heartbeat. An unrelated `main` commit is not proof the worker is alive. After
meaningful verified `main` checkpoints, the worker must also update its
`agent-runtime` checkpoint within the normal ten-minute interval.

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
5. continue the exact active task as the next step of the full Gate-17 mission;
6. after each verified task, continue to the next canonical source-backed
   task while the current session can still do useful work;
7. checkpoint to `main` at the normal persistence boundaries.

### During autonomous work

Do not rely on the conversation as durable state.

A main-branch checkpoint must contain enough evidence and an exact next step for
a fresh session to continue. If the live resume point changes, update
`CURRENT_STATE.md` / `project_status.json` as already required.

### Intentionally stopping

Before intentionally stopping because a specific user input/action is
required, update the runtime state to `waiting_for_user` and state precisely
what is required. A temporary tool outage or ordinary end of a worker response
does not by itself meet that condition.

If the user explicitly pauses work, use `paused`.

Only when Gate 17's final release criteria have actually been verified,
use `completed`. Completing a narrower task or intermediate gate is not
sufficient.

If the session dies before making this transition, it will remain `working`,
which is exactly what lets the watchdog recover it.

## Local recovery watcher

The local recovery layer has two cooperating parts:

- `tools/auto_continue/watchdog.ps1` is a deterministic Windows-side lease
  monitor. It survives a dead ChatGPT tab, checks whether a session marked
  `working` has stopped producing repository checkpoints, and logs stale
  conditions. It deliberately **never launches or focuses Chrome**.
- the Chromium extension under `tools/auto_continue/chrome-extension/`
  polls the repository while Chrome is running, watches the ChatGPT UI, and
  opens/submits replacement chats as inactive background tabs.

Installation is documented in `tools/auto_continue/README.md`.

It uses two independent failure signals:

### 1. Explicit ChatGPT UI failure

While a ChatGPT page is open, the content script watches newly inserted
non-message UI elements for interruption/length-limit signals such as:

- connection interruption;
- Retry / Try again / response-generation failure;
- conversation too long / maximum conversation length;
- prompts to start a new chat to continue.

It deliberately ignores text inside user/assistant message containers so old
messages discussing a timeout do not cause a false recovery.

When such a signal appears while runtime status is `working`, recovery may start immediately. Transient interruption/stall signals recover **inside the same worker conversation**. The extension clicks the ChatGPT Stop/Stop generating control if present, then submits a short continuation prompt in that conversation. A new conversation is reserved for a confirmed conversation-length/max-length condition.

### 2. Repository inactivity lease

Every few minutes both the Windows watchdog and, while Chrome is running, the
browser extension read the runtime state plus GitHub's commit Atom feeds (not
the rate-limited REST branch endpoint) for:

- runtime state from `agent-runtime`;
- latest worker heartbeat commit time on `agent-runtime` only.

The `main` branch remains the canonical technical project state, but is not a
live-worker heartbeat because unrelated work can change it.

If the state is `working` and neither branch has activity within `stale_after_minutes`, the browser extension treats the previous work session as stalled even when the ChatGPT UI never displayed an explicit error. It first reuses the recorded worker tab, stops any still-running generation, and re-prompts in the same conversation. Only when that worker tab no longer exists may it create a replacement ChatGPT tab with `active: false`.

The Windows watchdog remains an independent detector/logging path if the old
ChatGPT tab is gone, but it never opens or focuses Chrome. If Chrome is fully
closed, recovery is intentionally deferred until Chrome is opened again. This
prevents autonomous recovery from interrupting a fullscreen game or stealing
focus from other foreground work.

## Recovery action

When recovery is triggered, the local watcher:

1. enforces cooldown and per-hour loop limits;
2. fetches the latest `research/HANDOFF_PROMPT.md` from `main`;
3. for transient/stale recovery, reuse the recorded worker tab, stop generation if needed, and submit a short continuation prompt there;
4. only for a true chat-length limit or missing worker tab, open a new `https://chatgpt.com/` tab in the background (`active: false`) and insert the canonical handoff;
5. send the recovery prompt when the ChatGPT composer is available.

The new session is instructed to verify current `main`, read the canonical
state, mark runtime status `working`, and continue without asking the user to
reconstruct the old chat.

If ChatGPT is signed out, the prompt remains pending locally and the extension
keeps retrying after sign-in.

## Loop safety

The default runtime configuration uses:

- checkpoint target: 10 minutes;
- stale threshold: 15 minutes;\n- active-generation grace after stale detection: 10 minutes;\n- recovery cooldown: 20 minutes;
- maximum recoveries: 3 per hour.

The extension stores recovery cooldown/history in Chrome local storage as a
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

The automatic browser recovery is best-effort because ChatGPT UI selectors can
change. The repository inactivity signal remains independent of those selectors.
The Windows watchdog can still detect/log a stopped worker if the old tab is
gone, but it intentionally will not launch Chrome. When Chrome is running, the
extension uses several composer/send-button fallbacks for the final prompt
submission.

If a future ChatGPT UI update breaks automatic prompt insertion, the repository
still contains a complete recovery prompt and exact current state; only the
last local UI step needs repair.


## Same-chat recovery rule

From extension version 0.3.1 onward:

- Connection interruption, timeout, Retry / Try again, stalled response, or stale repository heartbeat: **reuse the existing worker chat**.
- If ChatGPT is still generating, click the visible Stop / Stop generating control first.
- True conversation-length / maximum-length exhaustion: create a fresh background chat and use the canonical GitHub handoff.
- Missing or closed worker tab: a fresh background chat is an allowed fallback.
- If an in-place recovery produces no `main` or `agent-runtime` heartbeat for `same_chat_fallback_minutes` (default 20), a fresh inactive background chat is also allowed even if the old tab still exists.
- Repeated same-chat attempts must not reset that fallback clock.


### Retry-state handling

Version 0.3.1 treats an explicit ChatGPT `Retry` / `Try again` control as a transient failure. It also scans already-rendered error controls when the content script starts. If Retry has left the composer unavailable, the extension may activate Retry only long enough for ChatGPT to expose a Stop control, cancel that generation, and then submit the continuation prompt in the same conversation. Heartbeat checks use commit Atom feeds so the Windows watchdog and browser extension do not collectively exhaust GitHub's unauthenticated REST branch-request allowance.


### No-progress escalation

From version 0.3.2, the first accepted same-chat recovery records the latest repository activity and starts a fallback window. Any later commit to `main` or `agent-runtime` proves forward progress and clears the window. If no commit appears for the configured interval (20 minutes by default), the extension may create one new inactive ChatGPT recovery tab using the canonical handoff. This prevents a permanently wedged Retry/stall UI from blocking unattended work indefinitely while still preferring the existing conversation first.


### Execution-sandbox failure handling

From extension version 0.4.0, a visible ChatGPT execution failure matching
`Analysis errored` or `caas.internal.errors.ClientError` is treated as a
separate sandbox failure rather than an ordinary transient response failure.

Observed project evidence showed that a registered worker conversation could
retain a failing CAAS execution allocation while a different ChatGPT
conversation on the same account successfully launched trivial shell and
Python processes. Therefore a sandbox failure immediately creates a fresh
inactive background worker chat using the canonical GitHub handoff instead of
first re-prompting the same conversation. Network/Retry/interruption signals
continue to prefer same-chat recovery.

Failure detection ignores text inside normal user/assistant message containers,
so repository notes or user discussion containing the error string cannot
trigger a false recovery.
