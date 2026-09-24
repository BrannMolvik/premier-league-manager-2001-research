# Premier League Manager 2001 Reverse-Engineering Progress

_Last updated: 24 September 2026_

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

Both the compact Master.dat player record and the runtime DBRPlayer contain two adjacent 17-byte skill arrays. They are now identified as current skills and corresponding peak/development targets. The complete 17-skill ordering and exact raw-to-0..30 conversion have been recovered.



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
- The former method-ID-1 anomaly is resolved: its jump target returns vector0 (attacking) without executing the invalid-ID `xor eax,eax` path. Final method map: 0 rest/recovery, 1 attacking, 2 midfield, 3 defensive, 4 goalkeeper, 5 fitness, 6 technique.

## Interrupted-session partial lead

The session timed out while tracing the exact probability math inside adult training. Before interruption, static analysis indicated a provisional form:

- nonzero profile weight is multiplied by a club/staff quality multiplier and by approximately 0.5;
- the result is compared against a random integer in the 0..99 range;
- observed quality constants were 1.25, 1.30, 1.35, 1.40 and 1.45;
- one facility-related branch appeared to add +0.25.

This is intentionally recorded as an **unverified lead**, not a confirmed formula. Re-enter the relevant code path and verify the source of each multiplier/facility flag before promoting it to `EXECUTABLE_ANALYSIS.md`.

## Training probability complete checkpoint

The active-training success probability is now recovered semantically:

`success if random(0..99) < profileWeight * Q * 0.5`

where:

- Q starts at 1.00;
- Youth Team Coach (employee type 3) rating 1..5 gives Q = 1.25/1.30/1.35/1.40/1.45;
- if no Youth Team Coach exists, an Assistant Manager (employee type 1) gives fallback Q = 1.25;
- a Training Centre (club feature ID 5) adds +0.25 to Q.

The identities are proven from EA's own formatter classes and the CTrainingBuilding constructor.

## Contract/transfer checkpoint

Contract analysis has started and already confirms player weekly wage at +0xC4, contract expiry at +0x154, the 0x50-byte contract terms object, and the core application routine at 0x418FB0. CDealInProgress and CPlayerBidLog structures are located. Several contract-clause bits and player-status bits are structurally mapped but remain deliberately unnamed until tied to EA's named UI actions.

## Complete contract-term map checkpoint

The negotiated player-contract object is now fully mapped at the user-visible level:

- +0x18 wage
- +0x1C signing-on fee
- +0x20 promotion bonus
- +0x24 contract length
- +0x28 appearance fee
- +0x2C relegation transfer-request clause
- +0x2D big-club offer clause
- +0x2E big-money offer clause
- +0x2F house
- +0x30 car

## Transfer-history movement checkpoint

`CPlayerMovement` is now mapped as a 0x18-byte transfer-history record:

- player ID
- source club ID
- destination club ID
- fee/consideration
- movement date

The fee field uses special values 1 = "on a free transfer" and 2 = "Bosman", recovered directly from `English.idx` -> `English.str`. All other values are currency-formatted fees.

## Transfer proposal checkpoint

The live transfer model is now separated into three layers:

- 0x50-byte proposal: target player, up to three exchange players, cash fee, contract terms, buying club and negotiation-history fields.
- 0x68-byte CDealInProgress: lightweight per-player/per-club negotiation state.
- 0x18-byte CPlayerMovement: completed transfer-history record.

Cash fee at proposal +0x10 and buying club +0x34 are confirmed. CPlayerBidLog is mapped as player + bidding club + 8-byte bid amount + bid date, with one remaining status/counter field.

CDeal states 3/4/5 are definitively swap/player-exchange variants of 0/1/2. Exact names of base states 0/1/2 remain the active target.

## Transfer state-machine checkpoint

New verified transfer findings:

- proposal +0x38 = previous/anchor wage offer;
- proposal +0x3C = previous/anchor signing-on fee;
- proposal +0x48 = stored anchor/previous total proposal valuation (exact UI label not yet known);
- vtable 0x7C8F50 is EA's own `EAMTPUserEndNegotiationssub`;
- vtable 0x7D7D94 is `MPMTryExecuteTransfer`;
- deal states 2/5 and 1/4 are explicitly distinguished by `MPMTryExecuteTransfer`, while 0/3 remains another/pending condition;
- medical pass/fail and transfer-conclusion event classes have concrete RTTI/vtable addresses for the next trace.

The exact human-readable enum names for CDealInProgress states 0/1/2 remain unresolved. Do not preserve earlier guesses such as "closed" or "accepted" as facts.


## Deal-state semantic checkpoint

CDealInProgress state 2 is now definitively the player-rejected/declined-contract outcome; state 5 is the swap/player-exchange variant. EA's own reason-code-3 event classes are FreePlayerDeclinesContract, PlayerDeclinesContractRenewal, and TPUserPlayerRejects.

Current safe model:

- 0/3 pending or unresolved
- 1/4 cleared/non-pending for execution
- 2/5 player rejected contract
- +3 marks the same state family in a swap/player-exchange deal

Also corrected: proposal helper 0x4F0460 simply tests whether any exchange-player slot is populated.


## Transfer execution checkpoint

The actual player-movement path is now traced:

- MPMTryExecuteTransfer stores buyer/seller clubs and gates execution on per-player deal states.
- states 2/5 are the player-rejected/declined-contract family; states 1/4 satisfy the ready-to-progress predicate. The +3 offset marks swap/player-exchange variants.
- MPMTransferPlayer ultimately calls player routine 0x4229B0.
- 0x4229B0 logs CPlayerMovement history, stages negotiated contract terms, and invokes the club-switch path.
- 0x422F70 writes the new club IDs, stamps the current-club join date, and resets temporary transfer/status state.
- swap players use the same movement machinery in the reverse club direction.

## Transfer finance checkpoint

Completed-transfer money flow is now proven:

- seller posting path `0x404BB0 -> 0x5DC510` credits the current finance money value;
- buyer posting path `0x404B30 -> 0x5DC650` debits the same value;
- affordability check `0x404AE0` compares the proposed amount against that current money value before a user-controlled buyer can proceed;
- Balance.cpp source metadata and BALANCE/CASH strings identify this as current cash/balance state;
- transfer budget is a separate subsystem and must not be conflated with this money field;
- both transfer postings use accounting category code 1000, whose exact display label remains to be mapped.

## Budget-structure checkpoint

EA's `EAMchairbudgetsettings` message now proves eight distinct chairman budget buckets: total, staff, player wages, maintenance, merchandising, miscellaneous, buildings limit and transfers. Transfer budget is therefore structurally separate from the already-recovered current cash/balance field. The message layout is mapped, while the authoritative live budget storage remains an active target.

## 24 September resume checkpoint

The previous session continued beyond the last GitHub commit and located a new named budget-related message class, `EAMbcstartseasonmail`, which represents the board/chairman start-of-season budget announcement.

This work had remained only in the conversation and was therefore not safely persisted. It is now checkpointed in `research/EXECUTABLE_ANALYSIS.md`.

Current exact resume target:

- trace construction/population of `EAMbcstartseasonmail`;
- identify the authoritative runtime source for its transfer/staff/wage/maintenance/merchandising/misc/building budget fields;
- determine how transfer completion changes the assigned transfer budget independently of the already-mapped cash balance.


## Start-season mail field checkpoint

`EAMbcstartseasonmail` is now mapped exactly at the message level. It carries seven dword budget values at +0x3C..+0x54 in this order: staff, player wages, maintenance, merchandising, miscellaneous, buildings limit, transfers. It does not contain the TOTALBUDGET field present in `EAMchairbudgetsettings`.

A matching seven-dword block exists at runtime club +0x3C..+0x54, but that relationship remains a hypothesis until the club fields are independently identified.


## Club-budget shortcut rejected

The suspected runtime club `+0x3C..+0x54` budget block has been disproven from EA's original 181-byte club importer. Club +0x3C is the expanded sponsor-string reference (Arsenal resolves to `Sponsor`), +0x40 is manager ID 204 (Arsène Wenger for Arsenal), and the following bytes are club record data. Do not revisit this block as live budget storage.

The budget trace therefore returns to the event creation/population path for `EAMbcstartseasonmail`.


## Monthly budget message checkpoint

`bcmonthlybudget` (event ID 0xA1) is now mapped: +0x3C total, +0x40 staff, +0x44 player wages, +0x48 maintenance, +0x4C misc, +0x50 buildings, +0x54 transfers. This differs from the season-start message and gives a recurring event to trace back to live budget state.


## Budget-config checkpoint

The board/business budget defaults are now mapped to their exact globals, including `TransferBudget = 0x821DC0` and `TransferBudget2K = 0x821DA8`, with matching staff/player-wage/facilities/stadium/misc globals.

Also verified: the generic event allocator's A3/A4 tags are not EAM IDs. `bcstartseasonmail` still identifies itself as event A0, and `bcmonthlybudget` as A1.


## Finance cheat trace checkpoint — SUPERSEDED

This checkpoint is historical and was superseded by the RTTI correction below. Do not use these getter labels.


Before continuing the live transfer-budget search, the current cheat-code evidence is now preserved:

- `0x516090` is called specifically on the insufficient-current-cash transfer branch and is the leading `/cash777` candidate;
- `0x516020` is a separate finance/business cheat getter and is the leading `/budget777` candidate;
- exact labels remain provisional until getter globals are tied back to the literal command-line strings.


## Cash/budget cheat mapping checkpoint — SUPERSEDED

This checkpoint is historical and was superseded by the RTTI correction below. Do not use these getter labels.


The finance cheat split is now resolved:

- `0x516090` is the `/cash777` affordability-bypass getter used after current-cash comparisons;
- `0x516020` is finance-adjacent but **not yet proven** to be `/budget777`; RTTI shows its current known caller is a season-ticket setting routine.

This gives a new direct route into the live budget logic while preserving the distinction between cash and assigned budgets.

## Correction checkpoint: 0x516020 not yet proven as budget777

RTTI resolved the routine ending at 0x5DE6C3 as season-ticket setting (`EAMChairSeasonTicketSetsub` / `EAMSeasonTicketSetsub`). The previous label of 0x516020 as definitively `/budget777` was premature and has been reverted. The `/cash777` association for 0x516090 remains strongly supported by four independent current-cash affordability checks.
## Critical cheat-trace correction

RTTI proves global `0x877540` is a `std::basic_istringstream`, with standard-library `basic_istream`/`basic_stringbuf` vtables. Therefore the byte getters at `0x515FF0..0x5160E0` are stream/internal-state accessors, **not cheat flags**.

All earlier attempted `/cash777` or `/budget777` labels for `0x516090` / `0x516020` are superseded. The actual cheat parser must be recovered independently from the literal cheat-string pointer table.


## Cheat-command table recovery checkpoint

Fresh analysis against the exact hashed executable has recovered the contiguous literal developer-switch pointer table at `0x828510..0x828568`. It contains, in order, `/nofmvplease777`, `/fastbuild777`, `/budget777`, `/sacked777`, `/cash777`, `/autorun777`, `/alwayswin777`, `/alwayslose777`, `/countrywin777`, `/countrylose777`, `/skipmatchcalc777`, `/nolimit777`, `/nosackwarnings777`, `/alttab777`, `/showskill777`, `/showstat777`, `/stadiumflags`, `/pitchlitter`, `/pitchwear`, `/noslidefx`, `/cameraflashes`, `/setslide`, and `/alwayssell`.

No direct absolute code xrefs to individual table slots were found, which supports a data-driven iterator/indirection model.

The earlier RTTI correction remains valid for the `0x877540` `basic_istringstream` object, but a refinement is now proven: tiny routines `0x515FE0`, `0x516010`, and `0x5160B0` read separate bytes at `0x82856C`, `0x82856E`, and `0x82856F` respectively. Those bytes sit immediately after the command-pointer table and are initialized to 1. They are not part of the stream object, but their meanings are still unresolved.


## 0x877540 container correction checkpoint

Constructor-level analysis has overturned the prior RTTI-based interpretation of `0x877540`.

**Confirmed:** `0x515F10 -> 0x5162A0` constructs a 16-byte ordered-tree container at `0x877540..0x87754F`, including an allocated 0x24-byte sentinel/header node and tree bookkeeping. The streambuf/stringbuf RTTI belongs to a separate implementation family beginning around `0x5166A0`.

Therefore the global bytes at `0x877550..`, exposed by getters `0x515FF0..0x5160E0`, are not inside the tree object and are no longer disqualified as command/cheat state. Their exact literal mappings remain to be proven.

This supersedes the repository's earlier statement that `0x877550..` were `basic_istringstream` internal bytes.


## TransferBudget global-reference checkpoint

Whole-image scanning confirms that `0x821D80..0x821DFF`, including `TransferBudget2K` at `0x821DA8` and `TransferBudget` at `0x821DC0`, has no absolute reference anywhere except the config-loader writes themselves. No direct read or pointer-table entry to that range exists in the executable.

Current implication: do not treat these tuning globals as live budget storage. Continue through the board-budget event/state production path to locate the authoritative per-club/user values.


## Confirmed command-state mapping: /nofmvplease777

Getter `0x515FF0` -> byte `0x877550` is confirmed as `/nofmvplease777`: startup uses it to skip playback of `easp.tgq`, and the same getter gates related FMV/video paths.

This validates the corrected interpretation that `0x877550+` contains real developer-command state.


## Match developer-command checkpoint

Confirmed command-state mappings:

- `0x877554` / getter `0x516040` -> `/alwayswin777`
- `0x877555` / getter `0x516050` -> `/alwayslose777`
- `0x877556` / getter `0x516060` -> `/countrywin777`
- `0x877557` / getter `0x516070` -> `/countrylose777`
- `0x877558` / getter `0x516080` -> `/skipmatchcalc777`

The mappings are established from direct match-result override behavior in `0x512D80` and the calculation bypass at `0x5130DC`.


## Confirmed /cash777 mapping

Getter `0x516090` -> state byte `0x877559` is the cash-affordability bypass corresponding to `/cash777`. All four consumers compare a required monetary amount to the club's current finance balance and use this flag to bypass the insufficient-funds path.

This conclusion is now restored on corrected object-layout evidence, not the superseded stream interpretation.


## 0x877552 budget-candidate checkpoint

Getter `0x516020` -> byte `0x877552` is called only at the return of seasonal finance routine `0x5DE530`. Both direct callers of `0x5DE530` ignore its return value, so this byte currently has no proven behavioral effect in the discovered call graph.

Do not label it `/budget777` yet. The live transfer-budget guard must be found independently.


## Accounting category 1000 checkpoint

Completed transfers are now confirmed to feed category `1000` into the club finance ledger on both buyer and seller sides.

The finance layer separately aggregates category-1000 credits and debits and computes a net value (`0x5DC890`, `0x5DD650`, helper `0x43F1E0`). Finance overview code explicitly queries category 1000 through these paths.

No separate transfer-budget scalar write is visible in the immediate transfer-completion/posting path.

**Hypothesis, not yet confirmed:** remaining transfer budget may be computed from a board transfer allocation adjusted by category-1000 transfer ledger flow rather than stored as a separately decremented scalar.

Exact next target: locate the board transfer-allocation source and the comparison/derivation that combines it with category-1000 spending or triggers `OVERSPENTBUDGET`.


## Corrected startup-handoff checkpoint

The previous checkpoint misidentified the value passed through `0x531AF0 -> 0x531C10 -> 0x530380` as `lpCmdLine`. Correct stack accounting proves it is WinMain's **hInstance**. Global `0x87784C` is later used as the `hMod` argument to `SetWindowsHookExA`, independently confirming the correction.

This route is not the cheat parser. Resume the cheat search from the literal pointer table and true command-line/argv consumers.



## Cheat-state behavior checkpoint

The reopened global option bytes now have verified consumer semantics:

- `0x877554..0x877557` are the four match-result override states used together in `0x512D80`; their probable literal identities are `/alwayswin777`, `/alwayslose777`, `/countrywin777`, and `/countrylose777`.
- `0x877558` bypasses later match calculation and is probably `/skipmatchcalc777`.
- `0x877559` is definitively a current-cash affordability bypass from four independent consumers and is very probably `/cash777`.
- `0x877552` is read by `0x516020` at the end of the season-ticket finance routine `0x5DE530`; its probable `/budget777` association remains unproven because current callers do not visibly consume the returned value.

This proves the runtime byte ordering is not a naive same-index copy of the literal command-pointer table. The decoder is still unresolved.

The finance investigation now returns to direct xrefs of `TransferBudget` / `TransferBudget2K` and the completed-transfer path rather than treating the probable budget cheat byte as authoritative storage.


## TransferBudget configuration-only checkpoint

A complete executable-wide absolute-reference and raw-pointer scan shows that `TransferBudget` (`0x821DC0`), `TransferBudget2K` (`0x821DA8`), and the neighboring mapped wage/facilities/stadium/misc budget globals are referenced only by their tuning-loader writes. No later direct read or data-pointer reference exists.

This rules them out as the authoritative live per-club/user budget storage. The current trace must continue through board/business runtime objects, budget messages, and expenditure checks.



## Chairman extra-transfer event checkpoint

RTTI now identifies event IDs 0x4F/0x50/0x51 as `EAMchairextratransferfail`, `EAMchairextratransfersuccess`, and `EAMchairextraforallbudgets`. Their vtables and generic-factory construction branches are mapped. `EAMchairbudgetwarning` is also located.

These are strong runtime-budget leads, but remain message containers rather than proven live storage. The next trace is their producers/handlers and the finance overview/business-controller state they expose.



## Season-ticket state rejection checkpoint

The heavily used game/session pointer at `+0x694` has been ruled out as live transfer-budget storage. It points to a 0x7C-byte object whose +0x04/+0x08/+0x0C fields and +0x14..+0x78 selection array are consumed by the season-ticket/business calculation and `EAMSeasonTicketSet` paths.

Resume live-budget tracing from actual budget/expenditure checks and chairman budget-event producers, not game/session +0x694.



## Expenditure-refusal and category-1000 checkpoint

`EAMChairmanRefusesExpenditureM` is now mapped through RTTI/constructor/serializer. In the transfer insufficient-cash path it carries club/index/manager-like identifiers, not a failed amount or budget scalar, so it is notification-only and not the live transfer-budget store.

Category 1000 is explicitly aggregated and rendered as a dedicated net row in Finance Overview. The transfer ledger therefore has a visible finance-UI representation, strengthening the hypothesis that remaining transfer budget may be derived from board allocation plus category-1000 flow. The exact localized label of category 1000 is still unresolved.

Immediate event-ID references for budget warning / extra-transfer events and `bcmonthlybudget` were inspected and are UI/event registration, not producers.

Exact next target: identify the localized Finance Overview label for category 1000 and/or trace `EAMchairbudgetsettings` / chairman extra-transfer handlers back to the authoritative board allocation source.


## Monthly-income transfer-fees checkpoint

`EAMbcmonthlyincome` is now identified as event ID `0x9F`. EA's formatter labels its seven dword business-income fields as `GATE, MERCH, CONC, ADVERTS, SPONSOR, TELLY, TRANSFERFEES`, with `TRANSFERFEES` at event `+0x54`.

This is an exact EA-authored transfer-finance label. The link from accounting category 1000 to this event field is plausible but remains unconfirmed until the monthly-income producer is traced.


## Chairman budget-adjustment formatter checkpoint

The `TRANSFERBUDGETINCREASE` key is now traced to EA's `chairextracashsuccess@ModFmt` formatter at `0x60E3A0`, paired with `chairextracashfail` and `chairextraallbudgets`.

The success formatter reads a message/reason variant selector at `+0x10` and a transfer-budget increase amount at `+0x14`. `ENGLIS2.STR` proves all seven branches are transfer-budget-success wording variants, not seven budget categories.

Exact next target: trace who populates the formatter/event selector and amount, then follow that source into the authoritative live board budget state.


## Extra-transfer success event field checkpoint

`EAMchairextratransfersuccess` is now directly connected to the seven-way `chairextracashsuccess@ModFmt` budget-adjustment formatter.

Confirmed event fields:

- `+0x3C` = budget increase amount
- `+0x40` = transfer-budget success message/reason variant selector
- `+0x44` = club/team ID

The event copies +0x40 to ModFmt +0x10 and +0x3C to ModFmt +0x14, exactly matching the selector/amount fields used by `TRANSFERBUDGETINCREASE`.

If +0x40 is -1, the formatter chooses a random message/reason variant 1..6; the formatter also supports a seventh wording branch. The previous selector-7-as-transfer-budget hypothesis is superseded.

Exact resume target: find producers/writers of this event's +0x3C/+0x40/+0x44 fields to recover the selector map and the actual live budget update.


## Selector dispatch and current-club checkpoint

The chairman extra-cash success selector is now structurally mapped end-to-end:

1 -> 0x60E3BA / global 0x87A870
2 -> 0x60E3EB / global 0x87A86C
3 -> 0x60E41C / global 0x87A868
4 -> 0x60E45B / global 0x87A864
5 -> 0x60E48C / global 0x87A860
6 -> 0x60E4CD / global 0x87A85C
7 -> 0x60E50A / global 0x87A858

All seven branches format the same transfer-budget increase amount with `TRANSFERBUDGETINCREASE`; only the localized success/reason wording changes. These selector values are not budget-category IDs.

The heavily referenced game/session pointer at `+0x5B4` has also been ruled out as a budget-controller object: initialization `0x4258D0..0x4258F2` stores an incoming current club/team pointer directly into that field. Resume from the event producer / club finance state, not game +0x5B4 as a separate store.


## DBRClub / budget-cheat correction checkpoint

The current-club runtime record is now tied to RTTI as `DBRClub`, size **0x2A8 bytes**, with `DBTClubs` at global `0x874B9C`. This gives a concrete runtime club object for finance-field tracing.

The apparent budget-option path was also rechecked: although `0x5DE530` returns the value from `0x516020 -> 0x877552`, both callers (`0x4A870D`, `0x4C4826`) ignore that return. Keep `0x877552` unresolved; do not treat it as proven `/budget777` behavior or as a route to live transfer-budget storage.

Exact next target: inspect DBRClub finance-related fields and finance-controller structures for the seven chairman budget buckets, using the confirmed 0x2A8 record boundary and known current-club pointer.


## Finance object +0x670 checkpoint

The main finance object at game/session `+0x670` is now structurally mapped:

- allocation size: **0xE0 bytes**
- constructor: `0x5DC400`
- cash/current balance: **qword at object +0x10**
- `0x5DC510` credits that qword
- `0x5DC650` checks and debits that qword
- the remaining object contains multiple accounting/range subrecords and bookkeeping state.

No obvious contiguous seven-dword chairman-budget array is initialized in this object. Treat it as the authoritative cash/accounting object, not automatically as the chairman budget store.

Exact next target remains the board/chairman allocation source and budget-warning/extra-budget producer path; use the finance object only where evidence shows a field/aggregate is consumed.


## Balance slots / financial-objective checkpoint

Game/session `+0x670..+0x684` are now confirmed as **six separate Balance-object pointers**. Save code loops over all six, serializing each Balance and its internal state beginning at +0x30.

The promising `ChairmanPercentBudgetMiss` runtime consumer at `0x5E1D90` has also been resolved. It compares current cash (Balance +0x10) with a stored target at Balance +0x50, then tests `target * ChairmanPercentBudgetMiss * 0.01`. The resulting events are RTTI-identified as `EAMManagerObjectiveContinuedSuccess` and `EAMManagerFailedObjective`.

So Balance +0x50 is part of the manager/chairman financial-objective system, **not** the authoritative transfer-budget allocation. Do not follow this target as the seven-bucket budget store.

Resume from chairman budget-setting/extra-budget state and budget-warning producers rather than the financial-objective tolerance path.


## Extra-transfer selector correction checkpoint

English localization resolves the seven-way `EAMchairextratransfersuccess` formatter dispatch.

Confirmed corrected semantics:

- +0x3C = transfer-budget increase amount
- +0x40 = transfer-budget success message/reason variant selector
- +0x44 = club/team ID

All seven formatter branches describe an increase to the **transfer budget**; they are different wording/circumstance variants. The previous idea that selector 1..7 represented the seven chairman budget buckets, or that selector 7 specifically meant transfer budget, is superseded.

The chairman budget-settings localization also explicitly distinguishes the transfer budget from quarterly spending limits and says the manager is free to buy and sell players. This fits the code-level observation that transfer completion checks current cash while transfer budget is a separate board allocation/reference value.

Exact next target: identify the manager-to-chairman extra-funds request event/action in the English resource and trace its gameplay producer/handler to where the transfer-budget value is read and increased.


## FundRequest event checkpoint

The manager-initiated “request extra funds” feature is now identified as `EAMFundRequest` event ID **0x185**, with `EAMFundRequestReject` at **0x186**. The request event serializes three dwords at +0x38/+0x3C/+0x40.

`ENGLIS2.STR` index 1465 contains the outgoing request for further monies for squad strengthening. Nearby response text proves the chairman can reject the request (index 1468) or grant a repayable loan amount with a month term (index 1470).

This is a stronger live-finance lead than the automatic extra-transfer-success mail because it begins from an explicit manager action and must pass through a decision path that calculates/changes funding.

Exact next target: trace the 0x185 handler into the accept/reject events and identify the approved amount, repayment state, and whether the mutation hits current cash, transfer budget, or both.


## FundRequestAccept cash-credit checkpoint

The manager-initiated extra-funds path is now substantially resolved.

`EAMFundRequestAccept` is event ID **0x187**. Its formatter proves:

- +0x3C = approved **AMOUNT**
- +0x40 = repayment **MONTHS**

The accept path uses tuning globals:

- `FUNDMaxReqPerYear` -> 0x8222B4
- `FUNDMaxTimeToRepay` -> 0x8222B8

Handler `0x472570` updates a request-state object at runtime +0x688:

- +0x04 = approved amount
- +0x08 = request count, incremented
- +0x0C = repayment-term value

It then credits the approved amount to the active Balance through **0x5DC510**, proving that accepted FundRequest money increases **current cash**, not the separate transfer-budget scalar.

This separates the user-requested repayable funding system from the automatic chairman `chairextratransfersuccess` system, whose text explicitly increases transfer budget.

Exact next target: trace the automatic transfer-budget-increase producer/mutation and compare it with the now-resolved cash-loan path.


## Transfer-budget reserve-model checkpoint

Vtable comparison now proves `EAMchairextratransfersuccess` does not itself apply the budget mutation. In the same side-effect slot where `EAMFundRequestAccept` has handler `0x472570`, the automatic extra-transfer success/fail/all-budgets events all use generic handler `0x4093E0`. Their class-specific `0x55D920` path is UI/navigation only.

Therefore the automatic transfer-budget increase is applied in its producer/board-finance logic **before** the notification event is emitted.

Original localization also sharpens the finance model:

- the five quarterly operating budgets are fixed spending limits;
- buildings have an annual limit;
- the transfer budget is separately stated while the manager is “free to buy and sell players as you wish”;
- after quarterly overspending, chairman wording explicitly says money can be taken from the **building and transfer budgets** to compensate.

This strongly explains why completed-transfer affordability checks current cash while transfer budget has resisted discovery as a separate hard-cap check: it is a mutable board reserve/reference allocation, not the immediate purchase gate.

Exact next target: trace the quarterly budget-recalculation/overspending producer that takes money from building and transfer reserves. That path must read/write the authoritative live transfer-budget state and may be easier to locate than the automatic increase producer.


## Chairman budget-settings producer checkpoint

`EAMchairbudgetsettings` is confirmed as event ID **0x4E**. Its serializer contains the eight known budget values through +0x58 plus additional fields +0x5C/+0x60/+0x64; the UI action handler proves +0x5C is the club/team ID.

All currently found hard-coded 0x4E references are UI/event registration/setup, not the gameplay producer. The same is true for the inspected hard-coded 0x4A budget-warning references. The live producer must therefore be located through dynamic event creation/dispatch or through the board-finance calculation that fills the event.

A candidate DBRClub block at +0x21C..+0x234 was checked and is not supported as a budget array; its fields are used in unrelated club/runtime logic.

Exact next target: trace the quarterly overspending/rebudget calculation or dynamic construction of EAMchairbudgetsettings, both of which must read the authoritative live transfer/building budget values.


## Stadium/Groundsman cash-affordability checkpoint

The real gameplay producers for `EAMsmnobudget` (0x9C) and `EAMgdnobudget` (0x9D) are mapped around 0x5D2130..0x5D2A8F. They compare the requested stadium/facility cost against active Balance cash (+0x10) and debit through 0x5DC650 when affordable; otherwise they emit the corresponding no-budget message.

Therefore these "no budget" events are another current-cash gate, not evidence for the separate chairman transfer-budget reserve.

Next target returns to persistent/save-state budget structures and the quarterly reserve-rebalancing path.


## Balance objective-block resolution checkpoint

The full six-record serialized block at Balance +0x30..+0x80 is now tied to the manager financial-objective system, not chairman spending budgets.

Periodic routine 0x5E12C0 runs on Balance+0x30 and emits EAMManagerWarnedObjective plus EAMMonthlyFinancialTargets. The latter's EA-authored formatter labels its values BALANCEA, BALANCEB, PROFITA, PROFITB and TARGET. Nearby Balance+0x30 routines emit EAMManagerObjectiveGoodWork and continued-success/failed-objective events.

Therefore none of the six +0x30/+0x40/+0x50/+0x60/+0x70/+0x80 value records should be treated as the live transfer-budget store. Current cash remains Balance+0x10; transfer reserve must be elsewhere or derived.

Exact next target: use save-state ownership and quarterly board/business calculations outside the Balance objective block to locate the transfer/building reserve mutation.


## Bank-loan object checkpoint

The persistent 0x108-byte object at game/session +0x698 is now identified as bank-loan state. Constructor 0x5DED10 consumes explicit Bank1/Bank2/Bank3 loan amount, term and APR tuning globals, and the object is serialized through 0x5DF360/0x5DF430.

Therefore +0x698 is not the live chairman transfer-budget reserve.

Exact next target: continue eliminating/identifying the remaining persistent game-owned finance/business objects, especially +0x690 and any quarterly board-state owner, while tracing the overspending reserve mutation.


## Finance category 1100 correction checkpoint

The apparent 0x44C-byte chairman-warning allocations in Balance.cpp were rechecked and are not allocations. At those sites 0x44C is the accounting-category argument **1100** passed to ledger aggregation/posting routines.

Real Stadium Manager/Groundsman expenditure paths at 0x5D21E5/0x5D2440/0x5D2712/0x5D2963 use the same category 1100 before debiting current cash through 0x5DC650, and Finance Overview queries category 1100 through 0x43F1E0.

Thus category 1100 is a real stadium/grounds/facility expenditure ledger category. The equality between decimal category 1100 (0x44C) and the 0x44C-byte EAMchairbudgetwarning object size is coincidental.

No incorrect event-producer conclusion from this lead was committed.


## Concession-offer object checkpoint

The remaining persistent finance-looking object at game/session **+0x690** is now identified and ruled out as chairman budget storage.

It is a 0xB50-byte object containing eight 0x168-byte offer records. Its live tuning inputs are explicitly named:

- `FCConcessionOfferMinWait`
- `FCConcessionOfferMaxWait`

and its periodic routine `0x5E5640` can credit current cash through Balance routine `0x5DC510`.

Therefore +0x690 is the **food/concession offer subsystem**, not the transfer/building reserve.

Exact next target: continue with the quarterly chairman rebudget producer / remaining board-state owner rather than +0x690.


## Sponsor-offer object checkpoint

The persistent object at game/session **+0x69C** is now identified as the sponsor-offer/sponsor-state subsystem. Its update routine `0x617C80` consumes tuning values loaded from:

- `FSNoSponsorMinWait`
- `FSNoSponsorMaxWait`
- `FSHaveSponsorMinWait`
- `FSHaveSponsorMaxWait`

with the same loader family continuing into `FSOfferMinLifeTime`.

Therefore +0x69C is not chairman transfer-budget storage.

Exact next target: trace the quarterly budget-failure/sacking path (including `EAMManagerSackedFailedBudget`) and the remaining board-state/event scheduler objects rather than guessing additional club fields.


## Failed-budget sacking event checkpoint

`EAMManagerSackedFailedBudget` is now mapped as event ID **0x190**. Its producer uses game/session sacking-reason value 5.

Reason 5 is set explicitly inside `0x5E1D90`, the already-proven financial-objective tolerance routine that compares current cash with the Balance objective target using `ChairmanPercentBudgetMiss`.

So this named “FailedBudget” sacking event belongs to **financial-objective failure**, not the quarterly chairman rebudget path that takes money from building/transfer reserves.

Exact next target remains the quarterly board-budget producer / remaining persistent board-state owner.


## ChairmanNotEnoughFunds cash-gate checkpoint

`EAMChairmanNotEnoughFunds` is now tied to a real gameplay producer at `0x4EECA0`.

The producer first tests the requested amount through the already-proven current-cash affordability helper `0x404AE0`; the chairman-not-enough-funds event is created only when that cash check fails. Therefore this event is another **current Balance cash** notification, not the missing chairman transfer-budget reserve check.

Exact next target remains the quarterly rebudget producer / event population path that supplies `EAMchairbudgetsettings +0x58 = TRANSFERBUDGET`.


## Monthly finance-history checkpoint

The monthly business/calendar path around `0x429CB0` is now tied to RTTI class **CMonthHistory**.

Each month the game builds a 0x68-byte finance snapshot from cash, Balance aggregates, commercial/attendance data, season-ticket state and club values, then appends it to the persistent history container at game/session **+0x6DC**.

This gives a concrete historical-finance input that may feed quarterly chairman rebudgeting. Exact field names remain partly unresolved, and CMonthHistory should not yet be called the transfer-budget store itself.

Exact next target: trace readers of game/session +0x6DC that run on quarterly/board paths and determine whether they calculate the values later placed into EAMchairbudgetsettings, especially +0x58 TRANSFERBUDGET.


## Stadium object checkpoint

The large unresolved persistent object at game/session **+0x6B0** is now decisively identified as the **stadium model/state**.

It is a 0x1BC4-byte object constructed by `0x65CB20`, contains an RTTI-identified `CEntriesList`, and during club setup `0x65D5B0` loads the stadium asset. Failure leads directly to EA's literal warning that the stadium could not be loaded and that building screens/ticketing will not work.

Therefore +0x6B0 is not chairman transfer-budget storage. Its use in `CMonthHistory` supplies stadium/attendance/ticketing context.

Exact next target: continue tracing quarterly board-budget calculation and/or retrieval of prior `EAMchairbudgetsettings` state rather than remaining stadium/business objects.


## DBRUser architecture checkpoint

RTTI now proves the large object previously called the "game/session" object is actually **DBRUser** (vtable 0x7BDF4C, constructor ~0x424CA0).

This object owns the six Balance pointers and all the mapped per-manager finance/business state at +0x670 onward, including funding requests, commercial state, concessions, season tickets, bank loans, sponsors, training, stadium, movements and monthly histories.

This materially narrows the transfer-budget search: the chairman allocation should be treated as **per-user DBRUser-owned or DBRUser-derived state**, not as a global club scalar by default.

Exact next target: inspect DBRUser fields and rule/board logic that populate EAMchairbudgetsettings, especially transfer budget +0x58, and test whether the value is persisted directly or reconstructed from user financial history/ledger state.


## Media-rights block correction checkpoint

The five-qword DBRUser block at **+0x588..+0x5A8** has been ruled out as the five chairman operating budgets. Routine `0x4268C0` initializes it from tuning values named `LRADIO_MAX/RES`, `NRADIO_MAX/RES`, `LTV_MAX/RES`, `NTV_MAX/RES`, and `EUROPEAN_MAX/RES`.

So this block is media-rights/reserve state, not chairman budget storage. The apparent five-values/five-budgets match was coincidental.

Exact next target: continue mapping unresolved DBRUser finance/board fields and trace the periodic board-budget producer that supplies `EAMchairbudgetsettings +0x58`.


## DBRUser support-staff list checkpoint

The repeated DBRUser triplets at **+0x5B8, +0x5C4 and +0x5D0** are now identified as list containers for RTTI class **CSupportStaff**. Load code reconstructs 0x218-byte CSupportStaff objects and appends them through the common list helper. The adjacent +0x5E0 triplet is also list/container state.

Therefore this structured DBRUser block is not chairman budget storage.

Exact next target: continue through the monthly/calendar path at `0x42AEB0` and its downstream board/business logic, looking for the producer or derivation supplying `EAMchairbudgetsettings +0x58 = TRANSFERBUDGET`.


## Monthly maintenance dispatcher checkpoint

Monthly routine `0x42AEB0` has been ruled out as the chairman rebudget producer. It dispatches three maintenance cash debits:

- category **601**: stadium-size maintenance selected by `SM_10000..SM_100000`;
- category **602**: major facilities (School/Hotel/Hospital/Club/Training/Parking/Merchandising) with level-based maintenance;
- category **603**: pitch systems (sprinklers/drainage/pitch cover/heating) with level-based maintenance.

All three debit current Balance cash through `0x5DC650`.

This also identifies DBRUser +0x65C as a facility/building collection and +0x6A8 as pitch/stadium-installation maintenance state rather than chairman budget storage.

Exact next target: continue in the periodic/event path and locate quarterly board-budget calculation or retrieval/population of `EAMchairbudgetsettings +0x58`.


## Transfer-window calendar checkpoint

The daily DBRUser calendar path directly emits the FA transfer-window event family:

- 0x88 = `EAMFAtransferdeadlinesoon`
- 0x89 = `EAMFAtransferdeadlinenow`
- 0x8A = `EAMFAtransfernegstart`

with constructor/populators `0x56D9A0`, `0x56DC10`, and `0x56DE00` respectively.

This branch is transfer-season/calendar logic, not chairman rebudgeting. Resume the finance search from other periodic/board routines rather than these daily transfer-window messages.


## Monthly budget-event layout checkpoint

`EAMbcmonthlybudget` is now exactly mapped:

- event ID **0xA1**
- vtable **0x7D01A4**
- constructor `0x541B20`
- serializer `0x5730C0`
- formatter `0x573190`

Confirmed fields:

- +0x3C TOTALBUDGET
- +0x40 STAFFBUDGET
- +0x44 PLAYERWAGEBUDGET
- +0x48 MAINTENANCEBUDGET
- +0x4C MISCBUDGET
- +0x50 BUILDINGSBUDGET
- +0x54 TRANSFERBUDGET
- +0x58 serialized context/identity field, exact name unresolved

This corrects older notes that did not distinguish the monthly layout from the season budget-settings layout. The monthly statement has no separate merchandising field.

Exact next target: recover the gameplay producer/populator of event 0xA1 and trace how +0x54 TRANSFERBUDGET is calculated from prior allocation, ledger flow, or DBRUser state.


## Match-engine feasibility checkpoint

A targeted feasibility investigation of the previously uncertain match/FastView side has produced a significantly more favorable architecture picture.

Confirmed:

- high-level match routine `0x513010` has a separable normal calculator path and a developer-controlled `/skipmatchcalc777` bypass;
- normal calculation routes through `0x632B20`, which runs stages `0x62AC90 -> 0x62FBC0 -> 0x667E20`;
- MatchCalculator exposes named tactics/player/substitution command classes;
- FastView consumes semantic goal/score/possession/substitution/time/penalty/player-update events;
- the 3D side loads structured external scenario/AI/motion data rather than hiding all behavior in code;
- the exact disc has **235 loose SCI files**;
- loose `SCTABLE.STI` has **137 × 48-byte** scenario-selection records, directly confirmed by loader `0x70F000`;
- `AISCRIPT.VIV`, `MOAI.VIV` and `GEN4TBLS.T` are straightforward BIGF archives;
- `MOAI.VIV` has **584** motion/animation-named entries;
- `AISEQS.TBI` and `AITMPS.TBI` each contain **452 × 20-byte** primary records plus **585 × 24-byte** secondary entries;
- all **584 nonblank AISEQS names** match the 584 MOAI archive entry names;
- `CAMERA.SCR` is plaintext camera configuration.

Assessment: backend match reconstruction now appears **feasible**, and exact 3D choreography is separable from the core calculator. The hard remaining problem is recovering match decision/probability mathematics, not penetrating an opaque asset format.

Detailed evidence is in `research/MATCH_ENGINE.md`; reproducible format checks are in `tools/inspect_match_assets.py`.

Match-side next target when this branch resumes: map the MatchRecord state and the three normal calculation stages, then trace semantic event generation before attempting exact SCI/MOAI playback.



## Core match-calculator loop checkpoint

The uncertain backend has now been traced beyond architecture into its actual simulation shape.

Corrections/new findings:

- `0x667E20`, previously listed as a possible third calculation stage, is a no-op `ret`;
- `0x62AC90` initializes match/player state;
- `0x62FBC0` drives repeated calls to main simulation routine `0x62AE90`;
- normal time is simulated in **5-minute chunks** (5..40, boundary 45, then 50..85);
- extra time uses 95/100, boundary 105, then 110/115;
- penalty state begins at minute 90 or 120 depending whether extra time is used;
- `0x62B1A0` is the five-minute segment simulator;
- its two symmetric strength routines `0x62F140` / `0x62F3E0` iterate players and all **17 current skills**, apply role/context/tactical weight tables, and return floating team aggregates;
- segment outcomes are then sampled through RNG `0x64D5B0` and dispatched into lower event-generation routines.

This materially strengthens feasibility: the backend is a finite, discrete weighted event simulator with recoverable formulas, not an inseparable 3D simulation.

Exact next match target: map `0x62C740` and the `0x62E1xx/0x62E2xx/0x62E6xx` event branches to semantic outcomes (shots/goals/fouls/cards/injuries/possession), then identify the two team-strength dimensions.



## MatchCalculator-to-FastView event mapping checkpoint

The linked MatchCalculator record stream is now directly tied to named FastView sender classes.

Confirmed type map from record +0x28:

- **0..4** = goal-event family routed through `Sender<EventGoal>`
- **5** = unresolved player incident/state family
- **6** = HalfTime
- **7** = FullTime
- **8** = ExtraTime
- **9** = Penalties
- **10** = Substitution

A type-1 goal-family record is rerouted through `Sender<EventPenaltyShootoutShot>` while the controller is in penalty-shootout state.

Multiple type-0..4 producer branches directly increment the home/away score pair at match record +0xD4C/+0xD50 before appending the record, proving that this family carries scoring events.

This removes a major reconstruction uncertainty: the simulator's linked record timeline has a recoverable semantic interface into FastView.

Exact next match target: distinguish goal-family types 0/1/2/3/4 and map type 5 to its player incident (card/injury/other) semantics.

## Active Investigation

Current focus: locate the authoritative chairman transfer-budget allocation from the now-confirmed **DBRUser** runtime architecture.

Confirmed constraints that define the search:

- transfer purchases are gated by current cash, stored at active Balance +0x10;
- transfer fees are posted through accounting category 1000;
- the chairman transfer budget is a separate mutable reserve/reference allocation;
- automatic extra-transfer success notifications are presentation-only, so their mutation occurs earlier in board/finance logic;
- quarterly overspending can consume building and transfer reserves;
- EAMchairbudgetsettings +0x58 is the displayed TRANSFERBUDGET value;
- DBRClub shortcut blocks, Balance objective records, funding-request state, bank loans, concessions, sponsors, stadium state and the DBRUser media-rights block have all been ruled out as the live transfer-budget store;
- CMonthHistory at DBRUser +0x6DC is a confirmed persistent monthly financial-history input and remains a possible ingredient in quarterly recalculation.

Immediate next steps:

1. Map remaining unresolved DBRUser finance/board fields and periodic board routines that can populate EAMchairbudgetsettings, especially +0x58.
2. Determine whether transfer budget is persisted directly or reconstructed from financial history, category-1000 transfer flow, and board reserve rules.
3. Once the transfer-budget derivation is proven, trace exactly how purchases, sales, quarterly overspending and automatic chairman increases change the displayed allocation.
4. Map remaining transfer-proposal fields +0x40/+0x44/+0x4C.
5. Finish exact CDealInProgress state names where named callbacks provide decisive evidence.
6. Return to the cheat-command decoder as a secondary line of work; /cash777 behavior is confirmed, while 0x877552 / /budget777 remains unresolved.
7. Then broaden into season AI, scouting/youth, save serialization and the match engine/FastView.

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


## 0x877540 type correction checkpoint

Fresh structural analysis supersedes the earlier claim that global `0x877540` is itself a `std::basic_istringstream`. Its constructor `0x5162A0` builds a 16-byte ordered-tree/container header with a self-linked 0x24-byte sentinel node and no vtable. The stream RTTI found previously belongs to separate routines beginning around `0x516370`.

Consequently the bytes at `0x877550..` are adjacent globals, not istringstream fields. The getter family `0x515FF0..0x5160E0` is therefore reopened as option/cheat-state accessors, but literal-to-byte assignments still require parser proof. `0x516090 -> 0x877559` is again a strong `/cash777` candidate from four cash-affordability consumers; `0x516020 -> 0x877552` remains unresolved.

Exact resume point: identify how the literal command table at `0x828510..0x828568` populates the adjacent global option bytes/tree, then prove `/budget777` and follow its consumers into live transfer-budget storage.
