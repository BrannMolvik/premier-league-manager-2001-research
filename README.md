# premier-league-manager-2001-research

Reverse engineering and clean-room reconstruction research for **The F.A. Premier League Football Manager 2001**.

## Current status

The repository contains a large executable/data-format research corpus and a substantial data-free clean-room reconstruction. It is **not yet a complete playable replacement game**, but the reconstructed Premier League backend can parse the original data, maintain mutable player/league state, prepare autonomous AI teams, simulate normal-time matches through the recovered MatchCalculator logic, persist important post-match state, and advance dated Premier League fixtures.

The project is now managed through explicit sequential development gates so work can continue safely across multiple ChatGPT, Codex, and local-agent sessions.

## Start here

- `ROADMAP.md` - authoritative long-term gate plan and completion criteria.
- `research/CURRENT_STATE.md` - authoritative short live resume point and exact next task.
- `research/CONTINUATION_INSTRUCTIONS.md` - required cross-session workflow.
- `research/HANDOFF_PROMPT.md` - copyable prompt for a completely new session.
- `project_status.json` - machine-readable mirror of the current gate.
- `research/BACKLOG.md` - useful work intentionally deferred.
- `research/FIDELITY_GAPS.md` - known deviations, approximations, and fallbacks.

## Technical research

- `research/FINDINGS.md` - high-confidence reusable findings.
- `research/EXECUTABLE_ANALYSIS.md` - detailed offsets, RTTI, call paths, and disassembly notes.
- `research/MATCH_ENGINE.md` - MatchCalculator, scheduling, and match-state research.
- `research/FILE_FORMATS.md` - Master.dat, Static.dat, strings, and other file formats.
- `research/PLAYER_DEVELOPMENT.md` - recovered aging/development/training mechanics.
- `research/FAILED_APPROACHES.md` - disproven/superseded interpretations.
- `research/RUNTIME_COMPATIBILITY.md` - original executable compatibility work.
- `research/PROGRESS.md` - chronological history. It contains old milestone/status text and is **not** the live resume point.
- `reconstruction/` - tested clean-room implementation.

## Historical audits

Files named `research/*AUDIT*.md` are dated snapshots. They are useful for understanding how the project evolved but must not override `research/CURRENT_STATE.md` or later evidence.

## Clean-room boundary

The original copyrighted game executable, data files, disc images, and extracted asset dumps are **not** stored in this repository. The reconstruction reads files from a user's legally obtained copy where required. CI includes a guard intended to catch accidental commits of original game assets.
