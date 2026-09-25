# premier-league-manager-2001-research

Reverse engineering and clean-room reconstruction research for **The F.A. Premier League Football Manager 2001**.

## Current status

The repository now contains both a large executable/data-format research corpus and a substantial data-free clean-room reconstruction. It is **not yet a complete playable replacement game**, but the reconstructed Premier League backend can already parse the original data, maintain mutable player/league state, prepare autonomous AI teams, simulate normal-time matches through the recovered MatchCalculator logic, persist important post-match state, and advance dated Premier League fixtures.

Canonical project state:

- `research/PROGRESS.md` — current investigation and exact resume point
- `research/FINDINGS.md` — high-confidence reusable findings
- `research/EXECUTABLE_ANALYSIS.md` — detailed offsets, RTTI, call paths and disassembly notes
- `research/MATCH_ENGINE.md` — detailed MatchCalculator, scheduling and match-state research
- `research/FILE_FORMATS.md` — Master.dat, Static.dat, strings and other file formats
- `research/PLAYER_DEVELOPMENT.md` — recovered aging/development/training mechanics
- `research/FAILED_APPROACHES.md` — disproven/superseded interpretations
- `research/RUNTIME_COMPATIBILITY.md` — original executable compatibility work
- `research/PROJECT_AUDIT_2026-09-25.md` — latest full-project audit
- `reconstruction/` — tested clean-room implementation

The original copyrighted game data/executable are not stored in this repository.
