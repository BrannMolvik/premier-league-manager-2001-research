# premier-league-manager-2001-research

Reverse engineering and Windows 11 modernization/porting work for **The F.A. Premier League Football Manager 2001**.

## Project goal

The target is not a generic football-management remake. The target is to make FM2001 playable and maintainable on modern Windows while preserving **as much of the original game as possible**.

The project owner has confirmed that the supplied FM2001 archive/disc contents are authorized for use in this project. Original data, music, sound, interface graphics, strings, and other resources should therefore be reused when practical. Modern replacement code is used where the legacy executable/runtime is incompatible with Windows 11 or where a modern implementation is required.

The result should ultimately feel like FM2001 itself: original presentation and content on top of a modern, stable runtime.

## Current status

The repository contains a large executable/data-format research corpus and a substantial modern reconstruction of the gameplay backend. It is **not yet a complete playable Windows 11 port**, but the Premier League backend can already parse the original data, maintain mutable player/league state, prepare autonomous AI teams, simulate normal-time matches through recovered MatchCalculator behavior, persist important post-match state, and advance dated Premier League fixtures.

The project is managed through explicit sequential development gates so work can continue safely across multiple ChatGPT, Codex, and local-agent sessions.

## Start here

- `ROADMAP.md` - authoritative long-term gate plan and completion criteria.
- `research/CURRENT_STATE.md` - authoritative short live resume point and exact next task.
- `research/CONTINUATION_INSTRUCTIONS.md` - required cross-session workflow.
- `research/HANDOFF_PROMPT.md` - copyable prompt for a completely new session.
- `project_status.json` - machine-readable mirror of the current gate.
- `research/ASSET_POLICY.md` - authorized original-resource reuse policy.
- `research/BACKLOG.md` - useful work intentionally deferred.
- `research/FIDELITY_GAPS.md` - known deviations, approximations, and fallbacks.

## Repository areas

- `reconstruction/` - modern replacement/runtime code. The name is historical; the project itself is now a modernization/port.
- `original_assets/` - authorized original resources intentionally imported for reuse.
- `research/` - reverse-engineering evidence and project state.
- `tools/` - analysis, extraction, conversion, and validation utilities.

## Technical research

- `research/FINDINGS.md` - high-confidence reusable findings.
- `research/EXECUTABLE_ANALYSIS.md` - detailed offsets, RTTI, call paths, and disassembly notes.
- `research/MATCH_ENGINE.md` - MatchCalculator, scheduling, and match-state research.
- `research/FILE_FORMATS.md` - Master.dat, Static.dat, strings, and other file formats.
- `research/PLAYER_DEVELOPMENT.md` - recovered aging/development/training mechanics.
- `research/FAILED_APPROACHES.md` - disproven/superseded interpretations.
- `research/RUNTIME_COMPATIBILITY.md` - original executable compatibility work.
- `research/PROGRESS.md` - chronological history. It contains old milestone/status text and is **not** the live resume point.

## Historical audits

Files named `research/*AUDIT*.md` are dated snapshots. They are useful for understanding how the project evolved but must not override `research/CURRENT_STATE.md` or later evidence.

## Asset/repository boundary

Authorized original resources may be intentionally imported under `original_assets/` and should be tracked with provenance. Raw disc images, duplicate archives, temporary extraction dumps, reverse-engineering databases, and build/cache noise should remain outside Git.

See `research/ASSET_POLICY.md`.
