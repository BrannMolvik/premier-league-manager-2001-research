# Continuation Instructions

## Read this first

This repository is designed so that work can continue safely across ChatGPT, Codex, and local-agent sessions.

A conversation timeout is not a reason to restart the investigation. **GitHub is the project memory.**

## Source-of-truth hierarchy

Use these files for different purposes:

1. `ROADMAP.md` - long-term gates and completion criteria.
2. `research/CURRENT_STATE.md` - short authoritative live resume point.
3. `project_status.json` - machine-readable mirror of the current gate/status.
4. `research/FINDINGS.md` and topic-specific research - established technical evidence.
5. `research/PROGRESS.md` - chronological historical log, including old status statements that may have been superseded.
6. `research/BACKLOG.md` - useful work deliberately deferred.
7. `research/FIDELITY_GAPS.md` - known observable deviations/fallbacks.

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
8. State the active gate and exact next task, then continue from there.

Do **not** read the entire multi-thousand-line `PROGRESS.md` as a prerequisite unless a task genuinely requires the full chronology.

A reusable prompt for a fresh session is stored in `research/HANDOFF_PROMPT.md`.

## One-gate rule

Only one roadmap gate should be active at a time.

If an unrelated but useful lead appears:

1. record it in `research/BACKLOG.md`;
2. add it to `research/FIDELITY_GAPS.md` if it is an observable reconstruction deviation;
3. return to the active gate.

Do not begin a new subsystem merely because its code or executable path is interesting.

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

Prefer original resources when they can be used directly or converted for Windows 11 compatibility. Intentionally imported source assets belong under `original_assets/` and should be provenance-tracked according to `research/ASSET_POLICY.md`.

Do not commit raw full-disc images, duplicate archive copies, temporary extraction dumps, reverse-engineering databases, or cache/build noise. The repository asset-policy CI check enforces placement/hygiene rules; it is not a ban on authorized original resources.

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
