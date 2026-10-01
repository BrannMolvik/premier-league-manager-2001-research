# Continuation Instructions

## Read this first

This repository is designed so that work can continue safely across ChatGPT, Codex, and local-agent sessions.

A conversation timeout is not a reason to restart the investigation. **GitHub is the project memory.**

**Permanent assignment:** finish the entire FM2001 modernization through
Gate 17, not merely the current gate or the next item in `CURRENT_STATE.md`.
Each gate's exact next task is the next action within this larger mission.
When a verified subtask finishes, take the next available source-backed step
in the same session if possible. When a gate passes its audit, advance to the
next roadmap gate without waiting for another user instruction. End the
runtime with `completed` only after Gate 17 passes; otherwise preserve the
exact next action and allow normal recovery across finite sessions.


## Source-of-truth hierarchy

Use these files for different purposes:

1. `ROADMAP.md` - long-term gates and completion criteria.
2. `research/CURRENT_STATE.md` - short authoritative live resume point.
3. `project_status.json` - machine-readable mirror of the current gate/status.
4. `research/FINDINGS.md` and topic-specific research - established technical evidence.
5. `research/PROGRESS.md` - chronological historical log, including old status statements that may have been superseded.
6. `research/BACKLOG.md` - useful work deliberately deferred.
7. `research/FIDELITY_GAPS.md` - known observable deviations/fallbacks.
8. `research/ORIGINAL_SOURCE_LOCATOR.md` - durable private-source locator and mandatory recovery procedure for the authorized original FM2001 archive/disc image.

When an old milestone in `PROGRESS.md` conflicts with `CURRENT_STATE.md`, treat the old milestone as historical unless later evidence re-establishes it.

## Required startup procedure

Before doing new work:

1. Check the current `main` HEAD.
2. Read `ROADMAP.md`.
3. Read `research/CURRENT_STATE.md`.
4. Read this file.
5. Inspect commits newer than the technical baseline recorded in `CURRENT_STATE.md`.
6. Read only the relevant `FINDINGS.md`, topic-specific research, and historical `PROGRESS.md` sections needed for the active task.
7. Check the relevant test/CI state before claiming that current code passes.
8. If the active task needs `FOOTBAL.EXE`, canonical game files, disc-image evidence, or another original binary resource, read `research/ORIGINAL_SOURCE_LOCATOR.md` and attempt its private Library recovery procedure before reporting that source material is unavailable.
9. State the active gate and exact next task, then continue from there.

Do **not** read the entire multi-thousand-line `PROGRESS.md` as a prerequisite unless a task genuinely requires the full chronology.

A reusable prompt for a fresh session is stored in `research/HANDOFF_PROMPT.md`.

## One-gate rule

Only one roadmap gate should be active at a time.

If an unrelated but useful lead appears:

1. record it in `research/BACKLOG.md`;
2. add it to `research/FIDELITY_GAPS.md` if it is an observable reconstruction deviation;
3. return to the active gate.

Do not begin a new subsystem merely because its code or executable path is interesting.

## Cost-controlled validation

GitHub commit checkpoints and GitHub Actions runs are separate. Preserve useful
recoverable research/code checkpoints roughly every ten minutes during active
investigations, but do not dispatch Actions for each small commit.

- Run relevant quick tests locally whenever execution tools are available.
- For direct main-branch work, request the focused workflow
  `.github/workflows/gate13-tests.yml` manually at a verified Gate 13
  integration milestone rather than after each commit.
- Request the complete `.github/workflows/reconstruction-tests.yml` manually
  at gate-completion audits, when a relevant regression warrants it, and before
  releases. Do not invoke the known-failing full suite repeatedly merely to
  reproduce the same two established secondary-schedule failures.
- Pull requests validate impacted focused workflows and applicable asset
  policy, with concurrent superseded runs cancelled.
- If monthly GitHub Actions billing limits block CI, run available local tests,
  record the exact unverified boundary, and defer cloud CI rather than consume
  paid Actions minutes without explicit authorization.
- Do not reduce technical-quality gates or label an unexecuted test as passed.
  Record the last *verified* test commit and workflow run in `CURRENT_STATE.md`.

Don't make empty or artificial commits to create heartbeats; checkpoint
real evidence and leave clear continuation state.

## Persistence requirement

Do not keep important discoveries only in conversational reasoning.

Commit:

- immediately after each verified subproblem or corrected interpretation;
- before switching to a different subsystem;
- after a meaningful implementation/test block;
- during a long unresolved trace after roughly ten minutes, even if the investigation is incomplete;
- before a risky or long operation likely to outlive the session.

A timeout should lose at most one small analysis block.

## What belongs where

- `ROADMAP.md`: project gates, sequencing, and definition of done.
- `CURRENT_STATE.md`: current gate, live implementation boundary, exact next task.
- `PROGRESS.md`: dated chronological checkpoints.
- `FINDINGS.md`: verified reusable discoveries.
- `FIDELITY_GAPS.md`: known differences, approximations, and deterministic fallbacks.
- `BACKLOG.md`: deferred work and side leads.
- `FAILED_APPROACHES.md`: disproven, unsuccessful, or inconclusive attempts.
- `EXECUTABLE_ANALYSIS.md`: PE structure, code paths, APIs, addresses, disassembly/decompiler notes.
- `FILE_FORMATS.md`: game data, database, save, resource, archive, and configuration formats.
- `RUNTIME_COMPATIBILITY.md`: launch behavior, Windows compatibility, graphics/audio/runtime dependencies, wrappers, patches.
- `tools/`: research/validation scripts that do not contain copyrighted game assets.
- `extracted/`: small legal-to-store derived metadata only, never an uncontrolled original-asset dump.
- `reconstruction/`: modern replacement/runtime implementation (historical directory name; original assets may be reused by the port).
- `original_assets/`: intentionally imported authorized original resources and their provenance manifest.

## Evidence discipline

Clearly separate:

- **Confirmed**: directly verified.
- **Probable**: strong evidence but not fully proven.
- **Hypothesis**: plausible explanation awaiting a test.
- **Fallback**: deterministic reconstruction behavior used while original behavior is unresolved.
- **Approximation**: intentionally incomplete model of a recovered original path.

A chat conclusion is provisional until it is persisted with enough evidence that another session can reproduce it.

## Original-resource and repository rule

The project owner has confirmed authorization to reuse the contents of the supplied FM2001 archive/disc image.

Original FM2001 resources and recovered original behavior are the default source of truth. If an original asset, layout, string, audio/video resource, data value, timing/navigation rule, or behavior is accessible, use it directly or through the minimum compatibility/conversion/wrapper layer required for Windows 11. Do not substitute or redesign original material merely for convenience, implementation speed, aesthetics, or modernization preference. Replacement is allowed only when the original is technically incompatible after reasonable adaptation or genuinely inaccessible/unrecoverable; document that boundary in the appropriate research/fidelity file. Intentionally imported source assets belong under `original_assets/` and should be provenance-tracked according to `research/ASSET_POLICY.md`.

Do not commit raw full-disc images, duplicate archive copies, temporary extraction dumps, reverse-engineering databases, or cache/build noise. The repository asset-policy CI check enforces placement/hygiene rules; it is not a ban on authorized original resources.

### Durable original-source recovery

The authorized original disc-image archive has a durable private locator in `research/ORIGINAL_SOURCE_LOCATOR.md`. A missing temporary extraction, expired sandbox, lost local shortcut, new worker, or new chat is not evidence that the original source is unavailable.

Before any worker pauses for or asks the user to re-upload `FOOTBAL.EXE` or the original FM2001 source archive:

1. read `research/ORIGINAL_SOURCE_LOCATOR.md`;
2. if ChatGPT Files/Library access is available, resolve and materialize the exact Library source recorded there;
3. recover the required canonical files into the current temporary workspace using the repository's source-access tooling;
4. only declare an external source blocker if that documented recovery route was attempted and failed, or if the current execution environment genuinely has no access to the recorded private source.

Never guess source behavior merely to avoid performing this recovery step.

## Gate completion procedure

Before advancing gates:

1. check every completion criterion in `ROADMAP.md`;
2. run/inspect the relevant tests and CI;
3. reconcile any new fidelity gaps;
4. update `PROGRESS.md` with the completion checkpoint;
5. update `CURRENT_STATE.md` and `project_status.json`;
6. mark the completed gate and new active gate in `ROADMAP.md`;
7. commit the transition.

## Timeout protocol

If a session must stop mid-task:

1. stop at a safe intermediate point;
2. persist useful scripts/output that are legal to store;
3. update the relevant research notes;
4. append a chronological checkpoint to `PROGRESS.md`;
5. put the exact next address/command/test in `CURRENT_STATE.md` if the live resume point changed;
6. commit and push.

The next session should continue from that checkpoint rather than reconstructing the previous chat.


## Deferred blocker and out-of-order work policy

Roadmap gates are **verification milestones**, not a rule that all productive work
must stop when one gate contains a temporarily blocked local/private task.

When the exact next task requires unavailable local Windows GUI access, the
private executable/source archive, or a functioning execution sandbox:

1. Record the task as a deferred blocker with the exact missing evidence/action.
2. Do not mark that criterion complete and do not infer missing original behavior.
3. Continue the highest-priority independent **cloud-safe** task elsewhere in
   the current gate or a later gate.
4. Work ahead only where the task does not depend on the unresolved blocker.
5. Keep the earliest incomplete gate as the active validation gate until all of
   its completion criteria are actually satisfied.
6. Later-gate implementation/tests may advance out of order, but a later gate
   must not be declared passed if its own criteria or an earlier prerequisite
   remain unresolved.
7. Revisit deferred blockers whenever a sustained private/local execution path
   becomes available, and clear every deferred blocker before the relevant gate
   is closed.

Useful cloud-safe work-ahead examples include already-evidenced presentation
integration, deterministic/fail-closed tests, repository-side fidelity work,
long-duration/destructive simulation testing, packaging/audit tooling, and
documentation of verified behavior. Do not use this policy to bypass missing
source evidence, Windows graphical verification, or original-resource
provenance.

