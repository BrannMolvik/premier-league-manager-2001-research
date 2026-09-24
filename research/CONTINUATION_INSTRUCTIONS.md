# Continuation Instructions

## Read this first

This repository is intended to preserve reverse-engineering progress across ChatGPT, Codex, and local-agent sessions.

A conversation timeout is not a reason to restart the investigation.

## Required startup procedure

Before doing new work:

1. Read `research/PROGRESS.md` completely.
2. Read `research/FINDINGS.md`.
3. Read `research/FAILED_APPROACHES.md`.
4. Read the topic-specific research files relevant to the current task.
5. Inspect recent repository commits when useful.
6. Continue from the latest documented active investigation and next step.

## Persistence requirement

Do not keep important discoveries only in conversational reasoning.

During long investigations, write intermediate results into the repository frequently. In particular, checkpoint before:
- long binary/decompiler analysis;
- dependency or compatibility experiments;
- batch extraction;
- format reverse engineering;
- large automated searches;
- rebuilding or patching attempts;
- any operation likely to consume a substantial part of a session.

## What belongs where

- `PROGRESS.md`: current state, active task, immediate next steps.
- `FINDINGS.md`: verified reusable discoveries.
- `FAILED_APPROACHES.md`: unsuccessful or inconclusive attempts.
- `EXECUTABLE_ANALYSIS.md`: PE structure, code paths, APIs, addresses, disassembly/decompiler notes.
- `FILE_FORMATS.md`: game data, database, save, resource, archive, and configuration formats.
- `RUNTIME_COMPATIBILITY.md`: launch behavior, Windows compatibility, graphics/audio/runtime dependencies, wrappers, patches.
- `tools/`: scripts and utilities made during analysis.
- `extracted/`: derived metadata or small legal-to-store extracted artifacts, not an uncontrolled dump of copyrighted game assets.
- `reconstruction/`: code for any clean-room replacement or reconstructed components.

## Evidence discipline

Clearly separate:
- Confirmed: directly verified.
- Probable: strong evidence but not fully proven.
- Hypothesis: plausible explanation awaiting a test.

Record enough detail that another session can reproduce important conclusions.

## Continuous checkpoint cadence

For this project, "checkpoint frequently" means:

- commit immediately after each verified subproblem or corrected interpretation;
- commit before switching to a different subsystem;
- during a long unresolved trace, commit partial evidence/next address at least once per substantial analysis block rather than waiting for a final conclusion;
- never allow several user-visible progress updates to occur without a corresponding GitHub checkpoint;
- when a finding is promising but not verified, record it explicitly as a hypothesis/active lead rather than leaving it only in chat.

The repository must remain close enough to the live investigation that a timeout loses at most one small analysis block.


## Timeout protocol

If the current task cannot be completed before a session ends:

1. Stop at a safe intermediate point.
2. Save all useful scripts/output that can be persisted.
3. Update the relevant research notes.
4. Update `PROGRESS.md` with exactly where work stopped.
5. Write the next concrete command/test/analysis step.
6. Commit the checkpoint.

The next session should continue from that checkpoint rather than repeating the full analysis.
