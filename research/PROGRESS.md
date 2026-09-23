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



## Complete player-skill ordering checkpoint

All 17 skill slots are now semantically mapped. The remaining six slots were recovered from EA's own Editor.exe Player Skills dialog and agree with the slots already proven from footballmanager.exe position-overall formulas.

Final slot order:

0 Speed; 1 Strength; 2 Stamina; 3 Determination; 4 Injury Proneness; 5 Passing; 6 Shooting; 7 Tackling; 8 Heading; 9 Control; 10 Technique; 11 Awareness; 12 Agility; 13 Goalkeeping; 14 Confidence; 15 Leadership; 16 Set Piece.


## Player aging/development formula checkpoint

The monthly player-development path has now been traced far enough to recover the core age curve used by FM2001.

Key routines:

- `0x41E970`: initializes per-player development baselines and randomized peak ages.
- `0x41EAD0`: recalculates all 17 current-skill bytes from age, stored baseline, target/potential bytes and club/training modifiers.
- `0x4173B0`: computes current player age from date of birth and the global game date.
- `0x4A8070`: main calendar/date tick.
- `0x40BB10` -> `0x4042E0`: iterates clubs and their players for the monthly development update.

Recovered tuning defaults:

- `AGEPhyical_lowest_peak` -> 25
- `AGEPhyical_highest_peak` -> 26
- `AGESkill_lowest_peak` -> 27
- `AGESkill_highest_peak` -> 29
- `AGEGoalie_lowest_peak` -> 30
- `AGEGoalie_highest_peak` -> 32
- `AGEPeakPeriod` -> 5

Each player stores a baseline age at runtime `+0x122`, copies the 17 baseline current-skill bytes to `+0x111..+0x121`, and stores three per-player peak ages at `+0x123/+0x124/+0x125`.

Normal forward-time skill evolution for one slot is now reconstructed. Let:

- `A0` = baseline age
- `A` = current age
- `B` = baseline skill byte
- `T` = target/development-target byte
- `P` = relevant personal peak age

Then, before the peak, current skill is linearly interpolated from baseline toward target:

`C = B + ((A-A0)/(P-A0)) * (T-B)`

If the player began before the peak and is now past it, the target is held through the peak period; after that, decline heads toward zero by age 60:

`C = T * (60-A)/(60-P)`

For a player whose baseline age was already beyond the relevant peak:

`C = B * (60-A)/(60-A0)`

The implementation contains additional backward-age branches for date/save edge cases.

Skill groups choose peak ages as follows:

- slots 0..4 use physical peak `+0x123`
- slots 5..8 use skill peak `+0x124`
- slots 9..16 use the third/goalkeeper peak `+0x125`

The second 17-byte array should therefore be described as a **development target / peak target**, not a strict ceiling: a small minority of original player records have target bytes lower than current bytes, representing expected regression toward the target.

Strong evidence from the calendar path indicates this recalculation runs on the first day of each month for every club/player.

Training-related tuning values identified near the same loader include:

- `TRNMax_boost` default 8192
- `TRNBuild_Boost` default 65
- `TRNInjuryReturnDefault` default 75
- `TRN_condition_divider` default 512.0
- `TRN_Condition_Warning_Threshold` default 75

The post-age section of `0x41EAD0` obtains a club-owned 40-record array of 200-byte records and reads two 17-byte regions from the selected record. Identifying this structure and its modifier semantics is the next active task.


## Training-system checkpoint

- Club training owns 40 x 200-byte per-player records; record +8 is player ID and player +0x70/+0x76 select a record 1-based.
- The embedded training state has 17 per-skill counters, 17 dword states, seven per-method counters, dates and timed effects.
- The exact seven 17-skill profile vectors are reconstructed: attacking, defensive, midfield, goalkeeper, rest, fitness and technique.
- Coach dispatcher 0x42C240 maps methods to goalkeeper, fitness, technique, defensive, midfield and attacking specialist employee roles.
- 0x4EACE0 is traced through its probabilistic success check and +8 raw-skill increment.
- Remaining anomaly: method ID 1 routes to the attacking coach, but generic profile selector 0x4EA9A0 returns NULL rather than vector0. This must be resolved before finalizing method IDs.

## Active Investigation

Current focus: resolve training method ID 1 / the attacking-vector special case, then recover the remaining club/staff/facility multipliers in the training success formula.

Immediate next steps:

1. Identify the 40 × 200-byte club-owned record structure at object +0x6B8 and its constructor at 0x424F90.
2. Map the two 17-byte modifier regions consumed by player development around 0x41ED2C.
3. Determine the semantic meaning of player runtime bytes +0x70/+0x76, which select records from that 40-entry array.
4. Connect the modifier structure to Training.cpp / training UI classes and TRN* tweak keys.
5. Update the clean-room player-development implementation once modifier semantics are proven.
6. Then move into contracts/transfers and season-state logic.

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
