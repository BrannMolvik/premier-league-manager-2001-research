# Premier League Manager 2001 Reverse-Engineering Progress

_Last updated: 23 September 2026_

## Purpose

This file is the canonical resume point for the project. Any ChatGPT, Codex, or local-agent session working on this repository should read this file before starting new investigation.

## Current Goal

Reverse engineer Premier League Manager 2001 as completely as practical, including:

- executable startup and subsystem layout
- database and string-table formats
- clubs, players, managers, squads, competitions, fixtures, transfers, finances, training and scouting
- save-game format
- season progression and AI
- match engine and match-day presentation
- clean-room reimplementation experiments that read the user's original game data without depending on the legacy executable

The fallback remains a persistent VM if a faithful native reimplementation becomes disproportionate.

## Current State

GitHub persistence is active. The connected GitHub account is `BrannMolvik` and has push/admin access to this repository.

The previous v0.3 clean-room parser/reimplementation work is present in the active analysis workspace and its verified findings have now been imported into this repository.

A Windows 11 modernization attempt successfully reconstructed the game installation without the obsolete 16-bit installer, but Windows Smart App Control / Code Integrity blocks the unsigned legacy `footballmanager.exe` before execution. Event ID 3077 in the Code Integrity Operational log explicitly identified the executable as blocked.

A clean-room reimplementation prototype has therefore been started alongside executable reverse engineering.

## Newly completed investigation block

Static.dat tables immediately preceding the competition table were verified:

- `0x2670`: Formation table, 21 records × 6 bytes. Names include 4-4-2 variants, 5-3-2 variants, 3-4-3 variants, 3-5-2 variants, 4-3-3 variants, 4-5-1, 2-5-3, 5-4-1, Long Ball, Sweeper and Xmas Tree.
- `0x26F2`: Player-status table, 12 records × 4 bytes. Names include Injured, Banned, International, Cup Tied, First Team, Substitute, On loan, Out of contract, Transfer listed, Bid in, Wanted and Non EU.

These discoveries are documented in `research/FILE_FORMATS.md`.

## Latest checkpoint

Additional Static.dat structures decoded:

- `0x0000`: 7 continents × 10 bytes.
- `0x004A`: 209 countries × 43 bytes.
- `0x2369`: 209 nationalities × 3 bytes.
- `0x4F1F`: 1,053 round records × 36 bytes; includes Premier League matchdays and FA Cup rounds with schedule/replay timing and team-entry counts.
- `0xE337`: 238 cup-allocation instructions × 28 bytes.
- `0xFD43`: 28-record league-allocation candidate × 28 bytes.
- `0x10057`: 380 real Premier League fixtures × 16 bytes with round/home/away club IDs.

The real-fixture table is a particularly strong milestone: the original 2000-01 Premier League schedule can now be reconstructed directly without running the EA executable.


## Latest executable-analysis checkpoint

MSVC RTTI has been resolved to actual vtables and methods for the manager rating/expectation/sacking classes. Their in-memory record strides are now known (12, 16, 12 and 12 bytes respectively), and their record parsing functions have been identified.

This analysis also prevented a premature identification: the 108-record block at `0x1181B` is still **unresolved**. Its 16-byte apparent grouping alone is not enough to call it `DBTManagerExpectedRankings`, because the values also strongly resemble competition/continental routing data and the binary parser can use packed serialization. Keep it as a candidate until field semantics and load order agree.


## Static.dat map completion checkpoint

The actual `Static.dat` loader at `0x4F7020` has now been traced. It resolves the previously ambiguous table identities by loading these RTTI-backed global objects in order:

`DBTCompetitions -> DBTRounds -> DBTCupAllocInstructions -> DBTLeagueAllocations -> DBTRealFixtures -> DBTInternationalFixtures -> DBTPrevInternationalScores -> DBTHosts`

The following manager/access tables are then loaded by the outer static-data loader:

`DBTManagerRatings -> DBTManagerExpectedRankings -> DBTManagerSackLeagues -> DBTManagerSackCups -> DBTAccessFanBase -> DBTAccessSkillFinancialValues`

Packed reader widths from the original binary establish exact table boundaries:

- `0x1181B`: InternationalFixtures, 108 × 16
- `0x11EDF`: PrevInternationalScores, 141 × 28
- `0x12E4F`: Hosts, 23 × 20
- `0x1301F`: ManagerRatings, 20 × 6
- `0x1309B`: ManagerExpectedRankings, 262 × 9
- `0x139D5`: ManagerSackLeagues, 24 × 7
- `0x13A81`: ManagerSackCups, 66 × 8
- `0x13C95`: AccessFanBase, 42 × 78
- `0x14965`: AccessSkillFinancialValues, 100 × 26

The final table ends exactly at `Static.dat` EOF `0x15391`.

This also corrects the earlier provisional label for `0x12E4F`: it is `DBTHosts`, not `DBTInternationalFixtures`.


## Player-structure checkpoint

The player database investigation has now separated two representations that must not be conflated:

- initial `Master.dat` player records: 103 bytes each
- runtime `DBRPlayer` objects: 592 bytes each (`0x250`)

The runtime/save reader contains two adjacent 17-byte arrays, while the compact master record contains an 18-byte characteristic/skill-related block. Exact conversion between these representations is now the active target.

The earlier clean-room prototype's linear 0–30 conversion is explicitly treated as provisional, not a recovered game formula.



## Compact player importer breakthrough

The actual `Master.dat` startup path and compact player importer are now located.

- player table startup loader: `0x4218C0`
- record loop: `0x421C80`
- per-player compact importer: `0x418B90`
- 35 file reads total exactly **103 bytes**

The importer proves the former 18-byte attribute interpretation was misaligned. The compact record contains a 3-byte position-related group followed by **two 17-byte arrays**, which map directly into two adjacent 17-byte regions of the 592-byte runtime player object.

This is now committed in `research/FILE_FORMATS.md` and `research/EXECUTABLE_ANALYSIS.md`.



## Player skill-model checkpoint

The paired 17-byte player arrays are now differentiated:

- runtime `+0x1E..+0x2E`: current skills
- runtime `+0x2F..+0x3F`: corresponding potential/ceiling targets

The game's exact raw-byte-to-rating conversion has been recovered as `floor((30*raw + 128)/255)`, producing the original 0..30 rating scale.

The position-overall function `0x41C7E0` plus named tweak keys has directly mapped current-skill slots:

- 0 Speed
- 1 Strength
- 5 Passing
- 6 Shooting
- 7 Tackling
- 8 Heading
- 11 Awareness
- 12 Agility
- 13 Goalkeeping
- 14 Confidence
- 15 Leadership

Unmapped slots remain 2, 3, 4, 9, 10 and 16.


## Active Investigation

Current focus: finish semantic mapping of the six remaining player skill slots (2, 3, 4, 9, 10, 16), then trace current-vs-potential development formulas and player characteristic consumers.

Immediate next steps:

1. Map remaining current-skill slots 2, 3, 4, 9, 10 and 16 using Editor/UI accessors and named tweak consumers.
2. Explain the small minority of Master.dat records where ceiling < current.
3. Recover development/aging/training formulas that move current skills toward ceilings.
4. Update the clean-room parser to the corrected 4-byte player header and verified skill model.
5. Then move into contracts/transfers and season-state logic.
6. Checkpoint before match-engine work.

## Persistence / Checkpoint Rule

Do not perform a long investigation without saving intermediate progress.

For future work in ChatGPT:

- Work in small reverse-engineering blocks.
- After each meaningful subsystem discovery, write the result to the appropriate file in `research/` and/or code in `tools/` or `reconstruction/`.
- Commit to GitHub before moving into another long investigation block.
- If a task may time out, checkpoint partial findings before the expensive step.
- Never rely on conversation state as the only copy of a discovered offset, record layout, algorithm, failed experiment or next-step hypothesis.

If a session is interrupted, the repository is the canonical state.

## Resume Rule

A new session should:

1. Read `research/CONTINUATION_INSTRUCTIONS.md`.
2. Read this file completely.
3. Read `research/FINDINGS.md`, `research/FILE_FORMATS.md`, `research/EXECUTABLE_ANALYSIS.md` and `research/FAILED_APPROACHES.md` as relevant.
4. Inspect recent commits.
5. Continue from the current Active Investigation section.

Do not repeat an earlier experiment solely because the conversation restarted.
