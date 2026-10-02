# Premier League Manager 2001 Reverse-Engineering Progress

_Last updated: 26 September 2026_

## Purpose

This file is the **chronological project log**. It preserves dated checkpoints, including older "current" statements that may later be superseded.

The canonical live resume point is now `research/CURRENT_STATE.md`, with long-term sequencing in `ROADMAP.md`. New sessions should not treat early status sections in this file as current merely because they appear near the top.

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

## 25 September MatchCalculator completion checkpoint

The normal-time backend has advanced beyond the former scoring-only orchestration boundary.

Now clean-room implemented and integrated from direct executable evidence:

- all 16 normal-time five-minute strength/scheduler passes;
- type-1 open play plus exact type-2 free kick, type-3 corner and type-4 penalty handoffs;
- Team Orders captain and set-piece priority behavior;
- recurring Condition decay and exact injury-incidence gate;
- immediate injury replacement through the original substitute selector/mutation path;
- exact booking/sending-off path and active-player removal;
- exact five-minute possession/territory normalization;
- exact `RNG(7)==0` automatic AI-substitution trigger and call order;
- AI substitution timing (normally 60/70/80 as original starters leave active state);
- exact role-rating helper `0x41C7E0` and Form-adjusted outgoing/incoming comparison;
- type-10 substitution event payload and runtime position/status mutation;
- due Premier League fixture -> reconstructed result -> live table integration.

Important preserved field distinction:

- assigned/current role = position-state `+0x03`;
- substitution auxiliary low nibble = `+0x04`;
- strength/discipline balance-position code = separate `+0x05`.

Substitution copies `+0x03` and `+0x04` from outgoing to incoming, but does not copy `+0x05`.

### Historical primary blocker at this checkpoint (superseded)

At this dated checkpoint, the backend calculator could execute a normal match when explicit prepared match-day state was supplied. The then-next fidelity/playability target was **authoritative match-day initialization**.

Later 25 September work implemented the autonomous AI preparation path, so this is retained as history rather than a live blocker:

1. identify how the original chooses/marks starting XI and substitute-available participants;
2. recover initial assigned roles and the `+0x04/+0x05` position-state values;
3. recover match-start Form and Condition state;
4. recover AI Team Orders/tactical setup and set-piece/captain priorities;
5. connect those original initialization paths to the existing simulator so a scheduled fixture no longer needs manually prepared inputs.

Secondary unresolved match details include the higher-level semantic names of MatchCalculator `+0xD3C` and shared guard `+0x1145`, plus exact FastView/3D choreography.

Regression source exists for the new role-rating, automatic-substitution, injury-replacement, dynamic Condition-iteration and scheduler integration paths. This chat environment still has no runnable GitHub checkout, so the complete repository test suite has **not** been executed here. Do not report the whole suite as passing until checkout/CI execution confirms it.

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



## Match incident/substitution/condition checkpoint

The match branch has been decomposed further:

- MatchCalculator **type 5** is a per-player incident/status family with three independent subtype flags stored in a 3-byte matrix per player;
- exact labels of the three flags are still unresolved and are deliberately not yet called cards/injury;
- `0x62E2F0` is confirmed AI substitution decision logic and emits type-10 records through `0x62EF90`;
- `0x62E6F0` is a recurring **Condition** decay routine; player +0x77 is now proven as Condition through the `ConditionInjuryInducingLevel` tuning key, and `0x62EAE0` is the subsequent injury check.

Exact next match targets:

1. identify the three type-5 incident flags;
2. connect `0x62EAE0` to the named energy/form FastView event and give player +0x77 its final semantic name;
3. prove player +0x1B7 as the user-adjustable aggression instruction and map its role in incident probabilities;
4. continue distinguishing goal-family record types 0..4.



## Match discipline/injury semantics checkpoint

Type-5 is now fully resolved at the top semantic level:

- subtype/status byte 0 = **Booked / yellow card**;
- subtype/status byte 1 = **Sent Off / red card**;
- subtype/status byte 2 = **Injured**.

Supporting state:

- per-player match byte +0x48 = booked state;
- per-player match byte +0x49 = sent-off state;
- MatchController maps the three subtypes through `0x6C28F0/0x6C2910/0x6C2930`;
- lineup/AI logic excludes players whose sent-off byte is set;
- the injury subtype is generated from the Condition-driven `0x62EAE0` path and can trigger a type-10 replacement/substitution.

Player runtime +0x77 is confirmed **Condition**. Tuning loader maps `ConditionInjuryInducingLevel` to global 0x821814, which is directly compared against +0x77 in the match injury generator.

Player +0x1B7 is confirmed as the 0..9 **Aggression** instruction/setting; it drives booking/dismissal probabilities and matches the named MatchCalculator `AggressionCommand`.

Exact next match target: distinguish goal-family types 0..4 and map their payload fields/player attribution.



## Match own-goal encoding checkpoint

Goal-family own-goal semantics are now resolved independently of record types 0..4.

- calculator record +0x04 = player's actual side;
- +0x08 = player index;
- +0x20 = **scoring-side inversion / own-goal flag**;
- MatchController derives credited side as `+0x20 ? !+0x04 : +0x04`;
- FastViewPanel callback `0x522690 -> 0x524880` compares credited side with actual player side;
- equal -> `Sender<EventPlayerGoal>`;
- different -> `Sender<EventPlayerOwnGoal>`.

Thus own goals are **not a dedicated one of types 0..4**. The remaining scoring-type investigation should identify source/context such as open play or set-piece variants.

Exact next match target: map types 0,1,2,3,4 through their creators/call-site contexts and the +0x24/+0x2C fields.



## Match chance-outcome encoding checkpoint

The ambiguous scoring records are now resolved structurally.

For MatchCalculator goal/chance-family records:

- `record +0x28` = chance/source family type;
- `record +0x24 mod 3` = result:
  - 0 = **goal**
  - 1 = **miss / failed chance before goalkeeper-save resolution**
  - 2 = **saved/stopped by goalkeeper**
- the record creators occasionally add +3, yielding 3/4/5 as presentation variants of the same three base outcomes;
- MatchController sends semantic `EventGoal` only for +0x24 values **0 or 3**;
- `record +0x20` remains the independent own-goal/scoring-side inversion flag.

This explains why types 2/3/4 appeared on both scoring and non-scoring branches: type encodes the source family, not whether the chance scored.

Exact next match target: map source-family types 0..4 and the remaining +0x2C context field.



## Match source-type 0 checkpoint

Direct creators and MatchRecord serialization now agree that only chance/source types **1, 2, 3, and 4** are actively generated/reconstructed in this release. FastView accepts type 0, but no normal producer has been found and the serializer never rebuilds it.

Treat type 0 as **unused/reserved/legacy-compatible** unless new producer evidence appears.

Exact next match target: assign EA-grounded semantics to active source types 1..4 using report/stat counters, source-branch logic, and original string/tuning evidence.



## Reconstruction development/training implementation checkpoint

The first recovered gameplay mechanics are now implemented in clean-room Python and covered by deterministic unit tests.

New reconstruction files:

- `reconstruction/player_development.py`
- `reconstruction/test_player_development.py`

Implemented from verified executable behavior:

- raw skill -> displayed rating conversion and minimum rating floor;
- monthly age/development curve for both baseline-before-peak and baseline-after-peak cases;
- 0..4 / 5..8 / 9..16 peak grouping;
- five-year peak plateau default;
- exact monthly per-skill training modifier including the original overshoot quirk;
- exact seven 17-byte training profiles from `0x4EAA00`;
- Youth Team Coach / Assistant Manager / Training Centre quality multiplier;
- active training success threshold;
- strict +8 skill step at `0x41A870` and -8 reversal at `0x41A9A0`;
- high-exclusive peak-age selection behavior.

Local verification: **13 unit tests pass**.

This is the first substantial move from research-only knowledge into executable reconstruction logic.



## Mutable runtime/calendar reconstruction checkpoint

The clean-room reconstruction now has a mutable runtime layer rather than read-only database records.

New files:

- `reconstruction/runtime_state.py`
- `reconstruction/game_state.py`
- `reconstruction/test_runtime_state.py`

Implemented:

- conversion of immutable parsed players into mutable `RuntimePlayer` state;
- initialization of verified development baseline/peak state;
- baseline-age clamp to 15..50 matching `0x41E970`;
- player training-modifier storage;
- mutable monthly skill recalculation;
- a generic day-by-day `GameCalendar` with daily and monthly hooks;
- first-of-month dispatch of player development across runtime players;
- deterministic seed support for reconstruction/test peak generation.

The current `age_on()` helper uses conventional whole-year birthday age. The original player-age accessor is known but its exact calendar edge-case helper is not yet instruction-mapped, so this helper is intentionally isolated for later replacement if needed.

Local regression status: **20/20 tests pass** across development/training/runtime/calendar modules.

This moves the reconstruction from a data browser toward an actual advancing game state.



## Premier League fixture/table reconstruction checkpoint

The clean-room parser now reads the verified real Premier League fixture table from `Static.dat` at `0x10057`.

Confirmed against the original extracted files:

- 380 fixtures;
- 38 round indices;
- exactly 10 fixtures per round;
- 20 participating clubs;
- each club appears in 38 fixtures;
- each club has 19 home and 19 away fixtures.

New reconstruction module `competition_state.py` provides mutable fixture results and league standings (P/W/D/L/GF/GA/GD/points) plus next-unplayed-round selection.

The exact FM2001 equal-points fallback after points/goal difference/goals scored is not yet traced, so that final tie-break is isolated in one sort function for later correction.

Regression status: **23/23 tests pass**, plus the original data integrity check above.

This gives the reconstruction its first real season competition state: original teams/fixtures can now receive match results and produce a league table.



## Integrated season-state skeleton checkpoint

`GameState` now combines:

- mutable runtime players;
- the advancing game calendar;
- first-of-month development updates;
- the original 380-match Premier League schedule;
- mutable match results;
- live league-table calculation.

A loaded database can therefore create one coherent career-state object rather than separate parser demos.

New regression file: `reconstruction/test_game_state_competition.py`.

Regression status: **25/25 tests pass** across development, training, runtime/calendar, fixture parsing, league-table state and integrated game-state behavior.

No placeholder match simulator has been invented: results are currently injected explicitly until the recovered MatchCalculator is ready to replace that boundary.



## Real Premier League calendar scheduling checkpoint

The reconstruction now parses all **1,053** Static.dat round records and maps the 38 Premier League rounds onto actual season dates.

Verified schedule interpretation:

- scheduled weekday **1..7 = Monday..Sunday**;
- week 0 is the Monday-led week containing July 1 of the season start year;
- date conversion reproduces the shipped 2000–01 calendar, including:
  - round 1: 19 Aug 2000;
  - round 2: 23 Aug 2000;
  - Boxing Day round: 26 Dec 2000;
  - New Year's Day round: 1 Jan 2001;
  - final round: Sunday 20 May 2001.

The exact original files verify:

- 1,053 total round definitions;
- 38 Premier League round definitions;
- 10 fixtures due on each PL matchday.

`PremierLeagueState` now exposes round dates, fixtures due on a date, and the next unplayed match date. `GameState` exposes `fixtures_due_today()` and `next_match_date()`, so the advancing calendar can now reach the original league matchdays naturally.

No match result is auto-generated yet; the MatchCalculator reconstruction remains the intended producer.

Regression status: **28/28 tests pass**, plus exact-source parser/date verification.



## Match Team Orders / penalty chance checkpoint

Confirmed:

- `PTeamOrders2K` is the Team Orders screen owning the ordered player-priority lists used by MatchCalculator;
- priority category **0 = captaincy order**;
- priority category **1 = penalty-taker order**;
- chance source type **4 = penalty kick**.

Type-4 resolver `0x62D660` selects through the category-1 penalty list, tests the taker's Shooting, then the opposing goalkeeper's Goalkeeping, and emits goal/miss/save using the existing +0x24 outcome model.

Categories 2 and 3 are still being traced against the corner/free-kick Team Orders lists; do not promote their exact ordering until that path is proven.

Exact next match target: prove category2/category3 = corner/free-kick order and thereby label chance types 3 and 2; then classify remaining type1 as the ordinary/open-play family if no contrary producer appears.



## Match chance-source taxonomy checkpoint

The active MatchCalculator chance-source taxonomy is now resolved:

- type 0 = unused/reserved
- type 1 = **ordinary/open-play chance**
- type 2 = **free kick**
- type 3 = **corner**
- type 4 = **penalty kick**

Team Orders priority categories used by the calculator are now:

- category 0 = captaincy
- category 1 = penalty takers
- category 2 = corner-kick order
- category 3 = free-kick order

Evidence for types 2/3 is structural, not name-order guessing: the category-2/type-3 resolver selects a set-piece taker plus a separate receiving attacker and uses Heading in the delivery/finish path, while category-3/type-2 is a direct designated-taker free-kick path. EA's Team Orders strings independently agree with the category ordering.

Type 1 is the only normal-play chance family used by the common open-play generator after dedicated free-kick/corner/penalty paths are separated. Penalty shootouts reuse type 1 only under shootout phase routing.

Exact next match target: recover the ordinary/open-play source substructure and the remaining +0x2C context flag, then map shot/stat counters sufficiently to implement a first faithful MatchCalculator slice.



## Typed MatchCalculator event reconstruction checkpoint

The clean-room reconstruction now has a typed semantic event layer in `reconstruction/match_events.py`.

Implemented only from verified MatchCalculator semantics:

- `ChanceSource`: 1 open play, 2 free kick, 3 corner, 4 penalty;
- `ChanceOutcome`: goal/miss/save from `record +0x24 mod 3`;
- the 3/4/5 presentation-variant bank;
- player actual side/index;
- `record +0x20` scoring-side inversion / own-goal attribution;
- type-5 Booked / Sent Off / Injured incident subtypes;
- type-6/7/8/9 HalfTime / FullTime / ExtraTime / Penalties boundaries;
- type-10 substitution code preserved as the known record type;
- `record +0x2C` retained as `context_raw` with no invented semantic name;
- timeline score calculation from verified goal attribution.

New tests: `reconstruction/test_match_events.py`.

Local event-layer regression: **10/10 tests pass**. This establishes the exact semantic data boundary that the reconstructed probability engine can emit later without requiring FastView or 3D playback.

The current match-stat trace shows `+0x1000/+0x1004/+0x1008` are three segment buckets normalized together into percentage-like arrays, but their exact football labels are not yet proven. Do not label them as possession/territory until their readers establish semantics.



## Match possession/territory statistics checkpoint

The segment-stat arrays are now semantically separated:

- raw counters `+0x1000/+0x1004/+0x1008` = side 0 / neutral-contested / side 1 possession-control states;
- `+0x106C[index]` = normalized side-0 percentage;
- `+0x10CC[index]` = normalized neutral/contested percentage;
- side-1 percentage is reconstructed as `100 - first - second`;
- `+0x100C[index]` is a separate territorial/pitch-position metric.

MatchController retrieves all three values every five minutes and emits named `EventPossession`.

FastView `PossessionFigures.cpp` formats the three possession percentages, while `PossessionDiagram` consumes the +0x100C-derived value and switches among `pitch_left/pitch_middle/pitch_right` assets.

This is enough to model the original possession event shape in reconstruction without conflating possession share with territorial position.

Exact next match targets:

1. resolve chance-record +0x2C or prove it is nonessential to semantic FastView;
2. implement EventPossession in the clean-room event layer;
3. continue toward the first verified five-minute MatchCalculator slice.



## Chance context + possession reconstruction checkpoint

Chance record `+0x2C` is now resolved beyond the earlier Boolean-only checkpoint: **0 = headed finish, 1 = shooting/kicked finish**. Type-1 open play chooses between the two by weighted RNG over effective Heading + Shooting; type-2/type-3 repeat the same split, while penalties always use shooting mode. Reconstruction now exposes `FinishMode.HEADED` / `FinishMode.SHOOTING`.

`reconstruction/match_events.py` now also implements the verified `EventPossession` shape:

- territorial/pitch-position metric;
- side-0 possession percentage;
- neutral/contested percentage;
- side-1 percentage reconstructed as the remainder to 100.

Updated event regression status: **13/13 tests pass**.



## Penalty-resolver recovery checkpoint

The timeout did **not** lose the type-4 penalty disassembly. Local files preserved `0x62D660`, and the partial exact formula is now committed.

Confirmed:

- `0x64D5B0(N)` yields bounded integer RNG in `0..N-1`;
- effective Shooting/Goalkeeping uses `(floor(Condition/3)+66) * skill`, then position/role compatibility, then Form, with truncation after each floating multiplier;
- Form states 0..4 map to 0.90 / 0.95 / 1.00 / 1.05 / 1.10;
- miss branch: one `RNG(3)` path performs `RNG(256)` versus `floor(effective_shooting/100)`;
- save branch: `RNG(800)` versus `floor(effective_goalkeeping/100)`;
- successful scoring then passes `RNG(10) < 10-current_score` before score increment/type-4 GOAL record;
- the remaining implementation blocker is the exact input/state needed for the already-numeric position/role compatibility helper `0x4EA440`.

Exact next step: model `0x4EA440` sufficiently to reproduce its multiplier, then implement the penalty resolver with deterministic RNG tests.



## Exact penalty-resolver implementation checkpoint

The first fully evidence-backed MatchCalculator chance resolver is now implemented.

New files:

- reconstruction/match_calculator.py
- reconstruction/test_match_calculator.py

Implemented from the exact executable path:

- zero-based PositionRole codes;
- full 0x4EA440 position-compatibility table;
- five shipped Form multipliers;
- exact Condition × skill × position × Form effective-strength pipeline;
- type-4 penalty MISS / SAVE / GOAL branches;
- exact RNG call ordering and bounds;
- original high-score suppression gate;
- 10% +3 presentation-variant roll;
- original type-4 Boolean context flag.

Local regression: **15/15 new MatchCalculator tests pass**.

This is the first original FM2001 chance-resolution routine running as clean-room replacement code rather than only research notes.

Exact next step: implement the verified five-minute match phase/boundary scaffold, then reverse and add type-1 open-play selection/resolution.



## Match clock scaffold checkpoint

New reconstruction files:

- `reconstruction/match_clock.py`
- `reconstruction/test_match_clock.py`

The verified `0x62AE90` timeline is now executable:

- 16 normal-time five-minute simulation calls;
- HalfTime at 45;
- optional ExtraTime boundaries at 90 and 105 with simulation at 95/100/110/115;
- Penalties boundary at 90 or 120 depending whether extra time occurred;
- final FullTime record at 90, 120, or 130.

The clock module does not invent competition rules; it accepts upstream `extra_time` / `penalties` decisions and only reproduces the original phase schedule.

Local combined MatchCalculator/clock regression: **19/19 tests pass**.

Exact next step: reverse the type-1 open-play selection and shot-resolution path sufficiently to implement the first normal five-minute scoring slice.



## Match finish-mode checkpoint

The previously opaque one-bit chance field `+0x2C` is now semantically resolved:

- 0 = **headed finish**
- 1 = **shooting/kicked finish**

Type-1 open play computes effective Heading and Shooting using the shared Condition × skill × position × Form pipeline, draws `RNG(heading+shooting)`, and selects the headed branch when the roll is below Heading. The two branches emit +0x2C 0 and 1 respectively.

Type-2 free kicks and type-3 corners independently reproduce the same two modes. Type-4 penalties always emit shooting mode.

The clean-room event schema and exact penalty resolver are updated to use `FinishMode` instead of an opaque context flag.

Exact next target: reverse the type-1 helper routines `0x62BD80`, `0x62BFC0`, `0x62C0D0`, `0x62C310`, and `0x62C530` to recover open-play save/goal/miss/own-goal decisions.



## Open-play primitive reconstruction checkpoint

The five helper routines underneath type-1 open play are now mapped and implemented as reusable clean-room primitives:

- `0x62BD80`: Heading-vs-Heading aerial duel;
- `0x62C0D0`: Control-vs-Tackling duel;
- `0x62BFC0`: headed-finish accuracy gate;
- `0x62C310`: shooting-finish accuracy gate;
- `0x62C420`: Set Piece execution gate;
- `0x62C530`: goalkeeper/high-score stop gate.

The shared accuracy helpers use `RNG(320)` against `floor(effective_skill/100)`, then an `RNG(2)==0` fallback.

The type-1 record creator `0x62ECF0` is also mapped: before minute 130 it suppresses plain miss records unless the 10% +3 presentation-variant roll turns MISS 1 into MISS 4. At minute >=130 it keeps misses and does not add the +3 variant.

These behaviors are added to `reconstruction/match_calculator.py` with deterministic tests.

Exact next target: map the type-1 player-selection/setup routines and the branches taken when the aerial or Control/Tackling duel fails, so the complete open-play chance resolver can be assembled without placeholders.



## Type-1 outer open-play flow checkpoint

The normal-play shell around `0x62C740` is now mapped beyond the reusable helper formulas.

Confirmed sequence:

1. rebuild active positional pools with `0x62DE90`;
2. `RNG(100)<5` -> direct type-3 corner;
3. otherwise choose initial carrier primarily from RM/LM/CM, fallback RW/LW/AM;
4. choose a role-matched defender;
5. resolve Control-vs-Tackling; defender win aborts;
6. require a Passing gate via `RNG(320) < floor(effective_passing/100)`;
7. select finisher with ~50% CF/ST, 25% RW/LW/AM, 25% RM/LM/CM weighting subject to availability;
8. select a closer role-matched defender;
9. choose Heading vs Shooting finish mode unless carrier==finisher, which goes directly to Shooting;
10. resolve the already-implemented duel, accuracy, and goalkeeper primitives.

If the final aerial or Control/Tackling duel is lost:

- `RNG(4)==0` with defender -> `RNG(100)<20` penalty, otherwise free kick;
- otherwise `RNG(2)==0` -> corner;
- otherwise no chance event.

Successful open-play goals also contain a `RNG(20)==0` own-goal attribution branch when a close defender exists.

Exact next target: implement these positional pools/selection routines as clean-room helpers, then assemble the complete type-1 resolver and verify all branch/RNG ordering against `0x62C740`.



## Open-play positional-selection implementation checkpoint

The verified 0x62DE90 / 0x62B780 / 0x62B7D0 / 0x62B900 / 0x62BCE0 role-pool and player-selection layer is now implemented in reconstruction/match_calculator.py.

Implemented: active role pools; initial carrier selection; role-matched first and close defenders; exact one-roll finisher fallback behavior; 0x62B9D0 defender-wins Control/Tackling Boolean; and the 0x62BBF0 Passing gate with no RNG(2) fallback. MatchSkillPlayer now carries Passing.

Next step: assemble these selectors with the existing finish/accuracy/goalkeeper primitives into the complete type-1 resolver and attach the mapped set-piece transitions.



## Outer type-1 open-play resolver implementation checkpoint

The verified outer 0x62C740 flow is now assembled in reconstruction/match_calculator.py as resolve_open_play_attempt(). It preserves the 5% direct-corner branch, possession/control increments, carrier/defender selection, early Control/Tackling abort, Passing gate, finisher/close-defender selection, forced shooting when carrier==finisher, Heading-vs-Shooting finish path, accuracy and goalkeeper gates, normal miss suppression, 5% own-goal attribution, and the exact lost-duel handoff structure to penalty/free-kick/corner.

Dedicated type-2/type-3 resolvers are not fabricated: the open-play function returns the verified ChanceSource transition so the caller can invoke those exact resolvers once implemented.

Next target: reverse and implement type-2 free kicks and type-3 corners, then integrate all chance families beneath the five-minute team-strength/frequency driver.



## Free-kick / corner resolver implementation checkpoint

The post-taker-selection type-2 and type-3 resolvers are now implemented in reconstruction/match_calculator.py with deterministic branch tests.

Implemented:

- Shooting-vs-Passing ×1.2 direct/free-kick delivery choice;
- cached-context direct and receiver overrides;
- direct free-kick Shooting path;
- Set Piece execution gates and possession increments;
- receiver selection, cached forced-heading behavior, and corner receiver!=taker rule;
- shared duel/accuracy/goalkeeper and failed-duel transitions;
- type-2/type-3 presentation-variant behavior without side inversion.

The only upstream piece intentionally outside these functions is Team Orders taker selection; category 3 free-kick and category 2 corner priority lists are already mapped separately.

Primary next target: recover the five-minute chance-generation frequency/team-strength driver sufficiently to invoke the exact type-1/2/3/4 resolvers and produce a complete normal league match result.



## Five-minute attack-frequency driver checkpoint

0x62B1A0 is now mapped as the finite per-segment attack scheduler.

Given the two paired team-strength ratios it produces integer side weights W0/W1, with shipped 1.10 vs 0.90 bias, then runs floor((W0+W1)/30) attacking sequences. Each sequence chooses its attacking side through RNG(W0+W1), distributes its event minute inside the five-minute window, and calls 0x62C740 plus the condition/discipline update paths.

This removes the uncertainty around how often the already-implemented chance resolvers are called.

Immediate next target: fully map 0x62F140 and 0x62F3E0 so the two segment weights can be computed from the actual players/tactics rather than supplied externally. Once those are implemented, a complete normal 90-minute result becomes mechanically reachable.



## Team-strength builder checkpoint

The current frontier is now the pair `0x62F140` / `0x62F3E0`, which feed the already-mapped five-minute attack scheduler.

Confirmed structurally:

- one routine is the attacking/build-up strength path;
- one is the defensive/resistance strength path;
- both iterate active players and all 17 skills;
- role and team tactics select coefficients from large EA tables;
- formation/shape plus mentality/aggression/human-AI modifiers adjust the final aggregates.

A role-code naming inconsistency has also surfaced around advanced midfield/wing positions 13/14/15. Numeric codes are stable, but semantic labels may be shifted; verify Static.dat/original consumers before changing `PositionRole` names.

Exact next steps:
1. verify the 13/14/15 role-name mapping from original data;
2. decode the team-tactic bytes and coefficient-table indices used by 0x62F140/0x62F3E0;
3. implement both strength builders with deterministic tests;
4. connect them to the already-implemented five-minute attack scheduler to produce complete normal-match results.



## Team-strength modifier checkpoint

Committed separately from the coefficient-table discovery:

- attack bias multipliers 0.8/0.9/1.0/1.1/1.2;
- inverse defence bias multipliers;
- user-controlled-club predicate at 0x4037B0;
- captain selector at 0x408560;
- captain Confidence + Leadership attack/defence formulas;
- AI fixed ×1.05 attack / ×1.10 defence modifiers;
- aggression factor `1 + (value-5)*0.02`;
- defence-only formation coverage penalty from 0x62F6A0.

Immediate next target: extract the two original 4×20×17 matrices into a user-local data loader and implement the attack/defence strength builders around these verified modifiers.



## Per-player strength formula checkpoint

Exact contribution inside the team-strength matrices is now known:

`(effective_skill / 255) * coefficient[tactic][role][skill] * (role_factor / 100)`.

Attack role factors 0..12:
105,108,110,120,112,115,97,95,102,92,90,117,100.

Defence uses 200 minus those values; roles 13..19 use 100 for both.

Next: implement the exact formation-coverage helper and coefficient-matrix loader, then the two complete strength builders.



## Position-role enum consistency check resolved

The temporary concern about runtime roles 13/14/15 was resolved during the team-strength trace.

- runtime role codes remain **13 RW, 14 LW, 15 AM**;
- the apparent discrepancy came from Static.dat position IDs being one-based while runtime/Master.dat role codes are zero-based;
- no clean-room PositionRole enum correction is required.

Do not reopen this branch unless new executable evidence contradicts the confirmed zero-based runtime mapping.

## Active Investigation

Primary focus: complete and implement the exact type-1 ordinary/open-play resolver, then connect verified MatchCalculator output to scheduled fixtures.

Current verified MatchCalculator stack:

- exact role compatibility and effective-skill pipeline;
- exact penalty type-4 resolver implemented;
- match clock/phase scaffold implemented;
- type-1 duel, Passing/accuracy, goalkeeper, finish-mode, and record-creator primitives implemented;
- type-1 positional pools, carrier/defender/finisher selection flow, 5% direct-corner branch, failed-duel set-piece transitions, and 5% own-goal attribution branch mapped;
- typed chance/incident/boundary/possession event schema implemented;
- original Premier League calendar/fixtures/table and mutable player runtime already implemented.

Immediate next steps:

1. Implement the verified positional pool and selection helpers from `0x62DE90/0x62B780/0x62B7D0/0x62B900/0x62BCE0` with deterministic tests.
2. Assemble the complete type-1 open-play chance resolver preserving exact RNG order and all early-abort/set-piece branches.
3. Trace/implement type-2 free-kick and type-3 corner formulas, reusing the existing primitives.
4. Recover the five-minute chance-generation frequency/team-strength path sufficiently to make a complete league-match result evidence-backed.
5. Wire that simulator into scheduled Premier League fixtures and league-table updates.
6. Keep chairman transfer-budget derivation as the secondary finance investigation.
7. After a playable match loop exists, deepen season AI, scouting/youth, saves and FastView/SCI.

Secondary finance target: authoritative chairman transfer-budget value supplying `EAMchairbudgetsettings +0x58`.

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


## 25 September normal-match orchestration checkpoint

The former primary team-strength blocker is now implemented and connected to a clean-room normal-time match orchestrator.

Confirmed repository implementation:

- `reconstruction/match_strength.py`
  - exact `0x62F140` attacking-strength contribution pipeline;
  - exact `0x62F3E0` defensive-strength contribution pipeline;
  - original 4 x 20 x 17 coefficient matrices supplied through the data-free loader;
  - role balance factors, live match bias, captain/AI, aggression and defence formation coverage;
  - exact `0x62B1A0` attack weights, sequence count, side draw and within-segment minute distribution.
- `reconstruction/match_simulation.py`
  - explicit prepared match-day player state rather than guessed lineups/Condition/Form/Team Orders;
  - all 16 verified normal-time five-minute segment calls;
  - strength recomputation at each segment;
  - scheduler-selected type-1 open-play resolution;
  - exact handoffs into type-2 free kicks, type-3 corners and type-4 penalties;
  - dynamic score accumulation;
  - Half Time at 45 and Full Time at 90;
  - timed semantic event output.
- `GameState.simulate_premier_league_fixture()`
  - requires the fixture to be due on the current calendar date;
  - runs the reconstructed normal-time simulator;
  - records the resulting home/away score into `PremierLeagueState`;
  - therefore updates the live league table through the existing result/table path.

The exact Library disc image was re-materialized in this session and converted from raw MODE1/2352 to ISO9660 only in the temporary analysis environment. The root `FOOTBAL.EXE` matched the canonical SHA-256 and the existing coefficient loader successfully decoded both real 4 x 20 x 17 matrices. No original binary or game-data asset was committed.

Regression source has been added for:

- team-strength formulas and scheduler;
- one exact open-play scoring sequence;
- complete normal-time phase traversal;
- due-fixture simulation -> stored result -> league-table update.

Environment limitation: this chat session could not obtain a runnable local GitHub checkout, so the newly committed repository regression files have not yet been executed as one full suite in this session. Do not report them as passing until executed in a checkout/CI environment.

### Current backend boundary

The new orchestrator is a complete **normal-time scoring/chance backbone**, but it intentionally does not fabricate still-unimplemented per-sequence side systems. Remaining integrations before calling the backend MatchCalculator complete are:

1. recurring Condition decay and the `0x62EAE0` injury path;
2. aggression-driven booking/sending-off generation at `0x62E130`;
3. AI substitution decisions at `0x62E2F0` and type-10 mutation;
4. exact per-segment possession normalization / territorial value production;
5. authoritative match-day lineup/assigned-role/Form/Condition/Team Orders initialization from the original runtime paths.

The immediate playable path is now materially shorter: once prepared match-day state is available, a scheduled Premier League fixture can already traverse the recovered normal-time scoring engine and persist its score into the table without any generic score generator.


## Team-strength position-field correction checkpoint

A fresh instruction-level audit found and corrected one important implementation assumption in the newly added strength builders.

The 4 x 20 x 17 matrix index and the small 105/108/... balance-factor table do **not** use the same player-position field:

- assigned role `+0x03` / `0x4EA3C0` -> compatibility + coefficient-matrix role;
- separate position-state `+0x05` / `0x4EA3E0` -> small attack/defence balance factor.

The reconstruction now requires this second value explicitly as `balance_position_code` and does not silently substitute the assigned role. Tests were updated with explicit values and include a deliberately different assigned-role/balance-code case.

This correction should be treated as part of the current team-strength implementation before using attack-frequency output for fidelity comparisons.
## 25 September pre-match participant bridge checkpoint

The next autonomous-match boundary has been narrowed from a broad "match-day initialization" problem to one concrete original runtime path.

Confirmed:

- normal match setup populates the MatchCalculator before `0x62AC90`; `0x62AC90` initializes already-selected participants rather than choosing the lineup;
- exact collector `0x510CD0` walks the team's ordered player-ID roster and includes only runtime players marked active/on-field or substitute-available;
- `DBRPlayer+0x14 bit 4` is the on-field starter flag and bit 5 is the match-substitute flag;
- setters enforce those states mutually exclusively;
- for AI teams, `0x5111A0 -> 0x409B50 -> 0x409C90` establishes lineup/position state before participant collection;
- the MatchCalculator therefore receives an ordered union of starters and designated substitutes from original runtime DBRPlayer state.

Primary remaining match-initialization target is now `0x409C90`: recover the exact AI starter/bench selection phases, formation role assignment and eligibility filters sufficiently to prepare a scheduled AI club without caller-supplied lineup state. Condition/Form/Team Orders runtime sources remain part of the same bridge but no longer obscure how the participant roster itself is constructed.
## 25 September autonomous AI pre-match selection checkpoint

The clean-room runtime can now execute the proven AI lineup-selection/mutation bridge rather than requiring a caller to hand-build an XI.

Implemented:

- exact low-bit base availability state on RuntimePlayer:
  - injured;
  - suspended/banned;
  - separate unresolved selection-exclusion flag;
- exact CCupTiedPlayer record semantics and cup-tied lookup as a separate competition layer;
- all 21 original numeric first-team formation templates;
- exact two-pass 0x409C90 starter selection core;
- exact Form-adjusted role scoring and roster-order tie behavior;
- exact ranked substitute categories plus overflow/no-extra-goalkeeper rule;
- first-team role/auxiliary writes and starter/substitute flag mutation;
- exact 0x510CD0-style ordered participant collection;
- refusal to commit an incomplete XI by default, leaving the original restriction-relaxation/context path explicit rather than fabricating a fallback.

reconstruction/match_preparation.py now composes RuntimePlayer-like state into an AI-selected participant list. The remaining external selection inputs are narrowed to:

1. competition/context registration checks beyond the proven cup-tied predicate;
2. the bit-11 team restriction/quota retry;
3. the original formation/substitute-quota source supplied by the team/competition runtime.

The next highest-value bridge is to resolve those team-level pre-match inputs together with tactical/order state, so a scheduled AI club can be prepared without caller-supplied formation/tactic metadata.


## 25 September exact schedule RNG/shuffle checkpoint

The reconstruction regression workflow is now operational and green:
**270 tests pass** at commit `3473737015fb6a283a5f807ba1af91f8f6494794`.
The preceding failures were stale synthetic fixtures/assertions and were
corrected without relaxing production behavior.

The simultaneous-fixture scheduler investigation has also advanced:

- `0x615950` is confirmed head insertion, so a date bucket begins in reverse
  insertion order;
- `0x615AE0` is exact descending Fisher-Yates with RNG bounds `N..2`;
- `0x615BE0` shuffles buckets in increasing bucket-index order;
- `0x66951C` is the classic MSVC 32-bit LCG / 15-bit `rand()`;
- `0x64D540(n)` is exactly `floor(rand15*n/32768)`;
- `0x64D530` is another `rand()` entry point, not a state getter;
- application startup seeds the CRT stream from the current-time routine;
- save/load deliberately serializes a `rand()` output and reseeds from it;
- schedule-generation paths can consume the same shared RNG before the final
  date-bucket shuffle.

Clean-room exact RNG and bucket-shuffle primitives now live in
`reconstruction/match_schedule.py`.

Remaining same-day-order target: recover the exact Premier League match-node
insertion/generation path and all intervening RNG consumption leading into
the final bucket shuffle. Until that is complete, fixture-ID order remains an
explicit deterministic fallback rather than a fidelity claim.


## 25 September fixed Premier League insertion-order checkpoint

The English fixed-real-fixture path is now directly recovered:

- DBTRealFixtures are attached to their DBRRound in global fixture-table order at 0x4F76A4..0x4F770D;
- DBTRounds are attached to League in global round-table order through 0x4F72D0 -> League::AddRound 0x4F4500;
- generic League initialization 0x4F5150 chooses fixed builder 0x6173D0 when real fixtures are present;
- 0x6173D0 walks rounds then each round's fixture list in those preserved source orders and consumes no RNG before schedule insertion;
- shipped Premier League round 0 therefore inserts fixture IDs 0..9, round 1 10..19, etc.;
- because 0x615950 is head insertion, each isolated ten-match PL round is reversed immediately before the later random bucket shuffle.

PremierLeagueState now preserves source order and exposes the recovered fixed insertion/pre-shuffle order without replacing the deterministic default execution order prematurely.

Next schedule-fidelity target: prove schedule-container selection for Premier League competition 0 and the exact shared-RNG state/consumers before 0x615BE0, including whether 0x4FA790 runs on the normal new-game path and whether unrelated competition nodes coexist in the same buckets.

## 25 September Premier League schedule-container checkpoint

Schedule-container selection is resolved exactly:

- DBRCompetition+0x38 comes from packed Static.dat competition dword +45;
- League selector 0x4F3B70 returns true only for values 2 or 3;
- true -> 0x947AF0; false -> 0x947AD8;
- shipped Premier League competition 0 has packed +45 = 1, so it uses 0x947AD8;
- 0x947AD8 is constructed with container mode +0x14 = 0; 0x947AF0 with +0x14 = 1;
- startup finalizes 0x947AD8 first, then 0x947AF0;
- 0x4FA790 is gated by container mode +0x14 and therefore runs only for 0x947AF0.

Result: the RNG-heavy 0x4FA790 path is no longer a blocker for reproducing the Premier League shuffle. Remaining work is to audit RNG consumption on the 0x947AD8/mode-0 finalization path and before its 0x616620 call.

## 25 September repository audit checkpoint

A fresh repository audit at parent HEAD e956925cfdc12cd96583a3cbd6bf86d70d13fa31 found the implementation and CI healthy: **279 reconstruction tests pass**.

The audit also found documentation drift and one important fidelity risk:

- reconstruction/README.md still described the project as largely a parser/browser and incorrectly listed season AI and the match engine as unimplemented;
- older FINDINGS/PROGRESS sections still describe match-day initialization as the main backend blocker even though later commits implement AI preparation;
- the 24 September project audit is now historical and materially understates match/reconstruction progress;
- RuntimePlayer new-game peak-age initialization uses Python random.Random even though the recovered original initializer uses the same bounded CRT RNG family as the later game. This means formulas are correct in isolation but the global original RNG timeline is not yet reproduced end-to-end.

A new research/PROJECT_AUDIT_2026-09-25.md records the reconciled status and risks. Immediate next work remains exact startup/global RNG sequencing into the Premier League bucket shuffle, followed by real ten-fixture/multi-round/full-season integration tests.

## 25 September shared CRT startup checkpoint

The player-startup RNG fidelity issue from the repository audit is now implemented and tested.

Recovered exact order:

- construct the full DBRPlayer array first, consuming RNG(15) once per player for initial morale;
- then load players in table order;
- per loaded player consume RNG(1), RNG(2), RNG(2) for peak ages, then RNG(5) for the unresolved +0xC0 month-span field;
- Non-EU startup classification consumes no RNG.

GameState.from_database now seeds MsvcCrtRng (explicit seed for deterministic reconstruction, current epoch seconds when omitted), preserves the table-wide two-phase draw order, and stores the live RNG on GameState. Autonomous Premier League methods can continue using this stored stream by default; test callers can still inject scripted RNGs.

CI is green after the implementation. Remaining RNG target: enumerate every other startup RNG consumer between application srand and the first 0x947AD8 / 0x615BE0 Premier League bucket shuffle, then reproduce that sequence before enabling exact default same-day fixture ordering.

## 25 September mode-0 pre-shuffle competition RNG checkpoint

The startup-to-Premier-League shuffle trace has narrowed again.

0x411020 initializes competitions matching the current schedule container before 0x615BE0. Generic procedural League initialization can consume RNG in 0x6170F0, but only for child leagues whose parent competition passes virtual +0x18. Root leagues skip the block entirely; League parents return false, Cup/DummyLeague parents return true.

Static.dat identifies the currently proven mode-0 candidates as IDs 14 (Ch. League Phase 1), 167 (Ch. League Phase 2), and 192 (WCC Group Phase), all with Cup parents. Their RNG draw counts depend on parent Cup participant vector +0x54/+0x58 at child initialization.

A nearby disassembly ambiguity was corrected before persistence: 0x616620 calls RNG-clean 0x40B380, not adjacent RNG-using 0x40B390.

Next exact target: recover how Champions League / World Club Championship Cup initialization populates +0x54/+0x58 before child League initialization, determine the reverse competition-init order used by 0x411020, and audit nested Cup initialization callees for any additional RNG consumption.

## 25 September mode-0 Cup branch correction checkpoint

The pre-Premier-League-shuffle RNG audit corrected two important provisional interpretations before they could enter implementation.

First, mode-0 Cup initialization skips the eight-entry +0x54 allocation branch. Root mode-0 Cups later create a one-entry vector when empty. Champions League ID 9 then reaches 0x40C6C0, whose selector consumes one bounded RNG draw only if its filtered candidate vector has more than one member. WCC ID 101 follows a separate branch whose Cup+0x40 state is still unresolved.

Second, the RNG-using 0x41ACA0 branch reachable from team routine 0x404110 is not taken during new-game schedule finalization: 0x616620 passes outer argument 1, which skips that path.

Immediate next targets: prove mode-0 competition registration/initialization order, trace later mutations of Cup+0x54/+0x58 before child League IDs 14/167/192 initialize, resolve WCC Cup+0x40 on the new-game path, and audit the argument-1 0x404110 / 0x50EA90 nested callees for any remaining RNG.

## 25 September exact root competition initialization-order checkpoint

The mode-0 pre-shuffle ledger now has an exact outer competition ordering.

Packed Static.dat competition +27 is the country/region index. Each country owns an array of root competitions only. Those roots are sorted by runtime +0x18 = -signed(packed +15), then 0x411020 walks the array backwards, so effective initialization is ascending packed +15. Child competitions are recursively attached in global competition ID order under their parent.

Examples: England initializes League Cup -> FA Cup -> Challenge Shield -> Charity Shield -> Premier League -> Division 1 -> Division 2 -> Division 3 -> Conference -> Conference 2 -> Conference Cup. Europe initializes Champions League -> UEFA Cup.

Remaining caveat: roots with equal +15 compare equal under qsort, so their relative order is not yet guaranteed. This currently matters most in the Other pseudo-country (116), where several roots share key 0.

Next target remains class-specific RNG: audit DummyLeague roots, ScotPremierLeague ID27, Cup mode-0 roots/children, and the argument-1 team setup helpers to produce the exact pre-0x615BE0 bounded-draw sequence.

## 25 September DummyLeague / ScotPremierLeague RNG checkpoint

The mode-0 initializer ledger eliminated another large class.

Vtable decoding proves packed kind 3 constructs DummyLeague and uses initializer
0x4F5130. That initializer plus base child dispatcher 0x4F3DE0 are RNG-clean.
The shipped primary set contains 118 DummyLeague roots and none has children,
so all 118 can be removed from the pre-0x615BE0 RNG-consumer list.

Scottish Premiership competition 27 is likewise a childless primary root.
Its special 0x4FAC60 initializer has no direct random call, and the only direct
RNG block in generic procedural League builder 0x6170F0 is skipped because the
Scottish root has no parent. Nested generic-League helpers remain under audit.

CompetitionDefinition now exposes packed +14 class code, +4 parent,
+15 initialization-order value and +27 country/region ID, allowing future
startup-ledger code to derive the competition hierarchy from Static.dat rather
than hard-coded IDs.

Next exact target: finish transitive RNG audit of root League initialization,
then reduce the remaining mode-0 RNG ledger to Cup roots and the three
Cup-parent child League phases (IDs 14, 167, 192), including WCC +0x40 state.


## 25 September WCC / Europe Cup RNG checkpoint

The mode-0 competition RNG ledger has narrowed to a much smaller set.

WCC ID 101 is now proven non-random in its root Cup team selector because
Cup+0x40 is initialized and the WCC-specific branch uses 0x40C550. The root
Cup populates its one-entry +0x54 vector before child initialization, so WCC
Group Phase ID 192 consumes zero parent-vector shuffle draws.

Champions League child phases IDs 14 and 167 also receive a one-entry parent
vector and consume zero 0x617277 shuffle draws.

The only primary root Cups using random selector 0x40C6C0 are Champions League
ID 9 and UEFA Cup ID 10. Each selector makes exactly one
RNG(candidate_count-1) call when its filtered candidate vector contains more
than one team.

Immediate target: reconstruct/count the 0x40C6C0 candidate set from shipped
team/country data, which should yield the exact remaining Europe-root bounds.


## 25 September exact Europe selector checkpoint

The Europe-root Cup RNG bound is fully recovered.

The runtime filter in 0x40C6C0 maps to Master.dat club +98 in {2,3}, club
dword +18 > 50000, and Static.dat country +16 != 0. The canonical data yields
seven candidates, ordered England, France, Germany, Holland, Italy, Scotland,
Spain.

The selector contains an original count-minus-one quirk: 0x5EE6C0 calls
RNG(count-1). Thus the seven-entry list uses RNG(6) and Spain, the final
entry, cannot be selected.

Champions League ID 9 and UEFA Cup ID 10 each build this vector independently
and therefore contribute exactly two RNG(6) draws in that order before the
primary schedule bucket shuffle.

Clean-room parser support now exposes the two neutral Master.dat fields needed
for this filter, and competition_startup.py has deterministic tests for the
filter, exclusion behavior, empty/singleton handling, and unreachable-final-
entry quirk.

Next target: finish the transitive RNG audit of generic root League
initialization and then enumerate any earlier non-player startup consumers
before 0x616620. If those paths are clean/bounded, the exact CRT state entering
0x615BE0 can be reconstructed.


## 25 September pre-schedule youth RNG checkpoint

The startup RNG ledger found a major upstream consumer before 0x4F7C00.

The user-reset path 0x413830 -> 0x413980 -> 0x61DF90 generates a randomized set of young players. It consumes an option-size draw when applicable, one candidate-selection draw per generated player, and two nested name-generation draws per selected player through 0x421C00 -> 0x421BA0.

Clean-room additions expose Master.dat player +10 as initial_flags and model the exact option target mapping, candidate filter, and swap-delete selection behavior in startup_rng.py.

Next target: recover 0x421BA0 per-country/fallback name-list bounds, then account for the separate 0x414330 -> 0x421C00 loop that can consume many startup name-generation draws before 0x61DF90.


## 25 September generated-name bound checkpoint

The two nested RNG bounds inside 0x421C00/0x421BA0 are now reproducible from
the shipped data rather than symbolic.

DBTNationalities post-process 0x411A10 constructs filtered player-pointer
vectors per nationality in table order. The four literal string exclusions
are preserved exactly. 0x421BA0 uses that vector count when >10, otherwise
falls back to the full DBTPlayers count.

The earlier 0x414330 startup block is also quantified: 1,157 shipped teams
qualify for one generated-name call (2,314 RNG draws), followed by 54 fixed
generated-name calls for the selected user's club country (108 more draws).
Thus 0x414330 contributes 2,422 bounded name draws before 0x413980 youth
generation.

Clean-room startup_rng.py now exposes/test-covers the exact name-source
filter, nationality source ordering, per-country RNG bound, team-loop filter,
and two-draw-per-team sequence.

Next target: use these helpers to construct the exact pre-schedule draw ledger
for a concrete new-game/user configuration, including the selected user's
country and 0x61DF90 youth candidate/name sequence; then continue auditing
any remaining setup callees before enabling exact default PL fixture order.


## 25 September exact !Spare youth-pool checkpoint

The fixed youth source global is resolved.

`0x8755D0` is written by `0x413890` from exact-name lookup `0x40C4E0`;
with the shipped Master.dat it is club **332, !Spare**. The similarly named
special -1 team is a clone and must not be confused with the raw source-team
index.

There are 2,048 Spare players in Master.dat, all source-eligible on the bit-3
predicate, but `0x61DF90` has only a 512-entry WORD candidate buffer.
Therefore the actual vector is the first 512 Spare players in DBRPlayer table
order, ending at player index 6643.

This makes the youth candidate draw sequence concrete:
`RNG(512), RNG(511), RNG(510), ...` for however many of the 4..8 target
players are generated.

Clean-room startup_rng.py now enforces the 512-entry cap, reproduces the exact
`!Spare` lookup, and can emit the descending candidate-selection bounds.

Next startup-RNG target: combine the now-known 512-source sequence with the
selected user's option-category-3 mode and country-specific two-name bounds,
then finish auditing any remaining pre-`0x4F7C00` callers so a complete
new-game-to-first-PL-shuffle ledger can be generated.


## 25 September DummyLeague sorter boundary checkpoint

A late RNG audit found and then correctly localized the random sorter near
0x4F4720.

The RNG routine is not League's +0x38 method. DummyLeague overrides that slot
with 0x4F4750; normal League/ScotPremierLeague use RNG-clean 0x4F4720.
DummyLeague's override consumes one RNG call per participant during its first
lazy sort.

Static.dat Round +20 is now mapped as the source competition reference used by
Cup setup. Scanning all primary Cup rounds proves none references a DummyLeague:
Champions League references League phases 14/167 and WCC references League
phase 192. The known DummyLeague sorts are confined to secondary-container
Euro/World Cup seed logic, after the primary PL shuffle.

This removes the apparent new DummyLeague draw block from the first-PL-shuffle
ledger while retaining it as a verified mechanism for later broader
competition reconstruction.

Next target: continue the pre-schedule audit for genuinely primary-path RNG
consumers and assemble a concrete total-call ledger from srand through the
first 0x947AD8/0x615BE0 bucket shuffle.


## 25 September replayable user-startup RNG checkpoint

The `0x413830` pre-schedule RNG contribution can now be replayed end to end
for a supplied human-game configuration.

New tested helpers:
- consume the entire `0x414330` generated-name sequence, including its 108
  selected-user-country draws;
- replay one user's `0x61DF90` youth sequence with the exact option draw,
  descending candidate bounds, swap-delete selected IDs, and two country-name
  draws per youth;
- resolve the youth name bound directly from parsed country/player data.

A control-flow correction is also locked down: the actual new-game
`0x413980` path calls `0x61DF90` once per user. A different routine that
calls it twice is not on this path.

Next target: finish proving the other immediate pre-`0x4F7C00` wrappers are
RNG-clean, then move farther back in startup to locate any database/team RNG
consumers that precede the already-reconstructed player initialization block.


## 25 September Scouting reseed correction checkpoint

A potentially project-changing RNG lead was resolved safely before it could
distort the new-game reconstruction.

The extra `srand` at `0x4AF7F0` belongs to **PScouting2K**. RTTI from
vtable `0x7C2E6C` names the class directly. Scouting event code 31 invokes
`0x4AE970`, which hashes Scouting UI/search state, reseeds the CRT stream,
and Fisher-Yates shuffles its candidate list.

This mechanism is real but **not part of the proven mandatory new-game path**.
Therefore the already recovered new-game RNG sequence remains relevant:
player startup, generated-name setup, per-user youth generation, primary
competition initialization, then the PL schedule-bucket shuffle.

Next target returns to the actual new-game call graph: finish the pre-
`0x4F7C00` transitive audit and then move backward from `0x4C42EE` toward
Master/Static loading to enumerate any remaining mandatory RNG consumers.


## 25 September immediate pre-schedule RNG-clean checkpoint

The mandatory new-game path immediately before schedule setup is now narrower.

Direct disassembly proves:

- `0x4C42EE -> 0x4E2EB0`: user-list cleanup only, zero RNG draws;
- `0x4C42FA -> 0x5328B0`: controller/UI synchronization only, zero RNG draws;
- `0x4C4304 -> 0x413830`: the already-recovered generated-name and per-user
  youth RNG block;
- `0x4C4379 -> 0x4F7380`: deterministic competition/country runtime graph
  construction, zero RNG draws;
- `0x4C4381 -> 0x4F7C00`: schedule/competition initialization begins.

The potentially opaque virtual calls inside `0x4F7380` were resolved far
enough to exclude hidden random consumption: class-code getters are constant
returns, round-attachment handlers only allocate/link data, and post-build
handlers only perform deterministic qsort operations.

Consequently the CRT state leaving `0x413830` reaches `0x4F7C00`
unchanged. The remaining first-Premier-League-shuffle uncertainty is now
confined to RNG consumers earlier than `0x4C42EE` plus the already-mapped
RNG-active competition/schedule paths under `0x4F7C00`.

Next target: walk backward through the same new-game function before
`0x4C42EE`, beginning with `0x532980`, `0x432A20`, `0x432D20`,
the user/controller virtual calls, `0x4311D0`, `0x5EC060`,
`0x4E9830` and `0x6596A0`, and rule each branch in or out of the mandatory
startup RNG ledger.


## 25 September TeamSelect pre-reset RNG checkpoint

The mandatory new-game RNG boundary has moved farther backward.

The entire TeamSelect prefix inside `0x4C41C0`, from function entry through
`0x4C42EE`, is now proven zero-draw:

- the current TeamSelect panel teardown is deterministic;
- `0x432A20` has no direct or transitive bounded-RNG path, and its sole
  previously-opaque control virtual is a callback-masked deterministic toggle;
- `0x432D20` resolves to deterministic control enable/disable operations;
- user `+0x5BC/+0x5F0` virtuals are concrete Bitmap/eCText state toggles;
- `0x6596A0` always returns zero, making `0x4C4284..0x4C42EC`
  unreachable.

Thus no RNG is consumed between entry to `0x4C41C0` and the already-known
`0x413830` block at `0x4C4304`.

Combined with the previous checkpoint, the path after `0x413830` through
`0x4F7C00` is also zero-draw. The remaining pre-first-PL-shuffle uncertainty
is now strictly:

1. RNG consumers before the call to `0x4C41C0` from the TeamSelect event
   handler/caller chain; and
2. the already-recovered RNG-active startup/competition work beneath
   `0x4F7C00`.

Next target: walk backward from the sole caller `0x4DA4A5` in
`PMain@TeamSelect`, then identify where that panel/new-game flow first enters
the already-reconstructed player/database startup sequence.


## 25 September TeamSelect start-button RNG boundary checkpoint

The immediate pre-`0x4C41C0` event-dispatch gap is now closed.

Confirmed:

- RTTI identifies `0x4DA480` as the `PMain@TeamSelect` virtual event
  callback at vtable slot `+0x10`;
- event/control ID `0x2A` is the branch that calls `0x4C41C0` at
  `0x4DA4A5`;
- the embedded TeamSelect control at `+0x3690` is
  `Button@ease_2001`;
- its setup stores ID `0x2A` and the TeamSelect owner;
- the generic Button input path calls TeamSelect `+0x0C` first
  (concrete `0x5CFA50`, constant true), performs deterministic UI/sound
  handling and state mutation, then dispatches TeamSelect `+0x10`;
- the Button setup chain forces its optional `+0x28` callback pointer to
  zero, removing the last opaque pre-parent state-change callback;
- no known CRT RNG entry point is called directly anywhere in the TeamSelect
  method range `0x4D7CC0..0x4DA4D0`.

Therefore the concrete click-to-new-game path consumes **zero RNG draws**
before `0x4C41C0`.

This pushes the remaining first-PL-shuffle uncertainty farther backward again:
the next target is the TeamSelect panel lifetime/activation path before the user
clicks Start/Continue. Trace panel construction/activation and its caller chain
back to the already-recovered database/player startup sequence, looking only
for mandatory CRT RNG consumers that can survive until the first schedule
shuffle.


## 26 September repository stabilization checkpoint

A repository-structure audit found that the technical implementation was healthy but the handoff documentation had accumulated conflicting "current" statements across a long chronological log.

The project now separates live truth from history:

- `ROADMAP.md` defines sequential development gates;
- `research/CURRENT_STATE.md` is the short canonical resume point;
- `research/PROGRESS.md` remains the chronological record;
- `research/BACKLOG.md` captures useful deferred work;
- `research/FIDELITY_GAPS.md` tracks observable reconstruction deviations;
- `research/HANDOFF_PROMPT.md` provides a reusable fresh-session prompt;
- `project_status.json` mirrors the current gate for tools/agents.

Stale status text was explicitly reconciled rather than deleting historical evidence. The current technical next target remains the TeamSelect panel lifetime/activation path before the Start/Continue click, tracing backward toward the already-recovered database/player startup sequence for mandatory CRT RNG consumers.


## 26 September Gate 1 completion checkpoint

Repository stabilization is complete.

Completed:

- introduced the sequential gate roadmap and one-gate working rule;
- established `research/CURRENT_STATE.md` as the short canonical live resume point;
- separated backlog, fidelity gaps, chronological progress, and verified findings;
- added a reusable cross-chat handoff prompt and machine-readable status file;
- reconciled the stale 279-test count, obsolete Python-Random startup statement, and historical match-day-initialization blocker;
- marked dated project audits as historical snapshots;
- added `.gitignore` rules for development/reverse-engineering noise and original game artifacts;
- added a CI clean-room guard that rejects forbidden original filenames/disc-image formats and byte-identical canonical originals by SHA-256;
- strengthened `reconstruction/verify.py` to verify the canonical Master.dat / Static.dat / Core.str / English.str SHA-256 values and use explicit verification failures rather than optimization-sensitive `assert` statements;
- refreshed the GitHub Actions workflow versions.

Validation at commit `16ea9615ca5d9f7f401ba53cffb819d016e64659`:

- clean-room repository guard: **passed**;
- reconstruction unit suite: **307 tests passed**.

Gate 1 is therefore complete. Gate 2 is active.

Exact Gate 2 resume target: continue from the TeamSelect panel lifetime/activation path before the Start/Continue click. Trace construction/activation and its caller chain backward to the already-recovered database/player startup sequence, recording only mandatory CRT RNG consumers that can affect the state entering the first Premier League schedule shuffle.


## 26 September Windows 11 port mission update

The project owner clarified the intended end state: this is a **Windows 11 modernization/port of FM2001**, not a strict clean-room-only replacement. The contents of the supplied source archive/disc image are authorized for use in the project, and the preferred strategy is now to preserve/reuse as much of the original game as technically practical.

Consequences:

- original music, sound effects, interface graphics, strings, data, and other useful resources should be reused directly when the modern runtime can consume them;
- where old formats are inconvenient, convert the authorized original resource rather than replacing it without need;
- the modern runtime/reconstruction remains necessary for incompatible executable/game logic and obsolete Windows/runtime behavior;
- `original_assets/` is now the controlled repository location for intentionally imported source/converted resources;
- `research/ASSET_POLICY.md` defines provenance and placement rules;
- raw disc/archive containers and temporary reverse-engineering artifacts remain excluded to avoid repository bloat and accidental dumps;
- the old strict clean-room guard has been replaced by a repository asset-policy check.

This policy change does **not** alter the active technical Gate 2 task. Startup RNG reconstruction remains the immediate blocker before schedule-order fidelity and real-data season integration.

Long-term presentation gates are updated accordingly: the target is to restore the original FM2001 experience, including original login/menu music and interface resources, on top of the modern Windows 11-compatible runtime.


## 26 September intro FMV verification checkpoint

A focused presentation audit of the authorized source disc confirmed that the original startup videos are directly reusable:

- `FMV/easp.tgq`: EA Sports logo FMV with embedded stereo EA ADPCM audio;
- `FMV/premintro.tgq`: approximately 54-second Premier League intro with embedded stereo EA ADPCM audio.

The analyzed executable explicitly calls `easp.tgq` during startup and later calls `PREMINTRO.TGQ` through FMV wrapper `0x461E20`. The Premier intro call uses flag 1 while the EA logo uses flag 0; lower routine `0x461900` uses flag bit 0 to register input callbacks, making a user-skip role for that flag probable.

Modern FFmpeg successfully decoded and converted the complete original `premintro.tgq` to H.264/AAC while preserving its picture/audio content. This establishes that the original intro plus original embedded music/audio is technically straightforward to carry into the Windows 11 port.

Detailed evidence is in `research/STARTUP_PRESENTATION.md`.

This was a side verification only. Gate 2 remains the active technical task.


## 26 September TeamSelect construction-order checkpoint

Gate 2 advanced and the first new boundary was committed immediately to avoid losing work across chat/session interruptions.

Confirmed from direct executable disassembly:

- PStartMenu event handler `0x4C3770` dispatches event/control ID 2 to branch `0x4C37C7`;
- that branch calls core loader `0x50D630` at `0x4C392F`;
- only afterward does it allocate the TeamSelect object and call `PMain@TeamSelect` constructor `0x4D9290` at `0x4C39B0`;
- `0x50D630` calls club loader `0x40B9C0`, player loader `0x4218C0`, and manager loader `0x415B70`;
- therefore the already-recovered DBTPlayers startup RNG sequence definitely occurs **before TeamSelect construction/activation**;
- direct calls inside TeamSelect constructor `0x4D9290..0x4D973F` do not include any known CRT RNG entry point, though its helper graph still requires transitive audit before calling the constructor fully RNG-clean.

This is the first concrete connection between the recovered player startup RNG sequence and the TeamSelect lifetime path.

Next target: audit the other mandatory loaders/setup calls inside `0x50D630` and the pre-`0x50D630` portion of PStartMenu ID-2 branch for any additional CRT RNG consumers before TeamSelect exists.


## 26 September core database-loader RNG checkpoint

Another Gate-2 boundary is now closed and committed.

The `0x50D630` core startup loader called before TeamSelect construction has been audited:

- DBTClubs allocation virtual resolves to `0x40BBE0`, constructing clubs through `0x405A40`; its normal load/import/post-load path contains no CRT RNG;
- the nearby club random selector `0x40BB50` is not called by the startup club loader;
- DBTManagers allocation virtual resolves to `0x414B80`, constructing records through `0x414C50`;
- manager loader `0x4147F0`'s record virtual `+0x18` resolves through vtable `0x7BDA20` to `0x415B50 -> 0x414D50`, which is deterministic serialization handling;
- manager post-copy `0x414E10` is deterministic;
- manager RNG-bearing behavior routines around `0x415435/0x415760` are not on the startup manager-load path;
- DBTPlayers post-process `0x421CE0` adds no new RNG beyond the already-reconstructed `0x421C80` startup draws;
- `0x4310C0/0x431160`, `0x413890 -> 0x40C4E0`, and `0x4F6EB0` do not introduce a mandatory CRT draw.

Result: **inside `0x50D630`, the mandatory startup RNG source is the known DBTPlayers sequence.**

Next target: close the PStartMenu ID-2 calls before `0x50D630` and then finish the TeamSelect constructor/activation helper audit.


## 26 September TeamSelect lifetime RNG closure checkpoint

The standard fresh-start TeamSelect lifetime is now closed as an RNG boundary.

Confirmed:

- PStartMenu construction writes zero to global `0x875614`, so the optional `0x4506B0` modal is skipped on the standard fresh-start ID-2 path;
- the PStartMenu pre-`0x50D630` helpers resolve to deterministic UI/resource/date/setup behavior;
- the child virtual `+0x34` loop resolves through `0x64F520 -> 0x64F3E0` and only toggles UI state;
- TeamSelect constructor `0x4D9290` and its reachable constructor helpers contain no CRT RNG path;
- TeamSelect panel registration/activation through `0x653320`, `0x5329A0`, `0x4DAF40`, `0x6542B0`, `0x653A30`, `0x5EE560`, `0x532C10` and `0x5328B0` is deterministic;
- together with the earlier TeamSelect method/click audit, the standard TeamSelect lifetime from construction through Start/Continue consumes zero CRT RNG draws.

The seed-to-shuffle investigation therefore moves one boundary earlier: determine whether anything consumes the CRT RNG between application seeding and the PStartMenu/database-loader path. If not, the startup ledger can be closed around the already-reconstructed DBTPlayers and `0x413830` draws plus competition/schedule consumers.


## 26 September Loader444 pre-player RNG checkpoint

A previously hidden mandatory startup RNG consumer has been recovered and committed.

After the application seeds CRT randomness at `0x53109E`, startup loads `FM2001_art\generic\bground.444`. Extension dispatch selects RTTI class `Loader444@EAUK`, whose decode method `0x68598A` calls `0x6864A0` and then `0x6868E0`.

Exact draw count:

- `0x6864A0` initializes a 0x103-byte random table with **259 raw CRT rand() calls** when global `0x9FB524` is zero;
- `0x9FB524` is zero-filled process data and is not initialized by the pre-srand EA Sports FMV or License.png path;
- `0x6864A0` sets the flag to 1 afterward;
- `0x6868E0` then consumes exactly **one** additional raw rand() call on either mutually-exclusive pixel-format branch.

Therefore the standard first post-seed background load advances the shared CRT stream by exactly **260 raw rand() calls before DBTPlayers startup**.

The authorized source asset was also extracted/verified:
`FM2001_Art/Generic/bground.444`, 222,616 bytes, SHA-256 `9db0d71daf70d77b4f5f2307304bb8c5eac4ee3a07a85f2828b570fbbf3b7fb9`, with 800x600 dimensions encoded in its opening uint16s.

Next: represent this 260-draw compatibility side effect in the startup RNG replay/tests, then continue auditing the short post-seed/pre-PStartMenu path for any other mandatory consumers.


## 26 September Loader444 replay implementation checkpoint

The newly recovered 260-draw presentation-side RNG cost is now represented in executable reconstruction code.

Added to `reconstruction/startup_rng.py`:

- `LOADER444_FIRST_DECODE_RAW_DRAWS = 260`;
- `consume_loader444_first_decode_rng(rng)`, which advances the shared MSVC CRT stream with exactly 260 raw `rand15()` calls before DBTPlayers startup.

The implementation deliberately models the RNG side effect rather than tying fidelity to the legacy image decoder. The Windows 11 port can decode/display the original `bground.444` through a modern path while still reproducing the original shared RNG state.

Tests cover both:

- exact call count = 260;
- exact resulting `MsvcCrtRng` internal state versus 260 manual raw CRT draws.

GitHub Actions at `c5d040f36e5ff20e13ee962b3df5ea2c854a8582` is green with **309 tests passed**. Repository asset policy also passes.

Remaining Gate-2 work: finish proving the exact ordinary post-`srand` path into the first PStartMenu/database load has no additional mandatory CRT consumer beyond Loader444, then assemble the complete startup ledger.


## 26 September initial PStartMenu path correction checkpoint

A potentially misleading startup branch was corrected and committed before continuing the RNG ledger.

Confirmed:

- global `0x8755E4` is the user count at object `0x874C10+0x9D4`, not an independent startup flag;
- `0x413BB0` adds a user and increments that count;
- `0x413D80` resets the user list/count/current index;
- `0x432190` requires an already-existing current user through `0x4139D0`, so it cannot be the zero-user initial PStartMenu route;
- generic front-end factory `0x47AEC0` maps **screen ID 0x323** to `0x47C928 -> 0x4C3280`, the PStartMenu constructor;
- TeamSelect control ID `0x29` also returns to `0x4C3280`, independently confirming the relationship.

This removes later user/calendar branches from the mandatory pre-DBTPlayers RNG audit unless a concrete first-start call path reaches them.

Next: trace the actual post-intro front-end navigation/factory activation of screen ID 0x323 and classify any RNG-bearing functions reachable before the New Game ID-2 event.


## 26 September seed-to-PStartMenu RNG closure checkpoint

The ordinary first-start path from the application seed through the first PStartMenu is now closed for the shared game CRT stream.

New key correction/confirmation:

- after `PREMINTRO.TGQ`, main startup directly allocates a 0x2E0-byte object at `0x53120F` and finishes by assigning PStartMenu vtable `0x7C64E0` at `0x53129C`;
- this is the actual zero-user initial PStartMenu construction path;
- the embedded-control `+0x30/+0x34` virtuals resolve to `0x64F510/0x64F520 -> 0x64F3E0`, deterministic control toggles;
- the normal front-end idle/event loop `0x531AF0` and its concrete event/audio helpers do not advance the game CRT stream;
- the setup functions between `0x53109E srand` and the first Loader444 decode contain no additional mapped game-CRT RNG consumer.

Result for the standard path:

```text
srand(seed)
 -> 260 raw Loader444 draws
 -> no further mandatory draw before New Game
 -> DBTPlayers startup RNG
```

Combined with the already-closed TeamSelect and post-`0x413830` paths, this leaves assembly/review of the complete seed-to-competition ledger as the final Gate-2 task.


## 26 September Gate 2 completion checkpoint

Gate 2 - Finish the startup RNG chain - is complete.

The standard seed-to-competition path is now bounded as:

```text
srand(time seed)
 -> Loader444 first bground.444 decode: 260 raw draws
 -> initial PStartMenu/front end: zero additional draws
 -> PStartMenu New Game prefix: zero
 -> DBTPlayers startup: 150,320 draws for 30,064 shipped players
 -> TeamSelect lifetime / Start dispatch: zero
 -> 0x414330 generated names: 2,422 draws
 -> 0x413980 per-user youth block(s): exact replayable order
 -> immediate competition-entry wrappers: zero
 -> 0x4F7C00 competition/schedule initialization boundary
```

The fixed prefix before per-user youth generation is **153,002 raw CRT draws**.

The complete parameterized ledger is persisted in `research/STARTUP_RNG_LEDGER.md`.

All Gate-2 completion criteria are satisfied:

- TeamSelect lifetime/activation bounded;
- mandatory pre-competition RNG consumers enumerated;
- exact competition-entry CRT state reproducible from seed plus human-game configuration;
- findings and implementation consequences committed.

Gate 3 is now active. Its first task is to compose the existing Loader444, DBTPlayers, generated-name and youth replay pieces into one executable startup ledger with fixed-seed intermediate-state tests, then extend through primary competition initialization toward the first Premier League schedule-bucket shuffle.


## 26 September Gate 3 precompetition replay checkpoint

The Gate-2 ledger is now executable as one shared-CRT replay rather than a set of independent helpers.

Implemented in `reconstruction/startup_rng.py`:

- `consume_dbtplayers_startup_rng(rng, player_count)`, preserving the two-phase DBTPlayers order;
- `StartupUserRngConfig`;
- `PrecompetitionStartupRngReplay` phase-checkpoint result;
- `replay_precompetition_startup_rng(...)`, which advances one shared RNG through Loader444 -> DBTPlayers -> `0x414330` names -> all linked-user youth blocks.

Tests now verify exact intermediate MSVC states, not only call counts.

For synthetic seed `0x12345678` with 25 players/two users:

```text
after Loader444:  0xC526B5BC
after DBTPlayers: 0x7B7B62DB
after team names: 0x0C18030B
after youth:      0x2797444C
```

The shipped-size DBTPlayers checkpoint is also locked:

```text
seed 0x12345678
 -> Loader444 state 0xC526B5BC
 -> 30,064-player DBTPlayers state 0x8FF8E56C
```

GitHub Actions at `52d5b4c2eaa9535a67a73b484e712fe0043306b5` passes **312 tests**.

Next Gate-3 task: close the residual primary-container team-setup audit, then model the already-recovered Champions League `RNG(6)` -> UEFA Cup `RNG(6)` sequence and establish the exact shared CRT state entering `0x615BE0`.


## 26 September primary competition RNG-tail closure checkpoint

The last old Gate-3 competition/team-finalization uncertainty is closed.

Direct branch tracing proves that new-game `0x404110(team, 1)` cannot take the only direct-call RNG chain found beneath `0x409C90`: it temporarily forces team category 2, so `0x403640` sends the per-player predicate to RNG-clean `0x418130` instead of `0x418050`.

A recursive direct-call audit of `0x50EA90` also reaches no mapped CRT RNG entry point.

Since `0x616620` orders competition initialization -> `0x404110` team loop -> `0x50EA90` loop -> `0x615BE0`, the exact primary-container RNG contribution after the pre-competition ledger is now:

```text
Champions League RNG(6)
UEFA Cup         RNG(6)
```

and nothing else mapped before `0x615BE0`.

Next: implement this two-draw competition tail and lock the exact fixed-seed state entering `0x615BE0`.


## 26 September Gate 3 completion checkpoint

Gate 3 - Build an executable startup RNG ledger - is complete.

Implemented and verified:

- one shared `MsvcCrtRng` replays the recovered startup path through Loader444, DBTPlayers, generated names, per-user youth generation and primary competition selection;
- the primary competition tail is exactly Champions League `RNG(6)` followed by UEFA Cup `RNG(6)`;
- argument-1 `0x404110` and `0x50EA90` add no primary pre-shuffle RNG;
- `reconstruction/startup_sequence.py` composes the full replay through the exact state entering primary `0x615BE0`;
- fixed-seed tests lock intermediate states and the final pre-shuffle state;
- startup player code requires the reconstructed bounded-RNG interface and no longer silently accepts Python `random.Random.randrange`.

Latest validation at `a382f7982614cbe1d0cf8508d7790df6d17246d9`: **314 tests passed**.

Gate 4 is now active.

The first Gate-4 issue is that `0x615BE0` shuffles every populated primary schedule bucket in bucket-index order. Therefore the exact RNG state at function entry is necessary but not sufficient for the first Premier League matchday: all earlier populated buckets and their sizes/order must be reproduced because each bucket of size N consumes bounds N..2 before later buckets are reached.

Next target: recover the primary schedule-container bucket indexing/date ordering and enumerate every populated bucket before the first Premier League fixture date, then propagate the shared CRT state to the first PL bucket.


## 26 September Gate 4 bucket-mapping checkpoint

The first Gate-4 scheduler boundary is committed.

Confirmed:

- primary `0x947AD8` contains 373 bucket heads;
- `0x6169F0` initializes its date/serial base before new-game competition scheduling;
- League `0x4F4500` stores each round's scheduled week plus zero-based weekday in the `League+0x60` schedule array;
- `0x615950` computes nominal target offset exactly as `7*week + (weekday-1)`;
- first Premier League round week/day 7/6 therefore targets offset **54**;
- `0x615950` has an original December-25 one-day adjustment;
- crucially, `0x615950` can move a match away from its nominal target using `0x615890` conflict searches, so final bucket populations require reproducing insertion/conflict behavior;
- `0x615BE0` shuffles the primary container strictly in bucket-index order 0..372.

Next: reverse the `0x615790/0x615890` conflict predicate and insertion search sufficiently to reconstruct final bucket placement, then enumerate every primary bucket before/including first PL target 54.


## 26 September Gate 4 conflict-placement checkpoint

The ordinary LeagueMatch placement search is now both reverse-engineered and implemented.

Confirmed:

- `0x615790` treats two ordinary LeagueMatch nodes as conflicting when they share either club;
- `0x615890` scans center-1, center, center+1 and returns the first conflicting bucket;
- `0x615950` searches outward in two-day jumps from the first conflict;
- it probes the side closer to the original nominal target, with the **later side winning equal-distance ties**;
- the first clear center is used, then the match is head-inserted.

Implementation/tests were committed in:
- `4f6a4b4c1b893eaef52637e306788dd785c0867e`
- `1be9a02785ab7aa85a23d783d1eee8351127d63d`

Next: use the exact country/root competition initialization order and procedural League round match counts to establish the first Premier League bucket's complete pre-shuffle population and PL slot positions, while checking whether any pre-54 fixture can be conflict-shifted into that bucket.


## 26 September first Premier League bucket structure checkpoint

Gate 4 now has the exact pre-shuffle structure of the first PL date bucket.

Canonical Static.dat + executable construction order prove:

- primary bucket 54 contains **142 ordinary LeagueMatch nodes**;
- country/runtime traversal is source order and canonical country IDs equal source indices;
- procedural leagues emit exactly N/2 matches per round;
- the Premier League's 10 fixed fixtures are inserted IDs 0..9 and therefore form the head-inserted local block 9..0;
- 96 target-54 league matches are inserted after the PL and therefore precede it in the final linked-list order;
- 36 target-54 league matches were inserted before the PL and remain behind it;
- PL fixture IDs 9..0 therefore occupy **zero-based pre-shuffle slots 96..105** in the 142-entry bucket.

The target-54 ±1 conflict window is clear for these league clubs, and adjacent target data does not add shifted ordinary League nodes into bucket 54.

Remaining first-matchday ordering task: determine the exact CRT state reaching bucket 54 after shuffling primary buckets 0..53, then run the known 142-entry Fisher-Yates and filter the ten PL nodes.


## 26 September Gate 3 correction: Cup round schedulers consume pre-shuffle RNG

**This checkpoint supersedes the earlier Gate-3 conclusion that the primary competition tail before `0x615BE0` consisted only of Champions League `RNG(6)` followed by UEFA Cup `RNG(6)`.**

While reconstructing Gate-4 bucket populations, RTTI and direct disassembly resolved the Cup round runtime classes and their scheduling virtuals:

- packed round type 1 -> `NormalRound`, scheduling virtual `0x4F64D0`;
- packed round type 2 -> `TwoLegRound`, scheduling virtual `0x4F6820`;
- packed round type 3 -> `MiniLeagueRound`, scheduling virtual `0x4F6B10`.

Cup initialization loops runtime rounds at `0x4F62B1..0x4F6321` and calls each round's virtual slot `+0x04` **before** returning to the primary `0x616620` path and before final `0x615BE0` bucket shuffling.

Both `NormalRound 0x4F64D0` and `TwoLegRound 0x4F6820` begin with an unconditional participant-array Fisher-Yates when their runtime participant count N is greater than one:

```text
RNG(N)
RNG(N-1)
...
RNG(2)
```

That is N-1 mandatory CRT draws for each active round scheduler invocation, independent of the later flag-controlled parent-vector branch.

`MiniLeagueRound 0x4F6B10` also contains a direct RNG shuffle and remains to be mapped exactly.

Therefore the synthetic checkpoint previously recorded as the exact state entering primary `0x615BE0` (including `0x5D07D526` in the current tests) is **not authoritative** until active Cup round participant counts/order and any additional flag-controlled shuffles are included.

Gate 3 is reopened. Gate-4 schedule-bucket mapping and ordinary LeagueMatch conflict-placement research remains valid and committed, but final same-day ordering must wait for the corrected pre-shuffle CRT state.

Immediate correction target:

1. map `NormalRound`, `TwoLegRound`, and `MiniLeagueRound` startup participant counts;
2. determine which runtime Cup rounds are active/scheduled during initial primary-container setup;
3. resolve the third round-scheduler flag and its additional parent-vector shuffle conditions;
4. add every resulting bounded draw to the shared startup replay;
5. replace the provisional pre-`0x615BE0` checkpoint and tests.


## 26 September corrected primary Cup RNG-state checkpoint

The reopened Gate-3 correction is now quantified and implemented.

Runtime round construction/allocation plus canonical Static.dat prove every
primary Cup round reaches its scheduler with N equal to packed `team_count`.
All three round classes start with an N-entry Fisher-Yates, contributing N-1
CRT calls.

Canonical totals:

- 27 primary Cups;
- 115 rounds;
- 80 NormalRound / 32 TwoLegRound / 3 MiniLeagueRound;
- **1,737** mandatory round-pairing calls;
- plus two Europe-root selector calls;
- **1,739 total primary-competition calls before `0x615BE0`**.

For the existing synthetic post-youth state `0x2797444C`, the corresponding
canonical competition-stage state is `0x986E4579`. The old two-draw value
`0x5D07D526` is superseded.

Implementation changes:

- `competition_startup.py` now derives primary Cup round counts from parsed
  competition/round metadata and replays the exact hidden CRT-state cost;
- `startup_sequence.py` composes that state replay instead of pretending the
  Europe selectors are adjacent;
- unit tests replace the obsolete two-draw final checkpoint;
- `verify.py` locks canonical 27/115/80-32-3/1737 invariants when run against
  the authorized shipped data.

The remaining Gate-3 task is not hidden-state counting; it is **exact bounded
draw ordering and Cup pairing output** so Gate 4 can reconstruct the actual Cup
matches sharing global date buckets with Premier League fixtures.


## 26 September ordered Cup RNG event checkpoint

The reopened Gate-3 correction has advanced from call-count fidelity to exact
bounded-call ordering.

Direct binary tracing established:

- Cup rounds append in source order through `0x4F6D60`;
- Cup `+0x08 = 0x4F6E30` qsorts the runtime round array before scheduling;
- Normal/TwoLeg round sort keys are their week/day pair;
- MiniLeague sort keys come from the first schedule pair of the referenced
  child League;
- canonical primary Cup arrays are all <=8 rounds, so the exact small-array CRT
  qsort path is reproducible;
- Spain's equal-key root Cups resolve deterministically to Spanish Cup then
  Super Cup;
- Europe selectors occur before their own Cup round loops.

The canonical competition-stage stream is now:

- 117 RNG-bearing events;
- 115 Cup round shuffle events;
- 2 Europe selectors;
- 1,739 bounded calls;
- Champions League selector event index 99;
- UEFA Cup selector event index 108;
- ordered-bound digest
  `baef6479394ffee84e7a9aec58d74f1c5418ccaeaad7f617d9ed0f77e95fd8df`;
- corrected synthetic final state `0x986E4579`.

Implementation commits:

- `2f1304385ab2c58e8790bf8c29ddc32a5103f6e9` ordered primary Cup RNG replay;
- `33310ed202038ba81c73eafbabcd9ac6309c2671` event-order tests;
- `eb0110436d517c612d030a1de1f6b2338c021d0a` startup sequence integration;
- `c35f1fcd8d7ebe4aa67e339776e22f09e2a54900` startup boundary tests;
- `1ee98449980c872de33ecdb377124701f3766149` canonical verification locks.

GitHub Actions at `1ee98449980c872de33ecdb377124701f3766149`
passes **326 tests**.

Remaining Gate-3 task: recover the 16-byte Cup participant records, their
allocation/source order and post-Fisher-Yates comparator `0x4F67D0`, then
materialize final pairings rather than only shuffled slot indices.


## 26 September ClubRef and Cup allocation bridge checkpoint

Gate 3 advanced from exact RNG slot permutations into the actual Cup participant-record layer.

Direct binary evidence now proves:

- the 16-byte round participant record is RTTI-named `ClubRef`;
- ClubRef fields are vtable, cached/direct club pointer, referenced runtime object pointer, 16-bit type tag and 16-bit selector/index;
- constructors `0x4F2CB0/CE0/D10/D40/D90` create tags 0/1/2/3/4 respectively;
- post-randomization comparator `0x4F67D0` groups type-2 references first and orders type-2 records by their referenced object's schedule pair; all non-type2 pairs compare equal;
- the 238 packed Cup allocation instructions expand to 0x20-byte `DBRCupAllocInstruction` runtime records;
- runtime +0x08 = destination competition, +0x0C = sequence/index, +0x10 = instruction type, +0x14/+0x18/+0x1C = the three remaining packed parameters;
- startup attaches instructions to their destination competitions, then qsorts each destination instruction list by sequence/index through `0x4F7A30`;
- canonical type counts are 11/2/148/11/66 for types 1..5;
- type 5 is confirmed to produce direct type-0 ClubRefs from a referenced League;
- type 4 updates an allocation accumulator rather than directly appending a ClubRef;
- Cup participant append/fill runs through `0x4F57E0 -> 0x4F5790 -> 0x4F5570`.

Implementation checkpoints:

- `4545b5bba6094c632d32eef5f24b2d5078f9f59c` parses the 238 allocation instructions into `FM2001Database`;
- `37990f407e088e88c3e4d148d6a21ea8ca02f289` locks canonical count/ID/type invariants in verification.

Next: finish instruction types 1/2/3 semantics and exact ClubRef source order, resolve the one equal-sequence instruction pair under the real CRT qsort, then materialize each primary Cup round's initial ClubRef array.


## 26 September ClubRef semantic correction checkpoint

A participant-layer audit corrected one interpretation before it could enter implementation.

`0x4F67D0` does sort type-2 ClubRefs before all other tags, but the pair read from the referenced object at `+0x20/+0x22` is **not a schedule date**. Type-2 ClubRefs point to runtime competition objects; `+0x20/+0x22` is the competition ID/context pair also consumed by `0x4F3B10`.

Further resolver tracing establishes:

- ClubRef type 1 = match-result reference: selector 0 resolves the referenced match's winner/result club; nonzero selector uses `0x513FB0` to return the opposite/losing side;
- ClubRef type 2 = competition-position reference; its selector/index addresses an eligible position in the referenced competition/ranking;
- type-4 allocation instructions advance the per-source position accumulator used when subsequent type-1 allocation instructions emit type-2 references.

This makes the domestic playoff allocation records intelligible and materially narrows the remaining allocation-type reconstruction.


## 26 September initial League membership/ranking checkpoint

The source order feeding Cup allocation from League competitions is now recoverable.

Direct executable tracing shows startup routine `0x4F7A60` walks DBRClub records in canonical Master.dat order. For each club it reads the competition assignment at runtime DBRClub+0x10, maps that from packed club dword +8, creates a direct type-0 ClubRef/LeagueClub, and appends it to that League's +0x34 array.

Thus the initial unsorted League membership is:

```text
Master.dat club source order
 -> filter by packed club +8 competition ID
```

Before type-5 Cup allocation consumes a referenced League, `0x4F4940` sorts the LeagueClub array through comparator `0x4F45E0`. At new-game startup all standings statistics are zero, so the comparator reaches its final club-string tie-breaker. That resolves DBRClub+0x0C, the runtime short/display-name string loaded from the second packed club name ID.

Canonical initial league ranking is therefore:

```text
initial League members
 -> sort by short/display-name string in CP1252 byte order
```

Canonical data has no duplicate short/display names within a starting League, so this initial ranking order is deterministic without additional qsort tie ambiguity.

Implementation commits:

- `882a8dddee82697d016786925be99a9f359b82bc` exposes packed club +8 as `Club.competition_id`;
- `a500c6d9f090ef71c7f27f46fcc4e8f881aa1732` implements initial League membership/ranking helpers.

GitHub Actions at `a500c6d9f090ef71c7f27f46fcc4e8f881aa1732` passes **328 tests**.

This directly enables exact type-5 Cup allocation from referenced League ranking arrays and supports type-2 ClubRef position references.


## 26 September direct allocation eligibility checkpoint

Two participant-source ambiguities are now resolved.

1. `0x4F5810` checks **destination Cup+0x34**, not candidate club+0x34. For Europe-root Cups, candidate helper `0x40C7A0` tests whether club+0x1B0 already resolves to another competition. Successful European direct allocation writes the destination competition ID into club+0x1B0, so later European direct allocations skip that club. Club+0x2A0 separately prevents duplicates within the same Cup.

2. Allocation type 3 does not enumerate the ordinary current League ranking at +0x34/+0x38. League/Dummy/Scot virtual +0x1C uses a separate +0x30/+0x3C historical/qualification array. Startup builds it from packed Master.dat club +32/+36 (target competition, preferred slot) with first-empty collision fallback through `0x4F7BD0`. Cup sources instead enumerate Cup+0x40/+0x44.

This prevents the reconstruction from incorrectly using alphabetized current League order for type-3 allocations.


## 26 September DummyLeague timing and allocation semantics checkpoint

A potentially serious Gate-3 RNG concern is closed.

- `0x616620 -> 0x411020` initializes root competitions through virtual +0x00 only.
- `0x616620` reaches primary `0x615BE0` at `0x6168A4` and returns.
- competition virtual +0x0C is dispatched by `0x411150`, whose only direct caller is later helper `0x616A70`.
- therefore DummyLeague `+0x0C -> 0x4F7FE0 -> RNG-bearing 0x4F4750` runs after the primary bucket shuffle.
- the corrected 1,739-call pre-`0x615BE0` ledger remains valid.

Canonical allocation behavior is narrowed further:

- all 11 type-1 instructions reference ordinary Leagues and emit sequential type-2 competition-position ClubRefs using the per-source accumulator;
- type-4 allocation instructions advance that accumulator and emit no ClubRef;
- the two type-2 instructions are Champions-League-to-UEFA transfers: knockout-loser refs on the non-MiniLeague branch and type-3 group-position refs on the MiniLeague branch;
- type-3 repeatedly selects the first eligible unique club from the source competition enumeration and emits direct type-0 ClubRefs;
- type-4 ClubRef construction is confined to Scottish Premier League procedural scheduling, not Cup allocation.

CI repair commit `05ce4173b91af2573b52227b7a97272e8adba64e` restores **333 tests passing**.


## 26 September DummyLeague allocation RNG correction checkpoint

Gate 3 caught another hidden pre-shuffle RNG consumer before Gate 4 resumed.

The older DummyLeague exclusion audit checked Cup round source references but
missed type-5 Cup allocation instructions. Type-5 calls `0x4F4940` on its
source competition; when that source is a DummyLeague, first access invokes
RNG-bearing `0x4F4750`.

Canonical primary startup first-sorts 11 unique DummyLeague sources through
type-5 allocation:

`89, 93, 25, 104, 168, 162, 148, 139, 102, 131, 120`.

They contain 124 teams in total, adding 124 bounded CRT calls.

Corrected primary competition total:

- 1,737 Cup round Fisher-Yates calls;
- 124 DummyLeague ranking calls;
- 2 Europe selectors;
- **1,863 total calls**.

Corrected synthetic checkpoint:

`0x2797444C -> 0xAECA9FA5`.

Corrected ordered-bound SHA-256:

`a6675e77b8256fcb8d5834efa6a9d006182078c12f27887c8228a14eca889711`.

The allocation-aware ordered replay now emits 128 high-level events, with
DummyLeague sorts at indices 20,47,60,98..105 and Europe selectors at 110/119.
For the synthetic checkpoint both Europe selectors resolve to club 1137.

Implementation/verification checkpoints:
- `90bd76c2...` state-only DummyLeague accounting;
- `efb1b8e6...` ordered DummyLeague events;
- `006ad710...` canonical 1,863-call verifier;
- `1622a7ff...` composed startup replay propagation;
- `218e7800...` DummyLeague score/bound tests.

Latest CI at `218e780064343838a3546fe497fe31606eb05b70`: **341 tests passed**.


## 26 September type-5 quantity and Cup-capacity checkpoint

The type-5 allocation loop is now exact.

Direct disassembly of `0x4F5F97..0x4F5FDC` proves that its source ranking
index advances on every candidate but its instruction progress counter advances
only when `0x4F5840` succeeds. Type-5 `quantity` therefore counts accepted
clubs, matching the implemented scan-until-N-successes helper.

A canonical count audit across all 27 primary Cups shows:

- 24 Cups request exactly their total `new_entrants` capacity;
- League Cup requests 94 for 92 slots;
- Champions League requests 77 for 76 slots;
- World Club Championship requests 10 for 8 slots.

Those three excess requests are intentional and are handled by the proven
silent-overflow behavior once all Cup round entrant quotas are full.


## 26 September conditional Cup-shuffle checkpoint

The extra shuffle visible inside NormalRound/TwoLegRound does not require
another Gate-3 RNG correction.

- NormalRound/TwoLegRound virtual +0x08 returns false; MiniLeague returns true.
- Cup dispatch can therefore enable the auxiliary-shuffle flag after a
  MiniLeague -> knockout transition.
- The auxiliary shuffle operates on Cup+0x54, **not** the participant ClubRef
  array.
- New-game initialization sets Cup+0x58 (that vector's count) to exactly 1.
- Both auxiliary loops call CRT RNG only when the copied count is >1.

Result: the conditional branch consumes zero startup draws and the canonical
pre-`0x615BE0` ledger remains **1,863 calls / state 0xAECA9FA5**.

## 26 September all-primary-Cup orchestration checkpoint

Gate 3 now has an end-to-end orchestration layer rather than only per-Cup
materialization primitives.

Committed implementation:

- `reconstruction/cup_runtime.py` traverses competitions in recovered primary
  initialization order on one shared bounded CRT stream;
- lazy DummyLeague type-5 ranking is consumed at first access;
- deterministic League rankings and historical enumeration arrays feed the
  recovered allocation semantics;
- previously materialized Cup state is used to inject allocation type-2 UEFA
  transfer ClubRefs at the later destination Cup;
- Europe-root selectors and all round Fisher-Yates/qsort/pairing work share
  the same traced RNG;
- every scheduled round still hard-fails unless its participant count reaches
  the packed canonical `team_count`;
- stable participant and pairing/group SHA-256 digests are produced by the
  orchestration layer;
- unresolved Cup-source type-3 enumeration is not guessed: callers must supply
  the exact Cup+0x40/+0x44 values if that path is encountered.

Cross-Cup synthetic regression coverage proves that a source Cup can
materialize knockout winners, feed loser references into a later Cup through
allocation type 2, and continue scheduling on the same ordered RNG stream.

Validation at `8b52d20a3e363430c33257b1954763a377aa0b06`:

- reconstruction unit suite: **358 tests passed**;
- repository asset-policy workflow: **passed**.

The authorized canonical Master.dat / Static.dat / STR files were searched for
in the current ChatGPT file library and connected Dropbox but were not
available there. Therefore no new participant/pairing digest is being labeled
canonical without an actual shipped-data run.

Next target: recover exact Cup match/schedule-node creation and primary
schedule-container insertion semantics for NormalRound, TwoLegRound, and
MiniLeagueRound, then wire those nodes into the all-Cup driver. Once canonical
game data is available to the execution environment, run the driver end to end
and lock the resulting shipped-data digests before closing Gate 3.

## 26 September canonical source recovery and Cup schedule-node checkpoint

The authorized original disc image was recovered from the retained ChatGPT
Library reference and materialized for direct executable/data analysis. The
disc payload was extracted transiently only; no original binary or database
payload is being added to the repository.

Canonical extracted hashes match the already locked release:

- `FOOTBAL.EXE`: `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`;
- `Master.dat`: `183dd457d09ce616f99a664636727668ec15eab3f65b9057ef0953e76548b6b8`;
- `Static.dat`: `e0ff7c10a5f5f973a87cf6cd2d3770e623071899a0b30378debd0e7d13edb9d8`;
- `English.str`: `aa594a55ad95c672b69184e5f3ff8349e41fe95b48c5dcb3c8fcfe2bcdf5b601`;
- `Core.str`: `b0800475769fa087e69de989388569e5b29f495e5abe5d62687c2acb1d339e06`.

Direct disassembly now resolves the Cup node layer substantially:

- NormalRound scheduler `0x4F64D0` creates one 0x5C-byte `CupMatch`
  through `0x510520` for every materialized pairing and inserts it through
  `0x615950` using the round's primary week/day pair at runtime
  `+0x20/+0x24`;
- TwoLegRound scheduler `0x4F6820` creates a `FirstLegMatch` through
  `0x510640`, inserts it at `+0x20/+0x24`, then creates a
  `SecondLegMatch` through `0x510680` and inserts it at
  `+0x28/+0x2C`; the propagated winner ClubRef references the second-leg
  match object;
- MiniLeagueRound `0x4F6B10` does not call `0x615950` directly. It
  distributes the shuffled/sorted participants into child League objects,
  whose normal procedural League initialization later creates the group-stage
  LeagueMatch nodes;
- the generic schedule-conflict virtuals shared by Cup/League match classes
  are `0x510A80` / `0x510A40`. They test both participant ClubRefs via
  `0x4F2830`;
- `0x4F2830` treats resolved/direct ClubRefs as conflicting only when they
  resolve to the same club pointer. If both refs are unresolved/symbolic, it
  requires an exact match of ClubRef type at `+0x0C`, referenced runtime
  object pointer at `+0x08`, and selector at `+0x0E`. A direct-vs-symbolic
  pair does not conflict.

This means schedule placement can be reproduced without prematurely resolving
future Cup winners: symbolic references conflict only when they identify the
same unresolved source object/type/selector.

Next target: finish `0x6170F0` procedural League fixture emission for the
MiniLeague child competitions, including exact round/date and insertion order.
Then implement the schedule-node descriptors and generic ClubRef conflict
placement, run the all-Cup materializer against the recovered canonical data,
and lock the resulting digests.

## 26 September procedural-League RNG correction checkpoint

**This checkpoint supersedes the claim that the complete primary
pre-`0x615BE0` competition-stage stream is 1,863 bounded calls ending at
`0xAECA9FA5`.**

Direct disassembly of the canonical `FOOTBAL.EXE` resolves an earlier-missed
RNG path inside the ordinary procedural League builder:

```text
League::Initialize 0x4F5150
 -> procedural builder 0x6170F0
 -> round-robin solver 0x616F20
 -> 0x616EA0
 -> randomized/backtracking selector 0x616CE0
 -> 0x64D540(bound)
```

The call at `0x61721C` is reached before `0x6170F0` emits its LeagueMatch
nodes and before primary `0x615BE0`. It is separate from the already-known
conditional parent-vector shuffle at `0x617277`.

Canonical Static/Master data has **22 primary root procedural Leagues** in
addition to the fixed-fixture Premier League. Their club counts imply
**3,591 unique pairings** in one round-robin cycle. Because `0x616CE0`
performs at least one bounded RNG call for each chosen pairing, these roots
alone prove at least **3,591 additional pre-shuffle bounded calls**, before
backtracking retries and before child procedural League instances such as
Champions League group phases.

A direct high-level translation of the solver has been sanity-checked on
synthetic even-sized leagues: it produces every unordered club pair exactly
once. It also shows the original backtracking can add extra draws. For
example, one tested 20-team state consumed 213 calls for 190 pair selections.

Consequences:

- the existing 1,737 Cup-shuffle + 124 DummyLeague + 2 Europe-selector =
  1,863 stream remains valid as a **mapped subset**, not the final primary
  pre-shuffle ledger;
- `0xAECA9FA5` remains only the state after that older subset and must not be
  presented as the final state entering `0x615BE0`;
- Gate 3 remains open and moves temporarily back to RNG-ledger correction;
- Gate-4 bucket/date/conflict primitives remain useful, but any final bucket
  shuffle state/order derived from the old checkpoint is paused pending the
  corrected procedural-League stream.

Next: finish an exact tested translation of `0x616CE0..0x616F20`, identify
every primary procedural League runtime instance and initialization position,
integrate its bounds into the shared startup stream, and then resume the Cup
schedule-node materializer on the corrected RNG state.


## 26 September complete primary competition RNG replay checkpoint

The procedural-League correction is now fully integrated rather than only
bounded as a lower-limit warning.

Canonical complete competition replay before primary `0x615BE0`:

- 39 procedural League runtime instances;
- 4,302 procedural-League bounded calls;
- 1,737 Cup participant-shuffle calls;
- 124 DummyLeague lazy-ranking calls;
- 2 Europe-root selector calls;
- 6,165 bounded calls total;
- 167 high-level RNG events;
- ordered-bound SHA-256
  `3e7accfdf108a48a53902bb32a782fb23c64c7e5ce54eff101e0f869f6c3629c`;
- synthetic post-youth state `0x2797444C -> 0x0DD3ACA3`;
- Europe selector event indices 137 / 158, selecting clubs 1137 / 1159
  under the synthetic checkpoint.

Filtering procedural-League events reproduces the earlier 1,863-call subset,
including digest
`a6675e77b8256fcb8d5834efa6a9d006182078c12f27887c8228a14eca889711`
and intermediate state `0xAECA9FA5`, proving that the correction is additive
rather than a rewrite of the earlier Cup/DummyLeague ordering.

Implementation is integrated through
`reconstruction/procedural_league.py`,
`reconstruction/competition_runtime.py`,
`reconstruction/startup_sequence.py`, and `reconstruction/verify.py`.

Validation at `fba3babd72859d4c932c1aadffc81f6b54e339a0`:

- reconstruction GitHub Actions: **365 tests passed**;
- repository asset-policy GitHub Actions: **passed**.

The live resume point was reconciled after that implementation. Gate 3 now
continues at procedural League schedule-node emission in `0x6170F0`, the
conditional child-parent vector shuffle, and exact Cup/League node insertion.


## 26 September automatic continuation infrastructure

Added a local recovery layer for long-running ChatGPT reverse-engineering work so
a timeout, silent connection loss, or conversation-length limit does not require
manual reconstruction of the previous chat.

The recovery architecture now uses:

- `main` as canonical technical state;
- a separate `agent-runtime` branch for ephemeral worker status;
- `research/AUTO_CONTINUE_STATE.json` as the runtime lease/state record;
- a Windows PowerShell watchdog that checks the public GitHub branch activity
  every three minutes and treats a continuously-working session as stale after
  the configured 15-minute lease;
- a Chrome Manifest V3 extension that detects explicit ChatGPT interruption /
  conversation-length UI signals and can submit the canonical handoff into a
  new chat;
- a special watchdog recovery URL so the Windows detector can launch Chrome and
  hand the new tab to the extension without requiring native-messaging access;
- cooldown and per-hour recovery limits to prevent restart loops.

Silent inactivity has one authority: the Windows watchdog. The extension handles
explicit ChatGPT UI failures and prompt submission, avoiding duplicate stale
timers that could create two recovery chats.

The runtime is intentionally left at `mode=continuous`,
`status=waiting_for_user` until the local components are installed and tested.

## 2026-09-26 - Procedural League schedule-node emission recovered

- Recovered generic procedural League node emission directly from canonical `FOOTBAL.EXE`:
  - `0x616F40` computes `ceil(scheduled_matchday_count / (team_count - 1))`;
  - `0x6170F0` reuses the randomized one-cycle pairing matrix;
  - exact insertion traversal is pairing round -> pair -> cycle;
  - participant direction swaps after each cycle, producing alternating home/away;
  - `0x616FC0` date index is `(team_count - 1) * cycle_index + round_index` and inserts a `LeagueMatch` through `0x615950`.
- Canonical data validation shows complete-cycle counts for every generic primary procedural League, including CL child groups (4 teams / 6 matchdays) and WCC groups (4 / 3).
- Isolated the Scottish exception: competition 27 (12 teams / 38 matchdays) intercepts the fourth generic cycle via `0x6170A0`; `0x4FAC60` creates the final five-matchday post-split schedule separately.
- Added implementation checkpoint `f24bda9` and regression-test checkpoint `0997c8d`.
- No GitHub Actions workflow run was attached to `0997c8d` when checked, so the previously verified full-suite baseline remains `fba3babd` with 365 tests passed.
- Next: finish the Scottish final-split node description, then add Cup/League schedule-node descriptors and integrate them into the complete primary competition materializer.


## 26 September auto-recovery schedule-node integration checkpoint

Recovered from the repository after the previous worker became unavailable. The live
handoff was stale: the Scottish post-split trace, parent-vector zero-draw invariant,
Cup/League schedule descriptors, and symbolic ClubRef conflict identity were already
persisted on main, so none of that investigation was repeated.

New integration work in this recovery:

- `d090408f` / `2528fe8f`: attached exact Cup schedule nodes and a deterministic
  Cup-schedule digest to the all-Cup runtime materializer.
- `2c0002a1` / `498e9d35`: added an interleaving primary materializer that uses
  the verified complete competition RNG replay as an event plan while consuming the
  real CRT stream exactly once. Procedural League solvers are injected at their
  recovered initialization positions and their pair matrices are retained for
  schedule-node construction.
- The first CI run exposed one genuine descriptor bug: normal Cup rounds were
  unnecessarily reading TwoLeg replay-date fields. `69fb14aa` fixes that path.
- `54e9f352` / `8b0b41c6` / `f7e67a07`: added explicit zero-RNG fixed-League
  traversal markers and exact `0x6173D0` fixed real-fixture node materialization,
  preserving round-table then per-round fixture-table order.
- `c1d06bba` / `2bcce1db`: locked synthetic fixed-League and integrated ordering
  regressions.

Validation at `2bcce1db718f0b7e8d35d93c90df65b0ca98a0da`:

- reconstruction GitHub Actions: **383 tests passed**;
- repository asset-policy workflow: **passed**.

The integrated materializer now sequences fixed real-fixture League nodes, generic
procedural League nodes, competition-27 Scottish post-split nodes, and Cup
Normal/TwoLeg nodes against the complete primary competition event plan while
preserving the already-verified RNG ledger.

The remaining canonical materialization risk is participant identity for the
League-parent playoff children 97, 157, and 169 if their current direct membership
does not supply the packed team count. The materializer deliberately raises rather
than inventing symbolic refs. After that source is resolved, run the complete
materializer against the authorized shipped data and lock participant, pairing, and
schedule-node digests before closing Gate 3.


## 27 September canonical integrated materializer run - Cup-source enumerator blocker

The authorized canonical shipped data was executed against the integrated Gate-3
materializer from synthetic post-youth CRT state `0x2797444C`.

Input parse was canonical and complete:

- 1,246 clubs;
- 30,064 players;
- 1,612 managers;
- 209 countries;
- 193 competitions;
- 1,053 rounds;
- 238 Cup-allocation instructions;
- 380 real fixtures.

The run advanced beyond the previously unresolved League-parent playoff children
97/157/169 using the recovered `0x4F4FD0` type-2 source-position ClubRefs.
It then stopped at the next deliberately unimplemented exact source:

```text
ValueError: type-3 source Cup 98 requires its exact Cup+0x40/+0x44 enumeration
```

This is not being approximated. The exact next task is to recover the Cup-source
enumeration semantics for Cup 98 (and audit whether any other type-3 Cup sources
exist), implement them, then rerun the canonical materializer. No participant,
pairing, or schedule digest is labeled canonical until this path is resolved.

## 27 September canonical Cup allocation / RNG correction

The canonical integrated run exposed two reconstruction assumptions that were stricter than the executable:

1. Allocation type 5 (`0x4F5F97`) stops normally when its source ranking is exhausted, even if fewer than the requested number of clubs were accepted. Canonical League Cup demonstrates this directly: after two earlier type-3 qualifiers and the first Premier League type-5 instruction, the later `quantity=15` Premier League instruction can admit only 13 remaining clubs.
2. Allocation type 3 (`0x4F60DD -> 0x4F58C0`) likewise performs exactly `quantity` source scans, but an exhausted scan inserts nothing and does not fail the instruction.

Both silent-underfill behaviors are now implemented and regression-tested.

A larger RNG-ledger correction follows from direct scheduler disassembly. NormalRound `0x4F64D0` and TwoLegRound `0x4F6820` load their Fisher-Yates count from runtime round `+0x0C` (the actual ClubRef count) before calling `0x64D540`. They do not shuffle the packed Static.dat team-capacity field directly.

The canonical UEFA Cup materialization proves the distinction matters: allocation currently produces 80 refs for round 210 against packed capacity 82 before further exact eligibility semantics are resolved. Therefore the prior Gate-3 complete replay's Cup draw total of 1,737 and grand total of 6,165, which were derived from packed round team counts, must be treated as **superseded/provisional**, not final canonical values, until an actual-count integrated replay is completed.

Next: replace the static-count Cup event plan with an adaptive one-pass competition replay that injects procedural-League RNG at the recovered competition traversal points while learning each Cup round's real descending shuffle bounds from the materialized participant vector.


## 27 September Gate 3 completion - actual-count canonical startup ledger

Gate 3 is complete after canonical shipped-data execution corrected the final
Cup RNG assumption and locked the full participant/pairing/schedule-node state.

The decisive correction was that Cup round schedulers `0x4F64D0` /
`0x4F6820` shuffle runtime round `+0x0C` actual participant count after
allocation/propagation. Packed Static.dat `team_count` is only capacity.
Canonical allocation preserves source-exhaustion underfill, so the old
packed-capacity 1,737 Cup-call / 6,165 total checkpoint was nine draws too high.

Canonical competition replay from synthetic post-youth state `0x2797444C`:

- 39 procedural League runtime instances / **4,302 calls**;
- 115 Cup round shuffles / **1,728 calls**;
- 11 DummyLeague lazy-ranking events / **124 calls**;
- 2 Europe selectors / **2 calls**;
- **6,156 bounded calls total**;
- **167 RNG-bearing events** plus one zero-draw fixed-League traversal marker;
- ordered-bound SHA-256
  `1ed67d7402f1fb749d963f8978a242a6833a1f4410434b61165c906b943a710d`;
- state entering primary `0x615BE0` = **`0x0E556598`**;
- Europe selectors = clubs **1137 / 1159**.

Canonical materialization digests:

- Cup participants:
  `f9282d4c236e14f9ccb56a8ecf90dc42095278e94471624f7248eb005e3daa4e`;
- Cup pairings/groups:
  `e2f34fe736db27a011c274d8be0b0df26ed7547062c80a8b34b7d56620c63e45`;
- Cup schedule nodes:
  `30b06c3e420ebb5bbead56a14b00340a532d12dcc5bdffba715e4f84eca5ca89`;
- complete primary schedule nodes:
  `0a22c9f0c1fa20de770a7d679583b6b4e4bdbd9363a5bda07194bfe8919cc35a`.

Canonical output contains **1,226 Cup nodes** and **9,346 complete primary
schedule nodes** before bucket placement/shuffle. Three allocation refs are
dropped after destination capacity; 24 Champions-League-to-UEFA type-2 refs
are injected.

The UEFA Cup exposes the original underfill/odd-count behavior directly.
Runtime participant counts for rounds 210..217 are:

`80, 95, 47, 31, 15, 7, 3, 1`

The scheduler pairs floor(count/2) and does not synthesize a bye for the final
unpaired ref.

The composed `startup_sequence.py` now feeds the precompetition replay
directly into `materialize_primary_rng_driven_schedule()` on the same CRT
object, so the single-stream Gate-3 criterion is executable rather than merely
documented.

Validation before transition:

- reconstruction CI at `b4264affbdbbf1e69d18a9293c2e46833ca4b76e`:
  **392 tests passed**;
- repository asset-policy workflow: **passed**.

`ROADMAP.md` now marks Gate 3 complete and Gate 4 in progress. Gate 4 resumes
from `0x0E556598` by placing the complete 9,346-node set into the recovered
373-bucket primary schedule and re-auditing first-matchday ordering.


## 27 September Gate 4 completion - exact Premier League schedule order

Gate 4 is complete.

The complete 9,346-node Gate-3 primary schedule was placed through a clean-room
implementation of the canonical primary ScheduleContainer path and then
shuffled from corrected state `0x0E556598`.

Recovered/implemented path:

```text
0x615670 -> 0x615700   373 primary buckets
0x615950              date mapping, conflict search, head insertion
0x615890 -> 0x615790  adjacent conflict predicate
0x615BE0 -> 0x615AE0  ascending-bucket Fisher-Yates
0x615C10              head-to-tail linked-list execution traversal
```

Canonical placement/shuffle audit:

- 9,346 nodes placed;
- 168 non-empty buckets;
- maximum bucket size 147;
- 38 nodes displaced from nominal buckets by conflict placement;
- 373-bucket count-vector SHA-256
  `fce6003d6a415813c08d3b55152ae6bf3da3fb9f68eef3bf4c0666e1df67718b`;
- 9,178 primary bucket-shuffle RNG calls;
- final primary shuffle state `0x839953AA`.

Bucket 54 is still exactly 142 nodes with no moved-in/moved-out entries.
Premier League fixture IDs occupy pre-shuffle slots 96..105 as 9..0. The
corrected first-matchday execution order is:

`8, 3, 2, 4, 6, 9, 5, 0, 1, 7`

The first ten real Premier League matchday orders are now independent
regressions in `test_primary_schedule.py`.

Validation at `c44e72ddae2e7976e8a1685f1662d659dc4a5e4c`:

- reconstruction CI: **399 tests passed**;
- asset-policy workflow: **passed**.

Detailed evidence is in `research/GATE4_SCHEDULE_ORDER.md`. Gate 5 now
integrates that recovered scheduler order into canonical real-data matchday
execution and proves a full 10-match round end-to-end.


## 27 September Gate 5 completion - canonical real matchday integration

Gate 5 is complete.

`GameState` now accepts the recovered per-round Premier League scheduler order
and uses it by default for due fixtures. The exact committed
`canonical_matchday_audit.py` independently verifies shipped hashes,
reconstructs the 9,346-node schedule, places/shuffles it, extracts all 38 PL
orders, and then runs the autonomous AI match path.

Canonical three-round audit SHA-256:

`dbe2aa4e5de50884b52616af3312e46f805d43b992c8cbb972d4446479535f4b`

The audit completed 30 matches across 19, 23, and 26 August 2000. All 20 clubs
participated exactly once per round. After round 3:

- 30 stored results;
- table played total 60;
- global goals 87-for / 87-against;
- 30 persisted match environments;
- 644 unique PL runtime players;
- Condition 34..99;
- 5 injuries with valid return dates;
- 3 active suspensions with valid counters/effective dates;
- yellow total 44;
- every club retained 11 active + 5 substitute-available players.

Validation at `6c87d6a1fae5b6e9ea2fac4fd1dccc4685ea01c5`:
**402 reconstruction tests passed** and the asset-policy workflow passed.

Gate 6 now extends the same canonical path to 38 rounds / 380 fixtures and
multiple deterministic seeds.


## 27 September Gate 6 first full-season pass

The exact committed Gate-5 audit runner was extended to its existing
`--rounds 38` mode and executed against the canonical shipped files with
`player_seed=1`.

The autonomous Premier League season completed all **38 rounds / 380 fixtures**
without an exception.

Initial full-season checkpoint:

- final matchday: **20 May 2001**;
- days advanced from 18 August 2000: **275**;
- stored results: **380**;
- league-table played total: **760**;
- global goals for / against: **960 / 960**;
- persisted match environments: **380**;
- PL runtime players: **644**;
- final Condition range: **60..99**;
- injured players at season end: **9**;
- suspended players at season end: **4**;
- accumulated yellow total: **576**;
- final autonomous match RNG state: **0x2C36A2D4**;
- preliminary audit SHA-256:
  `585118700ee56966476083f585cdc0442170cb506f2aa9031e554a73282c2605`.

Round 38 scheduler order was:

`378, 377, 371, 372, 379, 375, 374, 376, 370, 373`

This is a successful first Gate-6 season pass, but Gate 6 is not closed yet.
Next, strengthen the reusable audit with explicit 19-home/19-away checks,
per-round lineup validity, and longitudinal injury/suspension progression;
then repeat full seasons under multiple deterministic seeds.


## 27 September Gate 7 backend human-manager loop checkpoint

Gate 7 began by auditing the existing prototype and runtime rather than adding a
parallel match engine. The useful existing pieces were already present:
GameState owns live rosters, tactics, scheduler-aware calendar progression,
autonomous AI preparation, the shared match calculator, incident persistence,
Form/Condition synchronization, pitch wear, and league-table/results state.
The Tkinter app remained only a database browser.

Implemented:

- GameState.simulate_premier_league_human_fixture(): one human-controlled side
  plus one autonomous AI side, sharing the established environment, calculator,
  result, injury/discipline, Form/Condition, pitch-wear and table paths.
- reconstruction/human_gameplay.py with persistent human club, formation,
  XI/bench, Team Orders and tactics workflow.
- scheduler-aware advance-to-next-user-fixture behavior: AI fixtures earlier on
  the same date execute before the human match; later same-day fixtures execute
  after it; daily maintenance remains after the complete matchday.
- canonical shipped-data constructor hook reusing Gate-4 scheduler reconstruction
  and FOOTBAL.EXE coefficient matrices.
- exact validation for 11 starters, PL substitute quota, unique squad membership,
  current availability and Non-EU limit before a human match.

Regression coverage uses a 20-club / 10-match synthetic Premier League shape,
including a human fixture deliberately placed in the middle of the scheduler
list so both pre-user and post-user AI execution are exercised. A three-week
human-controlled loop completes through the same backend.

Validation at `22e81eacf91e56062aad101560eb94da2a8af301`:

- reconstruction GitHub Actions: **406 tests passed**;
- repository asset-policy workflow: **passed**.

Next: connect this verified controller to the existing Tkinter prototype as a
minimal temporary playable surface, then exercise the canonical shipped-data
path and audit Gate-7 completion criteria.


## 27 September Gate 7 completion - canonical human-manager gameplay

Gate 7 is complete.

The existing backend was reused rather than forked. A human-controlled side now
feeds the same reconstructed MatchCalculator, environment, result/table,
Condition, injury/discipline, Form and Pitch Wear persistence paths as AI
teams. `HumanGameplayController` persists club, formation, XI/bench, tactics
and Team Orders while preserving recovered same-day scheduler order around the
pending human fixture.

The temporary Tkinter prototype now has a Play tab for club selection, legal
11+5 lineup selection/autofill, formation, tactics, advance, match simulation,
result and live table. This is a minimum Gate-7 surface, not the later
original-style UI.

Synthetic regression uses a full 20-club / 10-match-per-round shape and
deliberately places the user fixture in the middle of the same-day scheduler
order. GitHub Actions at `92a003f6fb6e08eb810de8eb964c73260329cb69`:
**407 tests passed**; asset policy passed.

Canonical shipped-data audit then controlled Arsenal (club 0) for six real
Premier League fixtures from 19 August through 23 September 2000. Six complete
matchdays produced 60 results. Arsenal finished the audit segment 4-1-1 on 13
points; Condition remained 28..80 and legal autofill continued with two players
injured at the final checkpoint.

Canonical Gate-7 audit SHA-256:
`6baeb94d17acbdeddcda253f66a6a5e62fb9c427a7ab42e7e7ff0f457721ebee`.

Evidence: `research/GATE7_HUMAN_GAMEPLAY.md`.

Gate 8 now begins with an internal, versioned save/load format. Original FM2001
save compatibility remains explicitly separate.


## 27 September Gate 8 completion - internal save/load

Gate 8 is complete.

The modern port now has an explicit versioned internal save format
(`fm2001-modern-internal-save`, schema 2). Saves are deterministic JSON
logically and gzip-compressed `.fm2k` files by default. Immutable source-backed
database definitions are verified by a structural SHA-256 rather than copied
blindly into each save, while mutable/startup-randomized runtime state is
persisted.

The save contains calendar/scheduler state, runtime players and development
baselines, Condition/Form, injuries/suspensions, selection/tactics, Premier
League results, Pitch Wear, both relevant CRT RNG streams, human manager state,
and pending same-day match state. It supports saving after earlier AI fixtures
have already run but before the human fixture.

Schema-2 canonical mid-matchday checkpoint:
- raw deterministic JSON: 6,535,498 bytes;
- gzip save: 998,022 bytes;
- source signature:
  `6ba4b9c3bce385f084053d7b0ef13595652e3335ac7ea04991637281785668cc`;
- raw save SHA-256:
  `0eac6a1c5ddd248c76f153b2a274d334240fd0ec72cdc494331cb543e37838f6`.

A fresh canonical database/runtime restored the save before Arsenal fixture 20
on 26 August 2000 and stayed exactly equal to the uninterrupted branch through
23 September / 60 PL results / final match RNG `0xBE52A1F6`.

Canonical Gate-8 audit SHA-256:
`69a91dbce914be2fe5babdf8a8c71ad77bad5653c9cac09468520330f7c7b413`.

The playable Tkinter Play tab now exposes Save Game and Load Game and restores
club, XI/bench, formation, tactics, table, date and a pending fixture.

GitHub reconstruction Actions at `72c21e8f07bf9bf57f6dc3cbaba83809cdd06414`:
**413 tests passed**; asset policy passed.

Evidence: `research/GATE8_INTERNAL_SAVE.md`.

Gate 9 now begins: Transfers and contracts.


## 27 September Gate-9 dependency correction - starting wage RNG

While beginning contract implementation, direct tracing of the starting weekly
wage exposed one omitted mandatory CRT draw per DBRPlayer:
`0x418B90 -> 0x423A50` randomizes DBRPlayer `+0xC4` weekly wage from
`DBTAccessSkillFinancialValues`.

The startup replay/runtime now consumes this draw at the exact original point.
All affected Gate-3 through Gate-8 canonical regressions were re-run.

Key corrected checkpoints:
- DBTPlayers: 180,384 calls;
- synthetic post-youth state: `0x4B68DE28`;
- primary competition: 5,836 calls;
- state entering primary shuffle: `0x4F5CF274`;
- state after 9,178 bucket-shuffle calls: `0xD25DFFE6`;
- Gate-5 audit: `3c48d74ef2428dbc421f1ff39fa6952a095499f19dfdc312642884844c0c0a61`;
- Gate-7 audit: `4e324f5b231e62893849c904bde5a4c5cb5cb9ee3be4f54d119e5d850c8be33e`;
- Gate-8 audit: `25d5a461cf0c7eb4e05ad718d81a81815407deb15c25784eff514842e28d0b03`.

All three Gate-6 380-fixture seasons and Gate-8 branch-equivalence still pass.
GitHub Actions at `76ab612b5e9e678a2703f24d0efdc72212146928`:
**413 tests passed** and asset policy passed.

Full evidence: `research/STARTUP_WAGE_RNG_CORRECTION.md`.

Gate 9 resumes by materializing the financial-value table so the authentic wage
amount, not just its RNG consumption, enters RuntimePlayer contract state.


## 27 September Gate 9 contract initialization checkpoint

The previously neutral startup wage RNG call is now fully materialized.

Recovered and implemented:

- Static.dat `DBTAccessSkillFinancialValues`: offset `0x14965`, 100 records,
  packed size 26 bytes;
- best preferred-role rating 0..99 directly selects the wage row;
- row runtime `+0x10/+0x14` = weekly-wage base/random range;
- `0x423A50`: `base + RNG(range)`;
- `0x423990`: country financial multiplier from `DBRCountry+0x30`, then
  * 0.01 with truncation;
- `0x6596A0` optional x4 branch is hard-disabled in the canonical executable;
- initial contract span remains exact 12/24/36/48/60 months from `RNG(5)`;
- `0x418F10..0x418F68` advances the current date month-by-month into
  `DBRPlayer+0x154` contract expiry.

RuntimePlayer now stores authentic starting `weekly_wage` and
`contract_expiry_date`. GameState supplies the player's club-country
multiplier while preserving the corrected shared CRT ordering.

The Gate-8 internal save format has advanced to schema **3** so both contract
fields survive save/reload. Schema-2 historical Gate-8 evidence remains valid
for that checkpoint; current saves use schema 3.

Canonical seed-1 port-date smoke result (18 Aug 2000):
- 30,064 players;
- wage range 75..35,972;
- no zero wages;
- expiry range 18 Aug 2001..18 Aug 2005.

GitHub Actions at `1c1b62fa96788e780d0327f4e71521303dac735f`:
**418 tests passed**; asset policy passed.

Next Gate-9 task: persistent transfer proposal/deal/bid-log/movement state and
the first human bid -> decision -> negotiation -> completion workflow.


## 27 September Gate 9 persistent transfer-state checkpoint

The first live transfer runtime layer is now implemented and saveable.

`reconstruction/transfer_state.py` models the recovered structures without
inventing club/AI decision policy:

- full 0x50-byte proposal fields that are semantically known;
- negotiated contract terms: wage, signing-on fee, promotion bonus, contract
  length in months, appearance fee, three clauses, house and car;
- CDealInProgress state families 0/1/2 and swap variants 3/4/5;
- exact 0x4F0460 exchange-player predicate;
- keyed CPlayerBidLog behavior, including repeated-bid value/date update;
- CPlayerMovement history with free-transfer sentinel 1 and Bosman sentinel 2.

`GameState` now owns `TransferRuntimeState`. Internal save schema 3 persists
proposals, deals, keyed bid-log entries and movement history. Missing transfer
state in an earlier schema-3 snapshot restores as an empty runtime state.

Regression coverage verifies cash-only and swap initial states, +3 swap-family
transitions, rejected/ready state normalization, repeated bid updates,
movement sentinels, and exact transfer-state save/reload equality.

GitHub Actions at `8f7936d9badd1744e851c2027f9ac1818a7bd7de`:
**424 tests passed**; asset policy passed.

Next: trace the selling-club offer-decision routine/reason codes from the
executable. Do not guess the Poor Offer / Key Player / Can't Spare / Hot
Prospect / rival thresholds.


## 27 September Gate 9 - selling-club bid decision recovered

Canonical executable tracing resolved the ordinary seller-chairman decision at
`0x4EF940`.

Exact order:

- target under 30 with fewer than 11 higher-rated squadmates:
  reject as **Too Cheap** when total proposal value is strictly below 60% of
  `0x4205A0` player value;
- otherwise/after passing price, reject as **Too Small Squad** when
  `0x405080` returns fewer than 17 eligible/countable players;
- otherwise route to **Offer Accepted / Approach Player**.

RTTI directly names all three paths:
`EAMTPChairmanBlockTooCheap*`,
`EAMTPChairmanBlockTooSmallSquad*`, and
`EAMTransferOfferAcceptedMsub` / `EAMTPUserApproachPlayersub`.

The pure evidence-backed decision is implemented in
`reconstruction/transfer_decision.py` with boundary tests. The adapter for
`0x4205A0` valuation and the full four-bit `0x405080` eligibility count
remain separate so no unresolved semantics are guessed.


## 27 September Gate 9 - live seller inputs completed

The two remaining live inputs to the recovered seller-chairman decision are now
mapped and implemented.

`0x405080` is exact: seller squad count excludes transfer-listed
(`DBRPlayer+0x14 bit 8`), injured (bit 0), loaned-out (bit 6), and suspended
(bit 1) players. Bit 6 was proven through `MPMLoanPlayer -> 0x41A9D0`, and
bit 8 through `EAMAcceptTransferRequestsub -> 0x41B530 -> 0x420A10`.

RuntimePlayer now persists `transfer_listed` and `loan_club_id`; internal
save schema is **4**.

The `0x4205A0/0x4205F0` transfer-value formula is also reconstructed,
including AccessSkillFinancialValues base value, position/age/division
multipliers, club-country EU factor, and the post-five-appearance recent-rating
modifier. Static.dat competition byte +31 is now parsed as the valuation
division category and GameState carries the immutable source tables required by
the live valuation adapter.

Next: verify the proposal-total helper for cash-only bids, then connect
`TransferProposal.submit` -> live seller inputs -> seller decision -> accepted
player-negotiation state.


## 27 September Gate 9 live cash-bid workflow checkpoint

Canonical disassembly completed the seller-value expression used by
`0x4EF940`.

For ordinary cash-only proposals, setup calls `0x4EFE80(0,0)`. In
`0x4EFA20`:

- `0x6596A0` contributes zero;
- `0x4F0E00` contributes zero when all exchange slots are -1;
- `0x4EFE10` selector 0 contributes zero;
- proposal `+0x10` contributes the cash fee.

Thus the exact seller comparison for the default cash-only path uses the cash
fee itself.

Implemented `reconstruction/transfer_workflow.py`:

- exact cash-only proposal total helper;
- live target/seller/buyer validation;
- live `0x4205A0` player valuation;
- live `0x4212F0` protected-player inputs;
- live `0x405080` eligible selling-squad count;
- proposal/deal/bid-log creation **before** seller response, matching original
  lifecycle;
- returned seller decision (accepted / too cheap / squad too small).

Accepted bids remain pending; player negotiation and completion are intentionally
not invented in this checkpoint.


## 27 September Gate 9 player counter-offer checkpoint

The canonical executable now proves the normal player counter-offer transform.

`0x4EDB10` stores the submitted wage/signing fee in proposal anchors +0x38
and +0x3C. Fresh expectations come from player helpers `0x420180` and
`0x4202A0`; repeated negotiations use the midpoint of previous/current
offers, with wage floored to current player wage. Constant `0x7BDCC0` is
exactly 1.1, so a money field is raised only if desired > 110% of the submitted
amount.

`0x4EE180` then consumes exactly one RNG(3) and writes a 24/36/48-month
contract duration.

Implemented `transfer_negotiation.adjust_player_counter_offer()` and focused
boundary tests. GitHub Actions at `516788df7308e51a369aeb0d1e9886b933d4ae8b`:
**456 tests passed**; asset policy passed.

RTTI also resolves player-response codes:
- code 1 -> `EAMTransferUserPlayerCounterOfferMsub`;
- code 2 -> `EAMTransferPlayerAcceptsMsub`.

Crucially, normal cash code-2 acceptance is not the same as immediate
CDealInProgress ready-state promotion. The sole 0x50E760 promotion path runs
through `0x422920` and is reached here for swap/exchange-family handling.
The ordinary conclude/medical path still needs to be traced before marking
accepted cash deals ready.


## 27 September Gate 9 - ordinary cash conclusion handoff

Canonical disassembly resolves the normal post-accept lifecycle further.

- Player response code 2 -> 0x4EE490 Player Accepts.
- 0x4EEB80 applies the buyer cash gate and reaches 0x4EF170.
- User-controlled buyers receive Confirm Conclude Transfer Deal; AI/non-user
  buyers use Transfer Deal Concluded automatically.
- Both paths converge on 0x4EF600(proposal, 0).
- 0x4EF600 schedules MPMTransferPlayer through constructor 0x61B270 for the
  next day, preserving the proposal and setting the player's signed-elsewhere
  bit.
- Ordinary cash transfers therefore do not require a synthetic deal-state
  0->1 promotion before scheduling. The previously recovered 0x422920/0x50E760
  promotion belongs to swap/try-execute paths.
- MPMTransferPlayer::Execute 0x61B4A0 ultimately calls 0x4229B0 when its
  buyer-side constraints permit completion; a blocked mode-0 object may be
  rescheduled +7 days as mode 1.
- The 0x48-byte 0x4EF600 event at vtable 0x7D1218 is RTTI-proven
  EAMWorkPermitGranted, not a medical event.


## 27 September Gate 9 - ordinary cash transfer completion core

The modern runtime now reproduces the evidence-backed ordinary
MPMTransferPlayer completion slice without inventing Gate-10 finance state.

Implemented and verified:

- persistent ScheduledTransfer mirrors MPMTransferPlayer mode 0/1;
- normal conclusion schedules mode 0 for current date +1;
- buyer roster count >= 40 reschedules mode 0 to +7 days as mode 1;
- controlled-buyer execution requires an explicit current-cash affordability
  callback until the Balance subsystem is materialized in Gate 10;
- successful completion records CPlayerMovement-equivalent history, safely
  removes/adds the player between club rosters, stamps the new-club join date,
  clears signed/transfer-listed/loan state, and removes proposal/deal state;
- negotiated weekly wage, current-date-plus-months expiry, promotion bonus,
  appearance fee, three clauses, house, and car persist on RuntimePlayer;
- internal save schema **7** persists those contract fields and scheduled
  transfer objects;
- due transfer / save-reload regressions cover successful movement, exact
  movement consideration, no duplicate roster membership, and the 40-player
  +7-day retry.

GitHub Actions at `de175a605755da951a36fab3699831083f52de94`:
**477 tests passed**; asset-policy workflow passed.

The remaining Gate-9 implementation criterion is AI transfer activity during
calendar progression, followed by canonical integration/audit.


## 27 September Gate 9 - recurring AI transfer hook recovered

Canonical FOOTBAL.EXE tracing identified the recurring autonomous acquisition
entry point needed for the final Gate-9 criterion.

Every club reaches `0x40DD70` during club/calendar maintenance. When
`(current_date_integer + 5) % 7 == 0`, it calls `0x40DC90`. That routine
keeps the input as the buying club, chooses another club, asks `0x40DBB0` for
a target from the selling roster, then calls `0x41EFB0(target,buyer)`.

`0x40DBB0` includes club-status/minimum-roster checks, random roster
sampling, player eligibility, and a >26-week current-club-tenure requirement.
`0x41EFB0` is confirmed as an autonomous acquisition/signing routine that
ultimately reaches the existing player movement family.

This is sufficient to avoid inventing an arbitrary daily AI-transfer bot.
Before implementation, finish mapping the `0x41EFB0` fee/contract constants
and the remaining `0x40DC90` eligibility predicates; then wire the proven
weekly path into GameState calendar maintenance and regression-test actual AI
movement.


## 27 September Gate 9 - weekly AI acquisition core resolved

Recovered the canonical disc archive from the ChatGPT Library, converted the
raw MODE1/2352 image locally, extracted only the temporary executable, and
reverified canonical `FOOTBAL.EXE` SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
No original binary/data was added to Git.

Fresh direct disassembly closes most of the previously open weekly AI
acquisition mechanics:

- the `(current_date_integer + 5) % 7 == 0` phase maps to Saturday in the
  2000/01 calendar;
- buyer gate uses `BigClubFanBase` at `0x822408` and
  `BigClubBuyChance` at `0x82240C`; their built-in executable defaults are
  21 and 50 respectively;
- the three parser-exposed related-club IDs are exactly the fields consumed by
  `0x4079A0`; each matching direction requires an independent RNG(100) <= 10
  to permit the seller candidate;
- `0x40DB90` proves the seller retained-roster threshold is
  `AccessFanBase.field_48 - 4`;
- weekly target selection requires >26 completed weeks at the current club,
  while `0x41EFB0` independently guards at >=12 weeks;
- `0x41EFB0` ordinary valuation pricing is:
  - below 500,000: 0.98 * value + RNG(trunc(0.30 * value));
  - 500,000 or above: 1.10 * value + RNG(trunc(0.20 * value));
- movement consideration 1 and 2 remain the already-mapped free/Bosman
  sentinels;
- autonomous wage generation reuses the recovered skill-financial-value wage
  machinery;
- autonomous contract length comes from the embedded age/category table in
  `0x423340` and is applied as months through `0x4192B0`;
- successful direct acquisition reaches the existing CPlayerMovement and
  `0x422B80 -> 0x422F40/0x422F70` club-switch path.

Detailed instruction evidence is in `research/EXECUTABLE_ANALYSIS.md`.
Next: finish the remaining buyer/seller/candidate predicate semantics needed by
the clean-room data model, then implement the Saturday calendar path and run
canonical Gate-9 integration.


## 2026-09-27 - Gate 9 recovery: remaining weekly AI predicates

Recovery resumed from main `4f174fcf90ad27b2e75ba5448601844039b35eb7`
without reopening already-persisted transfer findings. The canonical
`FOOTBAL.EXE` was re-materialized from the authorized disc archive and its
SHA-256 reverified as
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

Instruction-level follow-up resolved the remaining implementable weekly AI
acquisition predicates:

- `0x403E10` validates an assigned club manager;
- `0x403E70` rejects the FREE TRANSFER pseudo-club, club category 2/3,
  `!`-prefixed names, closed country/window state, excessive buy counters
  for rosters above 28, and managerless clubs;
- `0x4F33B0` is exactly
  `roster_count < club_byte_1e8 - 2`;
- `0x40C7D0` discounts mismatched/current-club and status-bit-9 players
  before applying `AccessFanBase.field_48 - 4`;
- `0x4088E0` now has exact lineup-group coverage-equivalence and minimum
  tables, plus the explicit `player+0x64 > -1` exclusion check;
- the autonomous `0x423340` contract-duration table is completely decoded
  and its truncated integer is confirmed to be applied as calendar months.

The business meaning of player `+0x64`, club `+0x1E8`, and the source-file
seed for country runtime `+0x54` remain deliberately unnamed rather than
guessed. Their exact consumer behavior is sufficient to expose clean-room
runtime inputs and proceed with implementation.

Next: wire these predicates into a Saturday calendar AI-acquisition pass,
exercise it deterministically, then run the full Gate-9 transfer suite and
audit the final criterion.

## 27 September 2026 - Gate 9 complete: transfers and contracts

Gate 9 closed after the remaining transfer work was integrated into the live
human/controller and calendar paths.

Final implementation added:

- evidence-backed Saturday AI acquisition maintenance through
  `0x40DD70 -> 0x40DC90 -> 0x40DBB0 -> 0x41EFB0`;
- exact recovered buyer/seller/candidate gates where mapped;
- direct AI acquisition pricing, wage and contract application;
- schema-8 persistence for AI-transfer runtime inputs and neutral predicate
  state;
- `HumanGameplayController.submit_cash_bid` and
  `offer_player_contract`;
- automatic +1-day scheduling after code-2 player acceptance;
- due MPMTransferPlayer execution during normal GameState day maintenance;
- an explicit controlled-buyer affordability callback retained as the Gate-10
  finance dependency instead of inventing cash state early;
- safe roster movement and contract application through the existing transfer
  completion core.

The final human regression starts with a controlled Premier League club,
submits a cash bid for another club's player, negotiates accepted terms,
advances the calendar one day, and verifies that the scheduled transfer moves
the player exactly once into the buyer squad with the negotiated contract.

Final Gate-9 code checkpoint:

`c8b6d4e71fa9464e4d7f002c69213aad2f5ff196`

GitHub Actions: **486 tests passed**; repository asset-policy workflow passed.

Formal evidence is in
`research/GATE9_TRANSFERS_AND_CONTRACTS.md`.

Remaining transfer approximations were not hidden. The live fidelity tracker
now explicitly retains the broader `0x422803/0x423340` player-response
branches, due-transfer same-day ordering, later country-window toggling, the
autonomous contract-category source and buy-counter lifecycle.

## 27 September 2026 - Gate 10 begins: current cash first

Gate 10 starts from already recovered finance evidence rather than a fresh
search.

The immediate implementation target is the Balance/current-cash object:

- DBRUser owns Balance pointers at `+0x670..+0x684`;
- active Balance current cash is qword `+0x10`;
- controlled transfer affordability is club
  `0x404AE0` against that value;
- buyer transfer posting is `0x404B30 -> 0x5DC650` debit;
- seller transfer posting is `0x404BB0 -> 0x5DC510` credit;
- transfer accounting category is 1000;
- chairman transfer budget is a separate value and must not be conflated with
  current cash.

Next implementation block: materialize live cash, connect Gate-9 transfer
completion to debit/credit and insufficient-funds behavior, persist it in the
next internal save schema, then resume the separate authoritative
transfer-budget-store trace.



## 27 September 2026 - Gate 10 current-cash runtime integrated

The first Gate-10 finance slice is implemented and verified.

- Added `reconstruction/finance_state.py` with a clean-room
  `BalanceRuntimeState` representing the proven Balance `+0x10` current-cash
  qword and signed accounting postings.
- Transfer accounting category **1000** is now used for completed transfer
  buyer/seller postings.
- Removed the temporary Gate-9 affordability callback from GameState and
  HumanGameplayController calendar paths.
- A controlled buyer now checks live Balance cash. Insufficient cash leaves the
  scheduled transfer pending and does not mutate rosters or finance state.
- Successful completion debits a materialized buyer Balance and credits a
  materialized seller Balance by the identical transfer amount before the
  player switch.
- Internal save schema advanced to **9** and persists current cash plus the
  Balance ledger posting amount/category/date.
- Starting cash is **not** guessed. The original constructor-input source for
  Balance `0x5DC400` remains unresolved, so a controlled club's cash must be
  initialized explicitly until that source is recovered.

Verified checkpoint:

`80bc03134ec21a890ef87727a9272ed1e40ee3f6`

GitHub Actions: **492 tests passed**; repository asset-policy workflow passed.

Next: resume the existing chairman quarterly overspending/rebudget trace to
locate the authoritative live transfer/building budget reserve before modeling
the other operating budgets.


## 27 September 2026 - Gate 10 chairman-budget trace checkpoint

Canonical disc re-materialized; extracted `FOOTBAL.EXE` again matches SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

Two additional false storage/producer routes are now closed:

- full disc inventory contains no separate chairman/board budget-rule script or
  budget data file outside already-known localization, match-data and
  presentation resources;
- DBRUser `+0x5EC` is an array of four 0x1C scouting/list-state records,
  selected through `0x42B8A0 -> 0x42BCE0/0x42BD10` and heavily consumed by
  the `PScouting2K` family around `0x4ADxxx..0x4AFxxx`.

Next: classify the remaining large serialized/raw DBRUser region beginning at
`+0x700/+0x704/+0x708/+0x70C` and continue looking for finance/monthly
arithmetic feeding the chairman reserve.


## 27 September 2026 - Gate 10 PFormation2k block resolved

The 0x9CC-byte raw DBRUser save region at `+0x70C..+0x10D7` is now
instruction- and RTTI-classified.

`PFormation2k` (vtable `0x7C1AB4`) accesses this exact DBRUser region.
It checks magic `0x074A3216`, then uses five 0x1F4-byte records beginning at
`+0x714`. The records contain formation/team-sheet names plus current-club
player IDs and assigned-role data. Five records plus the 8-byte header equal the
serialized 0x9CC bytes exactly.

This removes the last large opaque block immediately before +0x10D8 from the
chairman-budget search. Next: audit remaining DBRUser scalars and finance/board
arithmetic rather than serialized container owners.


## 27 September 2026 - Gate 10 support-staff controller resolved

`DBRUser +0x5DC` is now removed from the chairman-budget search.

The `0x4D0B10..0x4D1290` family uses the object at +0x5DC as a support-staff
selector/controller while walking the DBRUser's actual staff lists. The
functions select virtual staff-type IDs in order; `0x4D0C90` is exact type 4,
the Business Consultant lookup used by the financial-objective path.
`0x4D13D0` dispatches staff types 1..16 to the corresponding lookups.

The methods do not read monetary/budget fields from the +0x5DC object.
Together with the prior support-staff/scouting classifications, this closes the
`+0x5B8..+0x5EC` neighborhood as a live chairman-budget candidate.


## 27 September 2026 - Gate 10 weekly player payroll integrated

The first recurring player-cost path is now implemented from the recovered
calendar and Balance evidence.

Instruction-level recovery established:

- weekly payroll phase:
  `0x4A8070 -> 0x40BAD0 -> 0x403C70 -> 0x404390`;
- cadence: `(date + 5) % 7 == 0`, mapped to **Saturday**;
- player amount: stored `DBRPlayer +0xC4` weekly wage;
- loaned-in players are excluded by exact helper `0x41FA50`;
- normal fresh-game DBRUser `+0xCC` starts clear, so the special
  human-only injured-wage suppression branch is inactive by default;
- accounting category **101** is posted through Balance debit `0x5DC650`;
- category 101 is a broader player-cost category and also receives
  appearance-fee postings;
- first-of-month support-staff cost path `0x4CA0F0` is separately recovered
  as category **102**, with each staff cost scaled by `1000 / 12`.

Modern implementation now:

- exposes recovered finance categories 101 and 102;
- runs weekly payroll for materialized Balance clubs;
- sums registered players' weekly wages while excluding loaned-in roster
  entries;
- preserves parent-club wage responsibility for registered players;
- leaves cash and ledger unchanged when Balance refuses an unaffordable debit;
- runs payroll on ordinary day advancement, autonomous fixture-day advancement,
  and human matchday completion;
- deliberately leaves concrete category-102 staff amounts unimplemented until
  the original CSupportStaff cost state is materialized.

The existing Saturday human transfer regression now proves the current
reconstructed same-day ordering explicitly: the due transfer posts category
1000 first, then the newly registered player's 2,000 wage posts category 101.

Verified code checkpoint:

`5dc29a072d6e4f91744b882251df16f980c82f55`

GitHub Actions:

- reconstruction suite: **497 tests passed**;
- repository asset-policy workflow: **passed**.

Next Gate-10 target: recover the next ordinary live cash-flow producer,
prioritizing match-day income / attendance receipts and other recurring
income before returning to support-staff amounts that require a broader staff
runtime dependency.


## 28 September 2026 - Gate 10 recurring-income recovery boundary

Automatic recovery resumed from main `c67c7db6ccb2e16e461d53855be413ec73260599`
without reopening the completed Balance, chairman-budget reachability, or
payroll work. The runtime lease was refreshed on `agent-runtime` at recovery
generation 24.

The verified implementation baseline remains:

`5dc29a072d6e4f91744b882251df16f980c82f55`

GitHub Actions at that code checkpoint passed **497 reconstruction tests** and
the repository asset-policy workflow.

The next ordinary cash-flow investigation was bounded from the existing
instruction evidence:

- concessions are a confirmed live cash producer through
  `0x42A9FD -> 0x5E5640 -> 0x5E56F0 -> 0x5DC510`;
- the exact concession accounting category, amount-field semantics and full
  offer-state transition remain unresolved and are therefore not guessed;
- match-day/gate income depends on the original stadium-section state at
  `DBRUser +0x694` and stadium model at `+0x6B0`;
- the modern runtime already exposes club stadium identifiers and
  `DBTAccessFanBase`, but does not materialize the original 26-section
  stadium/capacity state, so unmapped fan-base fields are not relabeled as
  attendance inputs;
- `EAMbcmonthlyincome` confirms the reporting labels GATE, MERCH, CONC,
  ADVERTS, SPONSOR, TELLY and TRANSFERFEES, but is not treated as a live
  producer;
- original Balance credit `0x5DC510` also constructs a category-1600 debit
  equal to 0.2% of incoming money. Its semantic label and exact
  conversion/rounding remain unresolved, so the clean-room credit primitive is
  not changed speculatively.

A focused durable handoff now exists at
`research/GATE10_LIVE_CASH_FLOW_TRACE.md`. The exact next executable trace is
the stadium/business family `0x429904`, `0x429BB4`, `0x42A111`,
`0x42A5D2`, `0x42C1F2` toward Balance credit, with `0x5E56F0` as the
parallel shortest route to an implementable concession posting.

No runtime behavior changed in this checkpoint. The correct current behavior is
to leave gate/concession income unimplemented until the exact producer inputs,
category and money conversion are recovered.


## Gate 10 concession payout correction checkpoint — 28 September 2026

Recovery generation 25 rematerialized the authorized source disc from the
ChatGPT Library, converted the raw MODE1/2352 image locally, extracted the root
`FOOTBAL.EXE`, and reverified its canonical SHA-256:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

The concession trace is now instruction-level exact:

- `0x5E56F0` returns each 0x168-byte active record's qword at `+0x160`;
- `0x5E5640` pays only on decoded day-of-month **1**;
- each payment uses accounting category **300 (0x12C)**;
- each payment is credited through Balance `0x5DC510`.

This also corrected the previous classification of concessions as an ordinary
fresh-game recurring producer. New concession state starts with active count 0.
The periodic generator `0x5E5330` builds a full candidate record only on the
stack, writes the candidate financial offer to `+0x158` and expiry/date to
`+0x164`, but never appends it to the persistent +0x690 object or increments
the active count. The `0x5E5710` active-record date pass likewise performs no
activation mutation. A complete direct DBRUser +0x690 reference scan found no
ordinary activation writer.

The correct implementation consequence is to keep normal concession income
disabled. Category-300 payout remains a faithful dormant/legacy path for
nonzero persisted records, not evidence that a new game should manufacture
concession revenue.

Exact next target: return fully to the match-day/gate receipt producer through
the DBRUser +0x694/+0x6B0 stadium/ticketing state and the bounded
`0x429904`, `0x429BB4`, `0x42A111`, `0x42A5D2`, `0x42C1F2`
family toward Balance credit `0x5DC510`.


## Gate 10 match-day gate producer checkpoint — 28 September 2026

A complete Balance-credit scan recovered the live gate-receipt producer outside
the earlier monthly/history trace:

`0x513252 -> 0x5DA2F0 -> 0x5DC510`.

Verified instruction behavior:

- DBRUser `+0x694 +0x08/+0x0C` supply two ticket-price inputs;
- category **1** credits
  `price_08 * count_A0 + price_0C * count_A1`;
- category **2** credits the same two prices against a second count pair;
- duplicate branches can make the same two postings for another controlled club;
- Balance high-level category **0** explicitly aggregates categories
  **1 + 2 + 3**;
- category **3** is independently produced by the season-ticket/ticket-sale
  path at `0x5D0FF4/0x5D1684`;
- therefore categories 1 and 2 are live match-day ticket components in the
  category-0 gate/ticket family;
- the producer directly consumes DBRUser `+0x694` 26-section ticket state and
  DBRUser `+0x6B0` stadium state through `0x618E00` and the
  `0x65Dxxx` stadium helpers.

The producer is now identified, but normal gate income remains unimplemented:
the four attendance/count values, exact subcategory semantics, two ticket-price
classes, special both-clubs flag and final conversion details still need to be
instruction-locked. The clean-room runtime also does not yet materialize the
required original stadium/section state.

No runtime behavior changed in this checkpoint.

Exact next target: finish translating `0x5DA2F0`, especially
`0x5DA5CF..0x5DA705` and the attendance/count pipeline feeding
`0x5DB3CB..`, then materialize only the required stadium source state and add
deterministic finance regressions.


## Gate 10 cup/ticket-state refinement checkpoint — 28 September 2026

Recovery generation 26 resumed from main
`adfdc14d732081def1565240cbc9dbe72345519d` and continued the already
recovered `0x513252 -> 0x5DA2F0` gate-receipt producer.

New instruction-locked results:

- the special both-controlled-clubs flag is set at `0x5DA705` inside the
  explicit cup/knockout attendance branch;
- that branch consumes `ATTCupFianlBoost`, `ATTCupSemiFinalBoost`,
  `ATTCupQuarterFinalBoot`, and `ATTCupDiv` at
  `0x821088/0x82108C/0x821090/0x821094`;
- this proves cup/knockout applicability but does not yet prove a narrower
  revenue-sharing or neutral-ground policy label;
- DBRUser `+0x694 +0x00` is season-ticket quantity and `+0x04` is
  season-ticket price;
- category 3 is exactly season-ticket quantity multiplied by season-ticket
  price before Balance credit;
- helper `0x618820` marks section state 2 as the season-ticket-reserved
  allocation;
- section states 0 and 1 remain the two ordinary match-day classes feeding
  `+0x08/+0x0C` ticket pricing.

The English string table contains explicit home-supporter, visiting-supporter,
season-ticket, terrace and seating labels, but no category or section mapping
was inferred from string order alone.

Exact next target: tie category 1/2 to home/visiting supporters and state
0/1 plus `+0x08/+0x0C` to terrace/seating, while continuing the four-count
attendance pipeline and exact rounding trace.


## Gate 10 home/visiting receipt split checkpoint — 28 September 2026

The live gate producer is narrowed further without introducing a guessed
attendance model.

Instruction-locked results:

- category **2** is home-supporter ordinary match-day ticket revenue;
- category **1** is visiting-supporter ordinary match-day ticket revenue;
- category **3** remains season-ticket revenue;
- the category-2 supporter count is the only match-day group to which the
  controlled host's season-ticket quantity is added before attendance output;
- match output `+0xD84` = total attendance, `+0xD8C` = home attendance
  including season tickets, and `+0xD90` = visiting attendance;
- section state **1** is rebuilt/enforced as the visiting allocation with exact
  minimum `10 * floor(stadium_capacity / 100)`;
- section state **0** is the remaining ordinary home allocation;
- state **2** remains season-ticket reserved and `-1` unavailable;
- match-day price `+0x08` is paired with stadium-entry capacity field
  `+0x1C`; price `+0x0C` is paired with field `+0x28`.

The terrace-versus-seating identity of entry fields `+0x1C/+0x28` remains
open and is not guessed from UI order.

Exact next target: resolve that final terrace/seating field mapping, then finish
the two parallel attendance-demand calculations and exact caps/conversion/
rounding before materializing stadium state and writing deterministic finance
regressions.


## Gate 10 terrace/seating mapping resolved — 28 September 2026

Recovery generation 27 rematerialized the authorized FM2001 source archive only
in the temporary working container and reverified the canonical executable
SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
No original binary or extracted game data was added to Git.

The last unresolved ticket-class label in the live gate-receipt path is now
instruction-locked. PTickets recommendation helper `0x461340` applies an extra
`0.75` multiplier relative to the otherwise parallel `0x4615B0` path. The
screen compares ticket field `+0x08` against the discounted result and
`+0x0C` against the undiscounted result. This proves:

- `+0x08` = terrace ticket price;
- `+0x0C` = seating ticket price;
- by the previously proven helper pairing, stadium entry `+0x1C` = terrace
  capacity and `+0x28` = seating capacity.

The section-state dimension remains independently resolved as state 0 home,
state 1 visiting, state 2 season-ticket reserved and -1 unavailable.

No runtime behavior changed in this checkpoint. Exact next target: finish the
two parallel attendance-demand, cap, conversion and randomized-rounding
pipelines inside `0x5DA2F0` before materializing the minimum stadium state and
adding deterministic finance regressions.


## Gate 10 attendance demand/RNG body resolved — 28 September 2026

Recovery generation 27 continued inside the already-mapped gate producer
`0x513252 -> 0x5DA2F0` and closed the four repeated ordinary-attendance
calculations without changing runtime behavior.

Instruction-level results now persisted in the focused Gate-10 trace:

- four separate cells are computed: home/visiting × terrace/seating;
- `0x40CBC0` supplies the seating reference price and an exact 0.75 terrace
  reference price;
- `0x5DA250` supplies the original piecewise ticket-price demand response;
- demand combines AccessFanBase scalar, an indexed 0.9..0.5 factor, the
  side-specific upstream modifier, price response and, for controlled clubs,
  the recovered Hotel/Club House/Parking attendance multiplier;
- ordinary demand is capped to fan base outside the cup-special path and always
  capped to the allocated class capacity;
- `0x668350` is truncation toward zero, not conventional rounding;
- `0x64D540(n)` is exact MSVC-15-bit randomized subtraction
  `floor(rand15*n/32768)`;
- the random span is exactly 1% of demand when price response <= 1, or
  `demand/(100+1000*(p-1))` when response > 1, truncated with minimum 1;
- final home and visiting counts sum terrace+seating separately, with season
  tickets added to home attendance only after ordinary home ticket revenue.

The class-demand body is closed, but the full producer is not yet declared
complete. Exact next target is the two upstream side-modifier helpers
`0x5DBA60` and `0x5DBCD0`; once those are translated, materialize only the
minimum original-compatible ticket/stadium state and add deterministic finance
regressions.


## Gate 10 attendance side modifiers resolved — 28 September 2026

Recovery generation 28 resumed from `ad9c826fbcb5d332254ee84d860a783589d2811e`
and continued only the two remaining upstream attendance helpers.

Instruction-level translation closes both:

- ordinary league `0x5DBA60` is the weighted average of first-XI rating,
  end-of-season opportunity, league-position and league-importance factors;
- first-XI rating is exactly the first 11 roster entries' `0x41E1D0` overall
  values summed and divided by 800;
- position is neutral before five matches played and for the final three
  matches remaining, otherwise `1 - table_index/team_count`;
- the late-season branch uses exact title/promotion/playoff/relegation points
  gaps and accepts a positive gap only when it is reachable at no more than
  three points per remaining match;
- the named end-play defaults produce factors 1.0/0.8/0.6/0.3/0.2;
- alternate type-6 `0x5DBCD0` is a 10:5 weighted own/opponent XI-rating blend
  followed by an exact 0.2 multiplier.

All associated named tuning globals and shipped defaults were tied back to the
loader. The gate-receipt producer is now formula-complete at the instruction
level. No runtime behavior changed in this checkpoint.

Exact next task: recover/materialize the minimum original-compatible stadium and
26-section ticket state needed by `+0x694/+0x6B0`, then implement the recovered
attendance/revenue path with deterministic regressions.


## Gate 10 stadium source-state checkpoint — 28 September 2026

Recovery generation 29 resumed from main `3bb6b90f` and continued only the
source-state dependency beneath the already-complete gate-receipt formula.

New instruction/source-format results:

- `DBRUser +0x6B0` is an owned 0x1BC4-byte stadium runtime object created by
  `0x65CB20` on the fresh path and on demand during load;
- original per-club `.MAP` data supplies the stadium grid. The exact valid-map
  read is `FM\\0 + 0x1A0 bytes + 40x40 dwords + one byte per non-empty grid
  building + 0x10 bytes`;
- Arsenal's original map is an exact validation case: 1,355 non-empty cells and
  8,190 total bytes;
- 26 hard-coded constructor anchors map the original stadium buildings to the
  26 ticket-section IDs used by Gate 10;
- `DBRUser +0x694` is exactly a 0x7C-byte ticket object: five header dwords
  followed by 26 section-state dwords;
- fresh section bootstrap writes -1 only for mapped stadium instances carrying
  flag bit 0x02 and 0 otherwise, before the previously recovered season-ticket
  and visiting allocation passes;
- the 3,000×0x74 global building table used by ticket capacities is loaded from
  the original WAD member `Lists\\Buildings.dat` by `0x660A80`;
- the extracted original member is exactly 3,000×0xD0 serialized bytes, with
  each entry read by the original path as 0x74 plus a 0x5C overlay at live
  record+8.

This removes the need to approximate stadium capacity from fan-base fields or
to reconstruct the legacy stadium renderer for Gate 10. Remaining source-state
work is to lock the fresh ordinary ticket-price initialization and package the
minimum original WAD/map resources or an exact parser-backed representation,
then implement deterministic gate-receipt tests.


## Gate 10 ticket-price initialization closed — 28 September 2026

The remaining fresh ordinary price state is now instruction-locked.
`0x5DE160` lazily initializes zero ticket prices from `0x40CBC0` reference
prices, preserving existing nonzero user settings. It converts the seating
reference and the exact 0.75 terrace derivative through the normal money path,
then applies a fan-base-order multiplier of 90%, 95% or 100% according to the
club's `+0x70` index rank within the league. Both results use the original
truncation-toward-zero helper before writing seating `+0x0C` and terrace
`+0x08`.

The match-day gate producer now has no remaining research prerequisite for the
minimum Premier League implementation. Next: add the exact original stadium
source parser/runtime state and deterministic gate-receipt regressions.


## Gate 10 stadium/ticket implementation checkpoint — 28 September 2026

The first runtime implementation slice for live gate receipts is now verified.

Committed behavior through `02ce20502b3a80e62c9485ac2d7fdb7e8b9b5200`:

- `reconstruction/stadium_state.py` parses the recovered original 3,000-record
  `Buildings.dat` layout and per-club `FM\0` MAP grid without storing source
  game data in Git;
- `Master.dat +16` is exposed as each club's original MAP path;
- MAP rotation, row-major instance flags and the original descending section
  anchor overwrite behavior are preserved;
- the minimum `DBRUser +0x694`-equivalent ticket runtime state is represented;
- fresh unavailable-section state and the exact visiting-supporter allocation
  use the recovered fixed section order, including its duplicate section-24
  quirk and the exact 10% capacity threshold;
- `reconstruction/gate_receipts.py` implements the instruction-locked ticket
  price response, four-cell floating demand caps, x87-equivalent truncation and
  15-bit MSVC randomized subtraction as source-independent primitives.

Two initially failing new tests were corrected at the test layer only: original
MAP flag bytes are consumed in row-major grid order, and a floating demand
assertion now uses tolerance rather than introducing rounding absent from the
executable.

GitHub Actions at `02ce2050`:

- reconstruction suite: **514 tests passed**;
- repository asset-policy workflow: **passed**.

Exact next task: attach recovered fresh terrace/seating price initialization and
source-backed club/competition inputs to the ticket runtime state, then integrate
the complete gate attendance/revenue producer into normal matchday progression
with deterministic ledger regressions.


## Gate 10 gate-receipt runtime/ledger checkpoint — 28 September 2026

Implementation has advanced from source parsing into the complete testable
receipt/ledger slice.

Verified through `ad31b680f07f2a5ff552e22a76a37efccfb9cc4f`:

- lazy ordinary ticket-price initialization implements the recovered 90/95/100%
  fan-base-rank bands, truncation toward zero and preservation of existing
  nonzero user prices;
- `GameState.materialize_gate_source_state` combines a parsed original stadium,
  the exact fresh section/visiting allocation, club capacity and league fan-base
  ranking while keeping the unresolved tuning/currency reference-price adapter
  explicit;
- the aggregate gate calculator consumes its four random values in the original
  order: home seating, visiting seating, home terrace, visiting terrace;
- the aggregate returns ordinary home/visiting attendance and exact host cash
  amounts from terrace/seating counts and prices;
- season-ticket quantity is appended to home attendance only after ordinary
  category-2 revenue, preserving the separate category-3 sale path;
- `GameState.post_gate_receipts` credits category 1 visiting-supporter and
  category 2 home-supporter revenue only when the home club owns a materialized
  Balance.

A shipped-data check independently confirms Arsenal's PL fan-base ordering:
19 of 20 clubs have `fan_base_index <= 31`, placing Arsenal in the 100% fresh
price band; its source stadium capacity remains 38,500 for the exact 10%
visiting-allocation threshold.

GitHub Actions at `ad31b680`:

- reconstruction suite: **523 tests passed**;
- repository asset-policy workflow: **passed**.

Exact next task: derive the remaining live attendance inputs from current
`GameState`/source data, especially the neutral-named supporter factor and
ordinary league side modifier, then call the four-cell calculator and ledger
posting exactly once at the recovered matchday point.


## Gate 10 Premier League FanFactor resolved — 28 September 2026

The neutral supporter tier factor in the implemented gate formula is now
source-backed. `0x410FF0` selects among `FanFactor1..5` using the competition's
index in its country's sorted root-competition array. The shipped defaults are
0.9/0.8/0.7/0.6/0.5, with later/default indices using 0.5. England's root order
places Premier League competition 0 at index 6, proving the PL factor is
**0.5**.

Next integration dependencies are the controlled-club facility attendance
multiplier and the exact four gate-RNG draws' placement relative to match and
post-match RNG consumers; automatic fixture posting remains disabled until
those are source-backed.


## Gate 10 normal Premier League gate integration — 28 September 2026

The live Gate-10 receipt path is now attached to normal Premier League fixture
progression.

New source-backed inputs and ordering:

- Premier League `EPBase = 30.0`, giving exact reference prices 30.0 seating
  and 22.5 terrace;
- fresh controlled-club facility attendance factor = 0.90 because the original
  `+0x65C` facility collection starts empty;
- ordinary side modifiers are derived from the current pre-match league table
  and selected XI through the recovered `0x5DBA60` formula;
- each normal league fixture consumes exactly four gate RNG draws after
  MatchCalculator and before incident/Form RNG, even when no user Balance is
  credited;
- controlled home fixtures with materialized source-backed stadium/ticket state
  post category 1 visiting-supporter and category 2 home-supporter revenue at
  that exact point.

Implementation commits:

- `17c5680` source-backed gate side-input helpers;
- `8c7e0fe` exact live-input regressions;
- `09f243d` normal PL gate RNG/receipt integration;
- `0d3010d` live input/RNG integration regressions.

GitHub Actions at `0d3010df0dbbb60ab147d40dedd1ad83ff533965`:

- reconstruction suite: **531 tests passed**;
- repository asset-policy workflow: **passed**.

The ordinary PL gate-receipt path is no longer the active research blocker.
Next Gate-10 trace: close Balance credit `0x5DC510`'s secondary category-1600
debit conversion/rounding before integrating it.


## Gate 10 category-1600 credit debit integrated — 28 September 2026

The remaining Balance-credit conversion ambiguity is closed.

`Balance::credit 0x5DC510` does not round the secondary debit to an integer.
It converts the incoming finance value to double, multiplies by exact literals
0.01 and 0.2, constructs a second finance value with conversion flags zero, and
calls `Balance::debit` as category 1600 / flag 1. The result is therefore an
exact floating finance value equal to **0.2% of the incoming credit**.

Implementation consequences:

- Balance current cash and postings now preserve fractional values;
- every credit inserts the category-1600 debit before the primary credit in
  ledger order;
- a rounding-sensitive regression proves that credit 1 produces debit 0.002;
- transfer seller credits and gate receipts now include their original
  secondary debit;
- internal save schema advanced from 9 to **10** so fractional cash/postings
  survive roundtrip.

The first CI pass exposed only stale assertions that assumed credits had no
secondary debit. Those were reconciled without changing the recovered behavior.

GitHub Actions at `3fc54ed8524fabade0f37be7017f84d5e967a279`:

- reconstruction suite: **533 tests passed**;
- repository asset-policy workflow: **passed**.

Exact next Gate-10 task: trace `Balance` constructor `0x5DC400` and its
fresh-game callers to recover authoritative new-game starting cash instead of
requiring an explicit caller-supplied value.


## Gate 10 starting cash source resolved — 28 September 2026

Recovery generation 33 continued only the active Balance initialization trace.
The source is now closed end-to-end:

- `Balance::Balance 0x5DC400` is zero-initialized on fresh DBRUser creation;
- DBRUser startup `0x425680` later reads controlled-club
  `DBRClub +0xD0/+0xD4` and writes the converted value to active Balance
  `+0x10`;
- compact club parser `0x4022D0` reads that qword directly from
  `Master.dat` club bytes **+165..+172**;
- runtime copier `0x403660` preserves it unchanged;
- the field is IEEE-754 double starting cash, e.g. Arsenal 28,000,000.0 and
  Manchester United 34,000,000.0;
- the standard analyzed build uses currency scale 1.0, so fresh current cash is
  exactly the packed double.

This removes the last reason to require a guessed or externally supplied
starting Balance amount. Next task: parse the field into `Club`, materialize the
controlled club Balance from it, and add deterministic parser/runtime tests.


## Gate 10 financial-objective lifecycle checkpoint — 28 September 2026

The active board/job-security trace moved from the previously identified reason-5
sacking event into the Balance-owned financial-objective state.

Verified results:

- the objective subobject starts at active Balance `+0x30`;
- three candidate IDs are generated and presented through RTTI-backed
  `EAMManagerNewClubSelectObjectivesub` / `EAMManagerSelectObjectivesub`;
- selection installs both an immediate starting-funds amount and a separate
  formal target;
- the immediate amount **overwrites live current cash**, meaning Master.dat
  club +165 is the pre-objective base rather than always the final opening cash;
- the deadline is exactly three years after selection;
- all 17 starting-funds/target percentage pairs are instruction-locked;
- `ChairmanPercentBudgetMiss = 95` and deadline cash at or below 95% of target
  sets reason 5, which feeds `EAMManagerSackedFailedBudget`;
- the check belongs to the controlled-club competition/season lifecycle, not a
  monthly cash test.

Exact next target: translate `0x5DFD30` far enough to generate the authentic
three candidate objective IDs for a Premier League club, then materialize and
persist the selected objective state without inventing chairman policy.


## Gate 10 Premier League objective candidates resolved — 28 September 2026

Recovery generation 34 continued only candidate generator `0x5DFD30`.

Fresh objective state is `+0x9C = 0`. The Premier League's two hierarchy
predicates are both false, and its top-side promotion/playoff allocation count
is zero, so fresh PL candidate generation consumes no RNG. The exact candidate
triples are:

- fan-base rank count >= half the league: **13, 1, 5**;
- fan-base rank count < half the league: **1, 5, 6**.

Arsenal's fan-base index yields rank count 19/20, so its authentic new-manager
financial objectives are IDs **13, 1, 5**.

Next task: materialize the Balance-owned objective state, selection cash/target
replacement and three-year deadline evaluation in the clean-room runtime, with
save persistence and deterministic reason-5 dismissal tests.


## Gate 10 financial objective runtime integrated — 28 September 2026

The source-backed Premier League chairman objective is now a persisted part of
the clean-room Balance runtime.

Implemented behavior:

- fresh PL controlled-club Balance state materializes the exact three candidate
  IDs from the recovered fan-base-rank branch;
- Arsenal/high-half clubs receive `13,1,5`; lower-half clubs receive `1,5,6`;
- selecting an objective uses the recovered ID-specific starting-funds and
  target percentages and immediately replaces live Balance cash;
- selection stores the start date and exact three-calendar-year deadline;
- deadline evaluation matches `0x5E1D90`'s **year comparison**, not a daily
  full-date comparison;
- once the separately recovered `+0x68` progression gate is set, cash above
  target is success, cash strictly above 95% of target is a non-sacking near
  miss, and cash at/below 95% returns dismissal reason 5;
- if the deadline-year check occurs while `+0x68` is still clear, the original
  branch returns dismissal reason 4 rather than silently treating it as the
  financial-target path;
- the progression gate is deliberately not auto-enabled at objective selection;
  the executable sets it later from season/competition progression;
- internal save schema advanced to **11** and preserves the complete implemented
  objective state.

Implementation commits include `75a23365`, `f39e63c1`, `d9cedba2`,
`00dda8ac`, `86ab1e95`, `7e5cdefd`, and `cf59d6dd`.

GitHub Actions at `cf59d6ddef3034ac5ea96b91605fd2641f67d3a3`:

- reconstruction suite: **541 tests passed**;
- repository asset-policy workflow: **passed**.

Exact next task: translate and attach the later season/competition transition
that sets objective `+0x68 = 1` (and updates `+0x9C`) so deadline evaluation
can be invoked automatically at the correct lifecycle point rather than through
the explicit clean-room gate setter.


## Gate 10 sporting-objective progression resolved — 28 September 2026

The objective lifecycle's remaining `+0x68` semantic gap is closed for the
normal Premier League path.

Season finalization calls the 17-way objective progression routine twice around
the competition transition. The pre-transition flag-1 pass evaluates the normal
PL finishing target. For the three source-backed fresh PL candidates:

- ID 13 succeeds only at table index 0 (champion);
- ID 1 succeeds at index 0 or 1 (top two);
- ID 5 succeeds when `table_index <= team_count // 2`, preserving the original
  inclusive midpoint comparison.

Success writes objective `+0x68 = 1` and increments `+0x9C`. This proves that
`+0x68` is a sporting-objective success gate, explaining why the deadline path
uses reason 4 when it is clear and only applies the reason-5 financial target
when it is set.

Next implementation block: run this PL-specific sporting check once at the
completed-season boundary, then invoke the already-tested year-gated financial
objective evaluator from the same annual lifecycle.


## Gate 10 automatic financial-objective season bridge integrated — 28 September 2026

The previously explicit objective progression gate is now attached to the
completed Premier League season lifecycle.

Implemented same-PL behavior:

- objective 13: champion only (`table_index < 1`);
- objective 1: top two (`table_index <= 1`);
- objective 5: exact executable midpoint quirk
  `table_index <= team_count // 2`;
- objective 6: succeeds in the current same-Premier-League/no-relegation slice
  because its executable branch accepts an unchanged or improved competition
  classification.

The progression check runs only when the Premier League fixture set has just
become complete, both in the autonomous all-AI day path and after the trailing
fixtures of the human-controlled final matchday. It skips the objective-selection
year, sets `+0x68` and increments `+0x9C` on sporting success, then invokes the
already-recovered year-gated three-year financial evaluation.

The broader promotion/relegation classification branches remain deferred to the
later broader-competition season transition. Also, the already-known unresolved
Premier League equal-points fallback can affect a club exactly on an objective
cutoff if the original game would order a perfect statistical tie differently.

Implementation commits: `3648845f`, `72fceee0`, `4857764c`,
`7d9ad94b`, and `eabe0838`.

GitHub Actions at `eabe0838d3f8a2d235d72b05e71a7f61f40761af`:

- reconstruction suite: **548 tests passed**;
- repository asset-policy workflow: **passed**.

Next Gate-10 target: trace the concrete gameplay side effect of the reason-4 and
reason-5 manager-sacking events and materialize the minimum authentic
job-security/control state. The objective evaluator currently returns the exact
reason but must not invent how FM2001 removes or reassigns the manager.


## Gate 10 manager-sacking side effect resolved — 28 September 2026

Objective failure reasons 4/5 now have a concrete downstream control path.
`0x42C6C0` simply writes the reason to persistent DBRUser `+0x10D8`.
Later `0x4290F0` turns a nonzero reason into the matching sacking EAM/message
and returns true. The shipped follow-up gate `0x516010` is constant true.

In a single-user game, the main loop then clears active control state and enters
`0x4C3280`, the PStartMenu creation family. It does not destroy the DBRUser or
Balance object at the reason-write site. Multi-user play cycles user context
instead.

Next implementation: persist the sacking reason in GameState/save state and end
active human control only after the current season-finalization/matchday
maintenance completes, preserving the original separation between persistent
reason state and front-end control transition.


## Gate 10 closure audit and Gate 11 transition — 28 September 2026

Gate 10 was audited against its roadmap completion criteria after the
manager-sacking control transition landed.

Verified closure checkpoint:

`5d626f0fda83d3f7b8ca09d82061002017b68b37`

GitHub Actions for that exact SHA passed:

- **550 reconstruction tests**;
- repository asset-policy workflow.

The audit found all Gate-10 criteria satisfied without inventing unsupported
finance systems. In particular, the legacy chairman transfer/wage-budget event
family is not treated as a live scalar because no ordinary fresh-game producer
or normal Finance/Transfer UI consumer has been recovered; the demonstrably live
constraint is Balance/current cash plus recovered accounting and board-objective
paths.

A dedicated closure record is now stored in
`research/GATE10_FINANCES_AND_BOARD.md`. ROADMAP and CURRENT_STATE have
advanced to **Gate 11 - Broader management systems**.

Gate-11 first task: audit training/development, scouting, youth, morale,
medical/injury, discipline, messages/news and recurring manager tasks against
the existing human gameplay loop, then choose the shortest original-backed path
to another meaningful human management workflow.


## Gate 11 training workflow selected and weekly state bounded — 28 September 2026

The Gate-11 implementation audit compared training/development, scouting, youth,
morale, medical/injury, discipline, messages/news and recurring tasks against
the current human gameplay loop. Training is the shortest high-value next
workflow: monthly age/development already runs live, exact seven training
profiles and training probabilities are implemented, while the original
per-player training method and weekly active-training state were not.

New instruction-level findings:

- active training runs on the recovered Saturday phase
  `(date_integer + 5) % 7 == 0`;
- `0x42AE40 -> 0x61CBA0` walks the owner's 40 × 0xC8 player-training
  records and `0x61C520 -> 0x4EACE0` updates eligible players;
- embedded training byte `+0x00` is the method ID and fresh records default to
  **5 = Fitness**;
- dword `+0x04` starts at 8, decrements once per weekly training update and
  resets to 8 when it reaches zero;
- `+0x0C..+0x1C` are the 17 persistent per-skill counters used by monthly
  development and by exact +8/-8 active-training changes;
- `+0x08` tracks active increments and `+0x64..` holds seven per-method
  result counters;
- zero-profile reversals occur only at the countdown boundary, preserving the
  original eight-week decay cycle.

No modern runtime behavior changed in this checkpoint.

Exact next target: recover the method-change setter semantics and the two
weekly eligibility predicates, then materialize the minimum persistent
per-player training state and human method-selection workflow before attaching
Saturday updates.


## Gate 11 weekly training eligibility resolved — 28 September 2026

Follow-up disassembly of `0x61C520` ties the two weekly training exclusion
checks to existing DBRPlayer flag semantics:

- injured, `+0x14 bit 0`;
- separate selection-exclusion state, `+0x14 bit 2`.

Suspension bit 1 is not tested by this call path, and bit 2 remains distinct
from the separately persisted cup-tied mechanism. The remaining narrow trace
before state implementation is the human training-method mutation itself.


## Gate 11 human training state verified — 28 September 2026

The first playable Gate-11 management action is now integrated without altering
the shared game RNG.

Verified checkpoint:

`3f7bec072a66437361a908128ea45de9e95b418d`

GitHub Actions passed:

- **555 reconstruction tests**;
- repository asset-policy workflow.

Implemented and tested:

- fresh per-player training method **5 = Fitness**;
- original eight-week countdown;
- active training count;
- 17 persistent per-skill training counters and dword-state equivalents;
- seven per-method result counters;
- human-controlled per-player method selection restricted to the human squad;
- method changes preserve accumulated counters/countdown, matching the original
  independently serialized record layout and direct method-byte mutations;
- save schema **13** persists all of this state;
- weekly eligibility helper is injury OR selection-exclusion, not ordinary
  suspension.

Automatic Saturday `0x4EACE0` execution remains intentionally disabled at
this checkpoint. The next trace must instruction-lock the mandatory weekly RNG
calls and separate them from still-unmaterialized specialist-coach,
condition/injury and timed-effect branches before calendar integration.


## Gate 11 weekly training RNG boundary closed — 28 September 2026

The primary active-training function itself is now bounded exactly.

- `0x4EACE0` ends at `0x4EAEA2`; later condition/injury logic is a separate
  routine.
- Its pre-loop timed-effect expiry `0x4EBA90` uses no RNG, and fresh training
  records initialize all 17 timed-effect bytes to zero.
- The skill loop consumes one `RNG(100)` only for each nonzero profile weight,
  in skill order 0..16.
- Exact eligible-player draw counts are 0/4/4/5/5/6/5 for methods
  Rest/Attacking/Midfield/Defensive/Goalkeeper/Fitness/Technique.

The shared-RNG placement is therefore no longer the blocker. Automatic Saturday
training still must not guess the quality multiplier because the current modern
runtime does not yet materialize the original Youth Team Coach, Assistant
Manager and Training Centre owners consumed by `0x4EACE0`.

Next implementation boundary: add the exact weekly state transition as an
explicit-quality primitive with deterministic RNG tests. Keep calendar wiring
disabled until the quality inputs become source-backed.


## Gate 11 exact weekly training primitive verified — 28 September 2026

Checkpoint `efe8a3039536cda6e7470d0237262d859c6cad03` passed:

- **559 reconstruction tests**;
- repository asset-policy workflow.

The modern RuntimePlayer now has an exact explicit-quality implementation of the
primary `0x4EACE0` weekly transition. Deterministic tests lock:

- six Fitness RNG(100) draws and the exact resulting MSVC RNG state;
- successful +8 skill/counter/method-result progression;
- Rest countdown-zero reversal with zero RNG draws;
- ineligible injury/selection-exclusion weeks consuming neither RNG nor
  countdown;
- nonzero profile slots consuming RNG even when the skill is already at target.

Automatic Saturday execution remains disabled. Fresh-game startup demonstrably
creates a global support-staff pool and assigns staff to each user before play,
so using quality 1.0 as an implicit fallback would erase original state. The
active trace is now the minimum support-staff type/rating state required to
source Youth Team Coach / Assistant Manager quality, with Training Centre
presence handled only when its original owner is materialized.


## Gate 11 training support-staff source narrowed — 28 September 2026

The quality-multiplier dependency is now tied to minimum original staff fields.

- training first looks for support type 3 (Youth Team Coach), then type 2
  (Assistant Manager fallback);
- CSupportStaff `+0x04` is the virtual staff type;
- `+0x10` is the normal 1..5 training rating;
- status `+0x18 == 2` forces the training rating virtual to return 1;
- fresh generator `0x4C98B0` consumes RNG for an age-like 25..49 value,
  derives/clamps a 1..5 rating, consumes `RNG(16)+1` for staff type, and
  appends the object to the global pool;
- fresh startup grows that pool to 200 and calls the per-user rebuild
  `0x4C9E90` twice before normal play.

This proves a silent fresh-training Q=1.0 assumption would be unsafe until the
per-user employed list is resolved. Training Centre feature ID5 is a separate
case: the source-backed fresh DBRUser facility collection starts empty, so its
initial +0.25 contribution is exactly absent.

Next trace: map the three DBRUser support-list headers and the `0x4C9E90`
assignment result far enough to determine whether a fresh user begins with a
type-3 or type-2 staff member in the list scanned by training.


## Gate 11 fresh training staff list resolved — 28 September 2026

Fresh DBRUser initialization now proves the training quality is always
staff-backed:

- `0x425680 -> 0x4D1760` creates initial support types 1,2,3,4,5,13;
- `0x4CA070` routes types 1..5 into the `+0x5B8/+0x5BC` list scanned by
  training;
- type 3 Youth Team Coach therefore exists in the fresh training list;
- types 1..5 bypass the special compatibility cases in `0x4CAF80`, so their
  status becomes 1 and their real rating is used;
- `0x4C9D40(type)` consumes exactly two draws per fixed initial staff:
  `RNG(25)` for age-like state, then `RNG(2)` for rating;
- the Premier League tier yields rating 1 or 2, hence fresh Q is exactly
  **1.25 or 1.30**; fresh Training Centre remains absent.

The active blocker is now only startup RNG placement: locate the exact CRT state
entering the one-shot `0x4D1760` user initialization so the Youth Coach
rating can be reproduced without corrupting the post-schedule/match RNG ledger.


## Gate 11 fresh-staff RNG boundary checkpoint — 28 September 2026

The remaining fresh training-quality RNG dependency is no longer an open-ended
startup search. Direct startup disassembly proves `0x4F7C00` runs the primary
`0x947AD8` `0x616620` pass and then the secondary `0x947AF0` pass. On return,
TeamSelect immediately counts the support-staff pool and calls `0x4C98B0` until
it reaches 200. No CRT-random call occurs between secondary schedule completion
and the first generated support staff.

Thus the exact state entering staff-pool generation equals the **post-secondary
schedule** RNG state. The next trace is now specifically the secondary
`0x616620` RNG stream, not the already-complete primary schedule replay or the
already-resolved staff generator.


## Gate 11 secondary Euro-seed RNG checkpoint — 28 September 2026

The six mode-1 Euro seed DummyLeagues (IDs 182..187) are now tied directly to
Master.dat historical-allocation fields. Canonical membership is 9/9/9/9/9/6,
exactly partitioning the 51 Europe national teams. Their first lazy sort is one
CRT draw per participant, so the secondary Cup special paths contribute a fixed
**51 draws** from these seed sorts. Repeated `0x4F4940` calls do not add draws
after a seed's sorted flag is set.

Next: compose the remaining mode-1 Cup/child-League schedule RNG, then replay
`0x4FA790` from the newly parsed InternationalFixture table and finally the
secondary schedule-bucket shuffle.


## Gate 11 secondary competition RNG state locked — 28 September 2026

Mode-1 competition initialization is now replayed exactly from post-primary
state `0xD25DFFE6` to **`0x492DC9DC`** in **334 CRT draws**. The ledger is:
139 first-access regional/Euro-seed DummyLeague draws, 93 full Cup-round
Fisher-Yates draws, 72 draws from twelve 4-team child League instances, and 30
draws from two 6-team qualifiers.

Child competition 188 is explicitly disabled by `0x4F59A0(6)`: its five-team
count does not match the selected six-team qualifier size, bit 0x02 is set, and
`0x4F5150` skips its procedural builder. It consumes no fresh-start RNG.

Exact next boundary: replay the 108 source-backed `0x4FA790` international
fixtures from `0x492DC9DC`, preserving regional sorted-team identities because
same-team avoidance can alter cursor exhaustion, then perform secondary
`0x615BE0` bucket shuffling.


## Gate 11 secondary schedule RNG tail closed — 28 September 2026

The source-backed 108-row InternationalFixture replay and final mode-1 schedule
bucket shuffle are now deterministic.

- `0x4FA790` starts from `0x492DC9DC`;
- it consumes **245** CRT draws in **18** participant-pool shuffles;
- one same-team avoidance advances a pool cursor without consuming RNG;
- post-`0x4FA790` state is **`0xCAB0B953`**;
- the secondary container contains **262 schedule nodes** in **45 non-empty buckets**;
- final `0x615BE0` therefore consumes **217** Fisher-Yates draws;
- exact post-secondary state is **`0x61D6DFA2`**.

A clean-room helper/test now locks the final bucket-state transition. The shared
CRT boundary required for fresh support-staff generation is therefore closed.
Exact next task: replay the already-recovered 200-person support-staff pool and
user-assignment draws from `0x61D6DFA2` through the first
`0x425680 -> 0x4D1760` fixed-staff initialization.


## Gate 11 fresh support-staff pool and candidate replay — 28 September 2026

The post-secondary staff boundary is now replayed through the two immediate
TeamSelect candidate-list rebuilds.

New-game branch `0x4C37C7` explicitly clears the global support-staff list at
`0x875600/+0x04/+0x08` before the later fill-to-200 loop. Starting from the
exact post-secondary state `0x61D6DFA2`:

- 200 calls to generic generator `0x4C98B0` consume exactly **600 CRT
  draws** (`RNG(25), RNG(4), RNG(16)` per object) and leave
  **`0x2992DEFA`**;
- the first `0x4C9E90(user 0)` starts from an empty candidate list, consumes
  **8 draws**, selects seven pool indices
  `110,106,5,39,74,65,192`, and leaves **`0x7B3EA402`**;
- the second immediate `0x4C9E90(user 0)` consumes **17 draws**, prunes pool
  entries 110 and 5, performs 11 selection attempts (including one duplicate
  selection of 172), reaches the 15-candidate list
  `106,39,74,65,192,125,172,69,20,133,129,140,2,139,45`, and leaves
  **`0x1D1A278D`**.

Fresh generic staff types are always 1..16, so the type-zero repair branch
`RNG(16)` inside `0x4C9E90` is unreachable on this path.

Data-free replay helpers and a canonical regression were added in
`reconstruction/support_staff_startup.py` and
`test_support_staff_startup.py`.

The next RNG boundary is now narrower but not yet closed: the first
`0x4A8070` calendar-maintenance pass executes before `0x425680`. Its
weekly branch includes RNG-bearing `0x6194D0`, and the day-one branch invokes
another `0x4C9E90` before fixed staff creation. These intervening calls must
be replayed before the Youth Team Coach's fixed `RNG(2)` rating can be
declared deterministic.


## Gate 11 first-calendar staff boundary correction — 28 September 2026

The first maintenance call before fixed support-staff creation has now been
narrowed substantially.

### Startup date is weekly-aligned, not day 1

Date initializer `0x64CC70` constructs **July 1** for the supplied startup
year, then computes `(serial_date + 5) % 7`. When the remainder is nonzero it
adds `7 - remainder` to the serial date before returning it. The fresh
TeamSelect path stores that aligned value as the global current date before
calling `0x4A8070`.

For the 2000/01 start this advances the July-1 value by three calendar days.
Consequently the first `0x4A8070` call enters its weekly branch but its later
decoded day-of-month test is **not 1**. The day-one block is therefore skipped
before `0x425680`: there is no third `0x4C9E90`, monthly-history update or
`0x4E2840` on this boundary.

### First 0x6194D0 user-club phase

Starting from the already-locked state **`0x1D1A278D`**, the first
`0x6194D0` phase scans Arsenal's 37 fresh roster entries.

- fresh player transfer-list bit 8 is clear;
- every Arsenal player resolves to the user-controlled active club;
- each therefore consumes one `RNG(10)`;
- player `+0xB8` was initialized from the same `0x4205A0` transfer
  valuation, so the value-difference candidate path has zero difference and
  does not append a player;
- after the 37 draws the CRT state is **`0x6400EEC0`**;
- because no candidate was appended, the fallback `RNG(100)` runs;
- its canonical result is **74**, above the shipped 25% unsolicited-bid
  threshold, so no roster-index draw follows.

This user-club phase therefore costs exactly **38 CRT draws** and leaves
**`0xDFCED283`**.

The remaining pre-fixed-staff uncertainty is now wholly inside the later
global transfer/loan-maintenance phases of `0x6194D0`. The day-one calendar
branch is no longer part of this startup boundary.


## Gate 11 empty fresh transfer-candidate shuffles — 28 September 2026

The next `0x6194D0` segment is now bounded exactly from fresh source state.

Across all 30,064 compact Master.dat player records, initial runtime flag source
`+0x14` contains neither bit 7 nor transfer-list bit 8. The fresh startup
paths before the first weekly maintenance do not set either state. Therefore the
global player scan at `0x6196CD..0x6197FF` refreshes cached `+0x230`
valuations but appends **zero** players to the shared transfer-candidate array
and consumes no RNG.

The fresh eligible-club list at `0x6197FF..0x6198B4` contains exactly
**895** non-user European clubs after the source-backed name/category,
country-European-index, transfer-window and valid-manager gates.

Both immediately following calls to `0x619DC0` always Fisher-Yates shuffle
that 895-club vector before checking whether the transfer-candidate array is
empty. Since the candidate count is zero, each call exits directly after its
shuffle:

```text
0xDFCED283
  -- 894 draws, first 0x619DC0 --> 0xC6B73181
  -- 894 draws, second 0x619DC0 -> 0xBD5CC00F
```

No acquisition fee/wage or target-selection RNG is reachable in these two
calls on fresh startup. The active boundary is now the reverse 895-club
transfer-list population loop beginning at `0x61991F`.


## Gate 11 reverse transfer-list population boundary — 28 September 2026

Recovery generation 40 resumed from main `61119f758d3ac8cb5a428650b37dc101f9e8152e`
and continued only the active `0x61991F` startup-maintenance boundary.

The reverse club population loop is now structurally exact:

- named tuning global `0x821610` is **MAX_PLAYERS_ON_TRANSFER_LIST**;
- shipped default is **1000**;
- the twice-shuffled eligible club vector has the already-proven fresh count
  **895**;
- the loop decrements its index before the first body execution and exits when
  the index reaches zero, so it visits vector indices **894 down through 1**
  exactly once and never processes index 0;
- every vector member already passed `0x403E70`, whose success path requires
  `0x403E10` manager validity, so the repeated manager check at `0x619935`
  cannot skip a fresh vector member absent intervening mutation;
- fresh transfer-candidate count entering the loop is zero and each iteration
  can append at most one player, so the 1000-player cap cannot terminate the
  894-visit loop early;
- therefore the loop executes exactly **894 mandatory RNG(10) dispatch draws**;
- dispatch result <7 enters `0x61A9A0(club,0)`; 7..9 enters `0x4050F0(club)`;
- when either selector returns a player, `0x420A10` sets DBRPlayer flag bit 8,
  the already-mapped transfer-list state, and increments the running populated
  count by one.

This does **not** yet give the final shared CRT state because both selector
branches can consume additional nested RNG, notably through player eligibility
`0x417470`, and `0x4050F0` also contains its own rejection-sampling draws.

Exact next target: replay the nested `0x61A9A0 / 0x4050F0 -> 0x417470` RNG
against fresh roster/player state, then continue into the loan-maintenance
segment of `0x6194D0`.


## Gate 11 nested transfer selector RNG map — 28 September 2026

The two branch-local selectors underneath the 894 mandatory dispatch draws are
now instruction-mapped sufficiently to replay without inventing RNG calls.

### Player eligibility 0x417470(player, mode)

The transfer-list population loop always calls this with mode 0. Before any RNG,
the player must have active/current club equal registered club and must pass the
mode-0 flag/status gates. It then requires `0x419390(player) >= 26`, rejects
players for whom `0x417460` is true, and obtains the maximum preferred-role
overall rating through `0x41E1D0`.

The rating gate consumes either zero or one `RNG(100)`:

- overall >= 70: **no RNG**, passes the rating gate directly;
- 61..69: one RNG(100), passes when result >= 50;
- 51..60: one RNG(100), passes when result >= 33;
- <=50: one RNG(100), passes when result >= 25.

A successful rating gate still requires the final club predicate
`0x417270(player) -> 0x403F10(club)`.

### Random selector 0x4050F0(club)

This selector first rejects the user-controlled club and requires its effective
roster count `0x405080` to exceed the existing AccessFanBase threshold
`0x40DB90`. If that deterministic gate fails, it consumes **no RNG**.

Otherwise it performs at most 20 rejection-sampling attempts. Every attempt
consumes:

1. `RNG(10)`;
2. exactly one roster-index draw chosen by that result;
3. then the selected player's `0x417470(player,0)`, which contributes the
   optional rating RNG above only if the earlier player gates are reached.

The first RNG(10) result selects between two roster regions: result <3 uses the
first branch, otherwise the second branch. The selector returns immediately on
the first player accepted by `0x417470`, otherwise it stops after 20 attempts.

### Positional selector 0x61A9A0(club,0)

No direct `0x64D540` call exists inside this function. It performs its club,
manager, roster-threshold and positional construction deterministically through
`0x61A380/0x61A900`, selects its candidate, and calls
`0x417470(candidate,0)`. Therefore its only possible RNG is the single
rating-dependent `RNG(100)` inherited from that final eligibility check.

### Club qsort key narrowed

The pre-shuffle club comparator `0x619CF0` compares
`club+0x2A0 / club+0x1B8`. The two fields are now structurally identified:

- `0x405470` builds `+0x2A0` from live `0x4205A0` player valuations;
- `0x404E60` builds `+0x1B8` from `0x41FB30`, which normally returns the
  player's cached `+0xB8` valuation.

`0x41FB30` returns zero instead only when the exact age/EU-status test in
`0x41E5A0` is true and contract expiry `+0x154` is at/before the current
calendar date. Fresh startup contract expiries are future-dated, so that zero
branch is not expected for normal fresh club players. The remaining qsort
replay question is whether the live `0x4205A0` value can differ from cached
`+0xB8` across the three-day startup calendar alignment; do not assume all
qsort keys are equal until that date sensitivity is proven or numerically
replayed.

Exact next target: reproduce the eligible-club qsort and both already-bounded
Fisher-Yates shuffles from source state, then execute the 894 dispatch/selector
steps with the now-exact nested RNG rules and transfer-list bit-8 mutations.

## Gate 11 exact eligible-club qsort and shuffle order — 28 September 2026

The remaining club-order dependency before the 894-selector replay is now source-backed and independently validated against the already-known RNG states.

`0x4205F0` transfer valuation is calendar-sensitive here only through integer player age. Between July 1 and the weekly-aligned July 4 startup date, nine of 30,064 source players cross a valuation age band. Cerro Porteño is outside the 895-club European vector, leaving eight eligible clubs whose live/cached qsort ratio differs from 1.0:

```text
Levski Sofia          0.960813673436702
Neftchi Baku          0.964986144313222
Anorthosis Famagusta  0.965667451667081
Slavia Sofia          0.993094744577438
Sileks Kratovo        0.996253483716185
Kidderminster         0.997707747535481
Albion Rovers         1.001184026457622
Torquay Utd           1.007371177945545
```

All other 887 eligible clubs have neutral ratio 1.0 on this fresh boundary.

The static CRT qsort at `0x668DA4` was translated from the executable, including its <=8 short-sort path, middle-pivot partition, explicit swaps and non-stable equal-key handling. With the real `0x619CF0` keys it places Levski/Neftchi/Anorthosis/Slavia/Sileks/Kidderminster at indices 0..5, Albion Rovers at 893 and Torquay at 894.

Running the two recovered `0x619DC0` Fisher-Yates passes over that exact qsort output from `0xDFCED283` reproduces both canonical checkpoints:

```text
first shuffle  -> 0xC6B73181
second shuffle -> 0xBD5CC00F
```

This independently validates the pre-selector club ordering model. The final twice-shuffled vector begins `25, 738, 783, 262, 812, 2, 397, 819, ...`; reverse `0x61991F` visits begin `118, 750, 510, 1216, 430, 622, 877, 243, ...`.

The first dispatch draw from `0xBD5CC00F` is RNG(10)=3, so club 118 enters deterministic selector `0x61A9A0(club,0)`. Exact next target: translate/replay `0x61A380/0x61A900` sufficiently to obtain that candidate, then continue the mapped `0x417470` eligibility RNG and subsequent clubs.


## Gate 11 first exact transfer-list selector replay — 28 September 2026

The first reverse `0x61991F` visit is now closed through its nested positional
selector.

From the proven post-shuffle state `0xBD5CC00F`, the mandatory dispatch
`RNG(10)` returns **3** and advances the MSVC CRT state to
**`0xAB415A96`**, selecting `0x61A9A0(club 118, 0)`.

Club 118 is source-backed **Carlisle Utd** with 20 players and manager 153,
**Ian Atkins**. The manager's stored formations are default **0**, class-3
**2**, class-1 **1**. `0x61A380/0x61A900` combines those three formation
demands against the roster's three preferred-position entries. Role **15
(Attacking Midfield)** is the only role with positive Carlisle supply and zero
combined formation demand, so `0x61A900` selects role 15.

The role-15 player vector contains Steve Soley as a primary AM and Stuart
Whitehead/Lubomir Lapsansky as secondary AMs. Comparator `0x61A520` sorts
preferred-position slot index ascending before role rating, therefore
**Steve Soley (player 7748)** is first. Fresh DBRPlayer load explicitly zeros
runtime `+0xB0/+0xB4`; no pre-maintenance transfer-move path has populated
that field. Consequently every `0x41EE60 / role-rating` ratio is zero and
the first role-15 entry remains the selector candidate.

Soley's exact role-15 / best-preferred-role rating is **34**. His source state
also has flags 0, registered/current club 118, runtime-+0x64 source
`0xFFFFFFFF`, and a 1 July 1999 join date, giving well above the
`0x419390 >= 26` residence gate on 4 July 2000. `0x417470` therefore
reaches its <=50 rating branch. The next `RNG(100)` returns **88**, passes
the shipped >=25 threshold, and advances the shared CRT state to
**`0x6A346701`**.

The final `0x403F10 -> 0x4F3330` club predicate also passes on this fresh
boundary: Carlisle's 20-player roster exceeds its fan-base threshold 16, while
the embedded fresh club-form counters `+0x0C/+0x0E` are zero and the
roster lower bound is satisfied. Thus `0x61A9A0` returns Soley and the
outer loop's `0x420A10` marks player 7748 transfer-listed.

Exact next target: continue from **`0x6A346701`** with reverse visit club 750,
replay all remaining 893 dispatch/selector paths including transfer-list
mutations, then continue through loan maintenance before fixed support-staff
initialization.


## Gate 11 fresh roster order and next exact selectors — 28 September 2026

The remaining fresh-roster ordering dependency under `0x4050F0` is now closed from the executable.

Post-load routine `0x4217E0` walks runtime DBRPlayer records in table order. For each ordinary current-club assignment it calls `0x40D4F0`, which appends the player's WORD ID at `club+0x244 + 2*club+0x294` and increments `club+0x294`. No sort occurs on this fresh path. Therefore the initial roster array for every club is the original Master.dat player-table order, equivalently ascending canonical player-record ID in the shipped data.

Continuing from the first closed visit state `0x6A346701`:

- reverse visit club 750 is Dunaferr, 18-player roster, manager Zoltán Varga with formations 2/5/0;
- its mandatory dispatch `RNG(10)=4` advances to `0xE1E8ADC0` and enters `0x61A9A0`;
- role 15 is the largest positive-supply / zero-demand role (four AM-capable players);
- `0x61A520` ordering places primary-AM Norbert Mitring (player 21416, role-15 rating 34) first;
- Dunaferr's AccessFanBase threshold is 16 and roster count is 18, so the selector enters eligibility;
- Mitring has flags 0, runtime +0x64 = -1, and passes the residence gate; `RNG(100)=55` passes the <=50 threshold and leaves `0x31D39583`;
- the fresh `club+0x1E0` constructor zeros the fields consumed by `0x4F3330`, so the final club predicate passes and Mitring is transfer-listed.

Next reverse visit club 510 is Rot-Weiß Essen, roster count 22. Its mandatory dispatch is `RNG(10)=9`, leaving `0x5EEBAA3A` and entering `0x4050F0`.

The first rejection-sampling attempt is exact:

- `RNG(10)=1` -> first roster region;
- `RNG(21)=14` -> fresh roster index 15;
- index 15 is R. da Silva Cerqueria (player 11588), preferred roles 14/15, best-preferred rating 35;
- his deterministic eligibility gates pass and `RNG(100)=45` passes the shipped >=25 threshold;
- he is accepted on attempt one and transfer-listed;
- shared state after club 510 is **`0xF0AD5F37`**.

The next mandatory dispatch for club 1216 is already fixed at **`RNG(10)=8`**, advancing the shared stream to **`0x590E1D1E`** and selecting `0x4050F0`.

Exact next target: replay club 1216's random selector from `0x590E1D1E`, then continue the remaining reverse visits with transfer-list mutations applied in-order.


## Gate 11 selector replay through club 622 — 28 September 2026

Continuing from club 1216's already-consumed dispatch state `0x590E1D1E`:

- Panahaiki (club 1216, roster 24) enters `0x4050F0`.
- Attempt 1: RNG(10)=0, RNG(23)=2 -> roster index 3, Dusan Jiovanovic (player 14220), best rating 41. RNG(100)=22 fails the <=50 rating threshold.
- Attempt 2: RNG(10)=0, RNG(23)=9 -> roster index 10, Panagiotis Gitsis (player 17751), best rating 59. RNG(100)=96 passes the 51..60 threshold.
- Gitsis is transfer-listed; shared state becomes **`0xEC30AACC`**.

Club 430 (Carmarthen Town) then dispatches RNG(10)=2 -> **`0x2956CE5F`**, entering `0x61A9A0`. Its roster count is exactly 16 and its AccessFanBase threshold is also 16, so the `roster <= threshold` early exit fires before any nested RNG. No player is listed.

Club 622 (KSC Lokeren) next dispatches RNG(10)=2 -> **`0xFE106FA6`**. Its 26-player roster exceeds threshold 16. Manager formations 0/2/1 leave roles 5, 8 and 15 at zero demand; roles 5 and 15 each have supply 3, and the strict greater-than zero-demand tie logic keeps lower role ID 5. Comparator `0x61A520` places primary role-5 Steven de Geest (player 18005) first with rating 51. The defender-group count is 11, above the required four-player group floor. His deterministic eligibility gates pass; RNG(100)=43 passes the 51..60 threshold and leaves **`0xB28F67D1`**. De Geest is transfer-listed.

Club 877's mandatory dispatch is already fixed as **RNG(10)=6**, advancing to **`0x377EEB50`** and selecting `0x61A9A0`.

Exact next target: replay club 877 from `0x377EEB50`, then continue the remaining reverse selector visits in order.


## Gate 11 transfer-club qsort permutation correction — 28 September 2026

The previously recorded 895-club permutation has been **superseded** after an instruction-level audit of CRT qsort `0x668DA4`.

The earlier model correctly recovered the eight non-neutral comparator keys and their extreme sorted positions, but it did not reproduce the executable's equal-key scan semantics inside the 887-club neutral block. In the real partition loop:

- the low scan continues while comparator result is **<= 0**;
- the high scan continues while comparator result is **>= 0**;
- equal keys therefore do **not** stop both scans for an exchange.

A second, literal byte-address translation of `0x668DA4` plus its `0x668EF8` short-sort independently matches the first translation when those exact branch conditions are used. The exact fresh eligible input is also now locked: the `0x6197FF` loop walks DBRClub records in table order, and the already-recovered user/category/name/European/manager filters yield the same 895 source-backed records in ascending runtime-record/club-ID order.

The eight age-sensitive ratios remain unchanged, and the corrected qsort still places Levski/Neftchi/Anorthosis/Slavia/Sileks/Kidderminster at positions 0..5 and Albion Rovers/Torquay at 893..894. What changes is the neutral-block permutation.

The two Fisher-Yates passes still consume exactly 894 draws apiece and therefore still leave the same shared states:

```text
0xDFCED283 -> 0xC6B73181 -> 0xBD5CC00F
```

Those RNG states validate the shuffle **draw counts only**, not the element permutation. The former statement that they independently validated the qsort ordering was incorrect.

With the corrected qsort output, the twice-shuffled club vector begins:

```text
488, 439, 509, 646, 1217, 623, 239, 548, ...
```

and the reverse `0x61991F` visits begin:

```text
805, 610, 140, 862, 362, 757, 507, 214,
611, 166, 867, 698, 399, 68, 209, 234,
779, 719, 1211, 232, ...
```

Therefore the selector replays previously recorded for Carlisle 118, Dunaferr 750, Rot-Weiß Essen 510, Panahaiki 1216, Carmarthen 430, KSC Lokeren 622 and Trisen 877 were performed against a superseded club order and must **not** be used as canonical startup RNG evidence. Their local selector mechanics remain useful spot checks, and the separate fresh-roster-order finding remains valid, but the shared stream must restart at the proven post-shuffle state **`0xBD5CC00F`** with club **805**.

A separate source-offset audit also confirmed that runtime player `+0x64` comes from compact player offset **+88**. Rechecking all players used by the superseded spot replays showed `+88 == 0xFFFFFFFF`; this offset correction does not create an additional RNG discrepancy in those isolated selector tests.

Exact next target: replay the corrected first reverse visit, club 805, from shared state `0xBD5CC00F`, then continue the corrected 894-visit sequence in order.


## Gate 11 corrected first canonical transfer-list selector — 28 September 2026

The corrected 0x668DA4 club permutation makes club **805 (FK Baník Prievidza)**
the first reverse 0x61991F visit. From the proven post-shuffle state
**0xBD5CC00F**, dispatch RNG(10)=3 advances the shared CRT state to
**0xAB415A96** and enters 0x61A9A0.

Club 805 has 21 fresh roster entries and manager 928 Vladimir Rusnak, whose
stored formations are default 0, class-3 2, class-1 1. Replaying
0x61A380/0x61A900 over the source roster makes role 15 (Attacking Midfield)
the largest positive-supply role with zero combined formation demand. Its
weighted supply is 71, ahead of the other zero-demand populated roles 5=36 and
7=35. Comparator 0x61A520 then orders the two primary role-15 players by
role rating, selecting **Marek Holmik (player 17608, rating 36)** ahead of
Milos Krsko (35).

Fresh player +0xB0/+0xB4 are still zero, so the 0x41EE60/rating candidate ratio
leaves the first sorted role-15 player selected. Holmik has flags 0,
registered/current club 805, source +88 = 0xFFFFFFFF -> runtime +0x64, and his
1950 source join date is normalized by the startup rule to current-date minus
200 days, clearing the >=26-week 0x419390 gate. The roster-category minimum for
his midfielder group is also satisfied (9 midfielders vs threshold 5).

His best-preferred rating 36 reaches the <=50 0x417470 branch. The next
RNG(100)=88 passes the >=25 threshold and advances the shared CRT state to
**0x6A346701**. The final fresh-club 0x403F10 predicate passes, so
0x61A9A0 returns Holmik and outer 0x420A10 marks player 17608 transfer-listed.

Exact continuation: reverse visit **club 610** from state **0x6A346701**.


## Gate 11 corrected selector replay through club 862 — 28 September 2026

Continuing from the corrected first canonical visit:

- club **610 (Excelsior)**: dispatch RNG(10)=4 -> 0x61A9A0. Role 15 is the
  sole populated zero-demand role. Volkan Kahraman (player 14011) is selected;
  best rating 56 consumes RNG(100)=55, passes the >=33 threshold, and leaves
  **0x31D39583** with Kahraman transfer-listed.
- club **140 (Darlington)**: dispatch RNG(10)=9 -> 0x4050F0. First attempt
  RNG(10)=1 uses the broad branch; RNG(30)=8 selects roster index 9,
  Martin Gray (player 2379). Rating 45 consumes RNG(100)=45, passes the >=25
  threshold, and leaves **0xF0AD5F37** with Gray transfer-listed.
- club **862 (FK Valmeira)**: dispatch RNG(10)=8 -> 0x4050F0. Attempt one
  RNG(10)=0 plus RNG(31)=23 selects roster index 24, Ainars Matvejevs; his
  rating-23 RNG(100)=22 fails. Attempt two RNG(10)=3 plus RNG(21)=5 selects
  roster index 16, Vitas Rimkus (player 18012); rating 38 then consumes
  RNG(100)=79 and passes. Rimkus is transfer-listed and the state becomes
  **0x7647CFCC**.

The next reverse visit is club **362**. Its mandatory dispatch RNG(10)=5 is
already consumed, leaving **0x1FE55F5F** and entering 0x61A9A0.


## Gate 11 corrected selector replay through club 166 — 28 September 2026

Continuing the corrected reverse order from club 862:

- club **362 (Gateshead)**: the already-consumed dispatch state was
  **0x1FE55F5F**. Positional selector chooses role 15 and **Mark Hine
  (player 2713, rating 33)**. RNG(100)=40 passes the >=25 threshold, Hine is
  transfer-listed, state **0xABE8BCA6**.
- club **757 (Bray Wanderers)**: dispatch RNG(10)=6 -> 0x61A9A0. Role 15
  selects **Paddy Geraghty (player 18406, rating 54)**. RNG(100)=9 fails the
  >=33 threshold, so no player is listed. State **0xFF61A050**.
- club **507 (1. FC Saarbrücken)**: dispatch RNG(10)=0 -> 0x61A9A0. Role 5
  selects **F. Weber (player 10721)**; his best-preferred rating is 55.
  RNG(100)=94 passes >=33, Weber is listed, state **0x6076B14A**.
- club **214 (Le Mans UC)**: dispatch RNG(10)=0 -> 0x61A9A0. Role 7 selects
  **David Charrieras (player 1889, rating 56)**. RNG(100)=49 passes >=33,
  Charrieras is listed, state **0x1931DA14**.
- club **611 (Dordrecht '90)**: dispatch RNG(10)=6 -> 0x61A9A0. Role 15
  selects **Arno Schaap (player 16244)**; best-preferred rating 49.
  RNG(100)=96 passes >=25, Schaap is listed, state **0x2130592E**.
- club **166 (KFC Verbroedering)**: dispatch RNG(10)=9 -> 0x4050F0. Random
  attempt 1 selects Rachid Yusuph (player 26981, rating 52), RNG(100)=17 fails.
  Attempt 2 selects Gudmunder Benediktsson (player 3748, rating 48), RNG(100)=18
  fails. Attempt 3 selects **Ljubica Nikolic (player 3759, rating 50)**,
  RNG(100)=94 passes. Nikolic is listed and the shared state becomes
  **0x458226E0**.

Exact continuation: reverse visit **club 867** from state **0x458226E0**.


## Gate 11 corrected selector replay through club 232 — 28 September 2026

The deterministic replay helper was regression-checked from the canonical
post-shuffle state through every hand-verified visit 805..166 and reproduced
all dispatch values, random roster indices, eligibility draws and shared CRT
states exactly.

A final-gate audit also closes the remaining fresh-loop retry concern:
`0x4042C0..0x4042CD` passes the club's current roster count as the first
argument to `0x4F32C0`, which stores it in embedded club-transfer byte +0x08.
Fresh +0x0C/+0x0E sell counters are zero. Therefore `0x403F10 -> 0x4F3330`
sees current roster count >= initial roster count - 4 and the zero counters,
so the final club predicate passes throughout this fresh transfer-list
population loop. It cannot create an unmodeled random-selector retry.

Continuing from **0x458226E0**:

- **867 FC Valga**: dispatch 1; Juri Pereverzev (15623), best rating 48,
  RNG(100)=25 passes; state **0x9405EC5A**.
- **698 Tomori Berat**: dispatch 6; Klodian Arberi (19281), best rating 49,
  RNG(100)=5 fails; no listing; state **0xCCF96DA4**.
- **399 Kareda Siauliai**: dispatch 9 -> random selector. First attempt
  branch RNG(10)=9 selects roster index 12, Irmantas Stumbrys (8799), rating
  52; RNG(100)=64 passes; state **0xA11011A8**.
- **68 AS Monaco**: dispatch 1; Marcelo Gallardo (10173), rating 76 passes
  with no rating RNG; state **0x969F09CB**.
- **209 Dinamo Zagreb**: dispatch 2; Robert Prosinecki (20345), rating 74
  passes with no rating RNG; state **0x98446D62**.
- **234 FC Porto**: dispatch 5; Ljubinko Drulovic (5054), rating 76 passes
  with no rating RNG; state **0xAC8D5E9D**.
- **779 Olimpia Balti**: dispatch 9 -> random selector. First attempt branch 3
  selects roster index 13, Nicolai Reaboi (17061), rating 46; RNG(100)=40
  passes; state **0x97342071**.
- **719 Spartak Varna**: dispatch 9 -> random selector. Attempt one branch 8
  selects roster index 28, Anto Valchanov (18449), rating 59; RNG(100)=29
  fails. Attempt two branch 1 selects roster index 16, Troian Diankov (15463),
  rating 57; RNG(100)=55 passes; state **0x03BB2D4E**.
- **1211 Siena**: dispatch 3; Omar Maffeis (26208), rating 56; RNG(100)=11
  fails; no listing; state **0x60EBD638**.
- **232 Benfica**: dispatch 5; - Lúis Carlos (6497), rating 66; RNG(100)=16
  fails the >=50 threshold; no listing; state **0x2C98D672**.

The corrected reverse-order prefix through the first 20 visits is therefore
closed. Next dependency: regenerate the remainder of the corrected 895-club
vector from the literal `0x668DA4` qsort plus the two exact Fisher-Yates
passes, then resume visit 21 from **0x2C98D672**.


## Gate 11 corrected selector replay visits 21-40 — 28 September 2026

The literal qsort implementation now regenerates the full 895-club vector. It
reproduces the corrected documented prefixes exactly and the two shuffle states
remain **0xC6B73181 -> 0xBD5CC00F**. Visits 21-40 replay as follows:

- 79 Hearts: Thomas Flögel fails RNG(100)=13; **0x20DD687C**.
- 742 Herfølge: Steven Lustü passes 74; **0xEE729AD6**.
- 775 Pietá Hotspurs: David Goodlip fails 17; **0xBFBDF000**.
- 624 RWD Molenbeek: Fabio Giuntini passes 48; **0x4554FE7A**.
- 409 Gornik Zabrze: Jacek Wisniewski passes 94; **0x1F9E10C4**.
- 118 Carlisle Utd: Steve Soley passes 33 on the corrected stream;
  **0x5675C55E**.
- 681 Joieries Aurum: Agustus Corominas passes 73; **0x5701AEC8**.
- 23 Eintracht Frankfurt: Alexander Rosen passes 51; **0xF117F382**.
- 179 Dundee U: random attempt one David Worrell fails 7; attempt two
  Anansasios Benstis passes 63; **0x37534713**.
- 67 FC Metz: random Arnaud Ribas fails 9, Farid Mondragón fails the 26-week
  residence gate without a rating draw, Nasredine Kraouche then passes 38;
  **0x8E9AC492**.
- 643 Elfsborg: random Andres Nicklasson passes 96; **0x5D58F2F6**.
- 514 KVK Tienen: random Ahmed Biga passes 88; **0xBFA0E09A**.
- 664 Panionios: Antonis Nikalaou passes 30; **0xF7A603E4**.
- 469 Rayo Vallecano: random David Clotet passes 27; **0xFA5F9BE8**.
- 131 Wrexham: Stephen Roberts fails 2; **0x633A49A2**.
- 761 Banga Gargzdai: Mindaugas Vijeikas passes 73; **0xB695F52C**.
- 355 Welling: Danny Chapman fails 15; **0xD8570D06**.
- 248 Partizan Tirana: Redi Jupi passes 69; **0xDE6973B0**.
- 662 Iraklis: random Alexander Brandic passes 93; **0x8959BB74**.
- 740 FC Copenhagen: Carsten Hemmingsen, best rating 67, passes RNG(100)=66;
  shared state **0x80A6458E**.

Exact continuation is canonical reverse visit 41 from **0x80A6458E**.


## Gate 11 bounded-RNG selector correction — 28 September 2026

Recovery generation 42 re-materialized the authorized canonical executable and
database and audited the newly committed transfer-list replay before continuing
visit 41.

A critical replay bug was found in the scratch helper used for the recent
qsort/selector checkpoints: it used `rand15 % bound` for bounded CRT values.
That is **not** FM2001's `0x64D540` behavior.

Direct disassembly of canonical `FOOTBAL.EXE` proves:

- `0x619DC0` calls `0x64D540` once for each descending Fisher-Yates
  bound;
- `0x61991F` calls the same `0x64D540` for every RNG(10) selector
  dispatch;
- `0x64D540` calls the MSVC CRT `rand()`, multiplies the 15-bit result by
  the supplied bound, multiplies by the embedded double **1/32768**, and
  truncates toward zero;
- therefore the exact bounded result is
  **`floor(rand15 * bound / 32768)`**, matching the already-implemented
  `MsvcCrtRng.randbelow()` in `reconstruction/match_schedule.py`.

The corrected instruction-level `0x668DA4` qsort itself remains valid. When
that qsort output is passed through the two exact **scaled** `0x619DC0`
shuffles from `0xDFCED283`, the shared states remain
**`0xC6B73181 -> 0xBD5CC00F`** because those checkpoints depend on draw
count, not bounded outputs. The resulting element order is different from the
modulo replay:

```text
twice-shuffled prefix:
25, 738, 783, 262, 812, 2, 397, 819, 626, 146, ...

reverse 0x61991F prefix:
118, 750, 510, 1216, 430, 622, 877, 243, 404, 500, ...
```

This restores the earlier club-118 prefix, but the earlier hand replay also
used modulo for nested bounded values and therefore is not canonical evidence.
For visit 1, scaled RNG(10) still returns 3 and selects the positional path for
Carlisle. Steve Soley remains the source-backed candidate; the subsequent
scaled RNG(100) is **82**, not 88, still passes the <=50 rating threshold, and
leaves shared state **`0x6A346701`** after the same two raw CRT draws.

All recently committed modulo-derived visit sequences beginning club 805 and
their visit-1..40 selector outcomes are superseded. Exact continuation is
canonical reverse visit **2, club 750**, from **`0x6A346701`**, using
scaled `0x64D540` bounded draws throughout.


## Gate 11 scaled selector replay verified through visit 40 — 28 September 2026

The selector helper was rebuilt against the canonical source after the
`0x64D540` bounded-RNG correction and given an independent regression check
before advancing the shared stream.

The validation is deliberately stronger than comparing one or two selected
players. With every selector mechanic held fixed but the bounded mapping
temporarily switched back to the erroneous `rand15 % bound`, the rebuilt
helper reproduces **all 40** superseded modulo-derived reverse visits and
**all 40** previously committed raw CRT end states exactly. That includes the
positional and random selector branches, roster-index draws, eligibility
failures, no-rating-RNG paths, and multi-attempt random selections. This
isolates the prior discrepancy to the bounded-RNG mapping itself; the rebuilt
selector mechanics agree with the earlier instruction-level audits.

Returning to FM2001's real scaled `0x64D540`, canonical reverse visits 1-40
are:

```text
 1  118 Carlisle Utd           -> 0x6A346701  Steve Soley
 2  750 Dunaferr               -> 0x7B490815  Goran Mosanovic
 3  510 Rot-Weiß Essen         -> 0xF0AD5F37  O. Skok
 4 1216 Panahaiki              -> 0x0C123F69  no listing
 5  430 Carmarthen Town        -> 0x7302C488  no listing
 6  622 KSC Lokeren            -> 0x86F7B742  no listing
 7  877 Trisen                 -> 0xABE8BCA6  Dieter Krainz
 8  243 Ajax                   -> 0x047A80D1  - Dani
 9  404 Coleraine              -> 0x79B832E5  Simon Smyth
10  500 Babelsberg             -> 0x80BA6087  no listing
11  717 Lokomotiv Sofia        -> 0x7FCFCB39  Sasha Angelov
12  597 Emmen                  -> 0x145D6118  no listing
13  616 KSC Eendracht Aalst    -> 0x3081B852  Christophe Kestens
14  842 Rostel'mash            -> 0x1850595C  no listing
15  413 Petrolul Ploiesti      -> 0x4FD812B6  Octavian Grigore
16   89 Crystal Palace         -> 0x458226E0  Steve Thomson
17  822 Newtown                -> 0x9405EC5A  no listing
18  804 SCP Ruzomberok         -> 0xCCF96DA4  Rastislav Zihlavnik
19  484 FC St Pauli Am.        -> 0xD8E7093E  M. Niemann
20    1 Aston Villa            -> 0x651BA9FF  Daniel West
21  470 Sevilla F.C.           -> 0x97342071  no listing
22  215 FC Lorient             -> 0x60EBD638  Laurent Bourmaud
23  818 Young Boys Berne       -> 0x2C98D672  Andre Allenbach
24  680 Zeljenicar Sarajevo    -> 0x20DD687C  - Zeric
25  213 Stade Lavallois        -> 0xEE729AD6  Anthony Braizat
26  165 Hertha BSC Berlin      -> 0x4554FE7A  Michael Hartmann
27   23 Eintracht Frankfurt    -> 0x1F9E10C4  no listing
28  237 Lierse SK              -> 0x5675C55E  Luc Struyven
29  630 KV Mechelen            -> 0x5701AEC8  Gunther Vets
30  144 Gillingham             -> 0xD8E3EE0C  James Pinnock
31  549 Barcelona B            -> 0x96AFCCE6  no listing
32  556 Dortmund Amateure      -> 0x5DFB3290  T. Stock
33  780 Nistru Otaci           -> 0x4E46D58A  Nikolai Kapusteanschi
34  496 Elgin City             -> 0xC71FD16E  H. Berg
35  145 Hartlepool Utd         -> 0xD1A29B58  Graeme Lee
36  173 SG Wattenscheid 09     -> 0x8E9AC492  no listing
37  103 Southend Utd           -> 0xE32BC79C  Scott Houghton
38  803 MSK Zilina             -> 0x5D58F2F6  Branislav Labant
39  538 Litex Lovech           -> 0xBFA0E09A  Koicho Ivanov
40  620 Germinal Beerschot     -> 0x1EBAE4F5  no listing
```

Selected instruction-sensitive examples on the corrected stream:

- visit 2 Dunaferr dispatches scaled RNG(10)=7 into `0x4050F0`; its first
  random attempt selects Goran Mosanovic and the rating-49 scaled RNG(100)=96
  passes, leaving **`0x7B490815`**;
- visit 3 Rot-Weiß Essen dispatches 0 into `0x61A9A0`, selects O. Skok,
  and rating 55 passes scaled RNG(100)=88, leaving
  **`0xF0AD5F37`**;
- visit 5 Carmarthen consumes only its dispatch because effective roster count
  16 equals the AccessFanBase threshold 16;
- visit 8 Ajax lists Dani with best rating 81 and therefore consumes no
  rating RNG;
- visit 20 Aston Villa's random selector rejects Mark Draper on the first
  attempt and accepts Daniel West on the second, closing the first twenty at
  **`0x651BA9FF`**.

As an additional sanity run, the exact same scaled helper traverses all
**894** bounded club visits without reaching an unmodeled selector branch.
That full run currently ends at raw CRT state **`0x126CF137`** with 625
players listed. Treat that final state as a **provisional full-run
checkpoint**, not yet the next canonical boundary: the replay helper itself
must be made durable/reproducible and the later prefix should be checkpointed
before the state is carried into loan maintenance.

Exact durable continuation: reverse visit **41, club 742 (Herfølge)** from
shared state **`0x1EBAE4F5`**.


## Gate 11 full fresh transfer-list population replay locked — 28 September 2026

The exact replay helper is now durable in
`tools/replay_gate11_transfer_list.py` rather than existing only in chat
scratch state.

The committed Git blob SHA is:

```text
c5fd82d7eef72841c87a8d67b14d9df0eb5f9f7f
```

A byte-for-byte Git-blob hash of the locally executed helper is identical.
Before commit, that exact file passed three source-backed runs against the
authorized canonical FM2001 database:

```text
scaled, visits 1-40, prefix validation:
  state_after = 0x1EBAE4F5
  listed = 28

diagnostic modulo, visits 1-40, prefix validation:
  state_after = 0x80A6458E
  listed = 32

scaled, complete 894 visits, prefix validation:
  state_after = 0x126CF137
  listed = 625
```

The diagnostic modulo mode is intentionally retained only as a regression
oracle for the superseded scratch trace. Normal/default replay uses the exact
`0x64D540 = floor(rand15 * bound / 32768)` mapping.

Because the source-driven helper is now persisted and reproduces both the
known corrected scaled prefix and all 40 historical modulo checkpoints under
the diagnostic mapping, the complete scaled result is promoted from
provisional to the canonical **post-`0x61991F` fresh transfer-list
population boundary**:

- reverse club visits: **894**;
- players newly transfer-listed: **625**;
- shared CRT state after visit 894: **`0x126CF137`**.

The final visit is club **Stavoartikl Brno**. Its positional selector reaches
Jan Polak, best-preferred rating 60; scaled RNG(100)=14 fails the >=33
threshold and the loop exits at **`0x126CF137`**.

Exact next dependency: continue the same shared CRT stream from
**`0x126CF137`** through the loan-maintenance remainder of `0x6194D0`,
then into `0x425680 -> 0x4D1760` fixed-support-staff initialization. Do not
attach live Saturday training until that startup quality bridge is complete.


## Gate 11 post-transfer loan-list tail mapped — 28 September 2026

Recovery generation 43 resumed from the canonical post-transfer-list boundary
**0x126CF137** and re-materialized the authorized FM2001 disc archive. The root
`FOOTBAL.EXE` was re-extracted and SHA-256 reverified as
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3` before
new disassembly evidence was accepted.

The remainder of `0x6194D0` after `0x61991F` is now bounded as the original
**loan-list** maintenance system rather than an unspecified transfer tail:

- tuning-loader target `0x821618` is fed by the literal key
  `MAX_PLAYERS_ON_LOAN_LIST`; its shipped executable default is **200**;
- the post-loop phase clears the shared candidate count and scans clubs/players;
- the user-controlled-club path reaches a bounded `RNG(200)` gate only for
  players not already carrying status bit 12 and not currently selected or
  substitute-active for that club;
- non-user eligible clubs call `0x618F80`, whose candidate append path requires
  player status **bit 12** before reaching its later eligibility checks;
- after sorting, the same club-vector machinery is handed to `0x619EB0`, which
  uses the separate `MAX_LOANS_PER_WEEK` limit and `0x61ABF0 -> 0x41AAE0`
  loan-selection/execution path;
- the later reverse-club population loop stops when the shared loan-list count
  reaches `MAX_PLAYERS_ON_LOAN_LIST`; successful selectors set player status
  **bit 12 (0x1000)** and increment club `+0x1A8`.

Fresh source state also resolves the first candidate scan enough to advance the
RNG ledger. Fresh players have no status bit 12, no injury/loan state, and the
pre-match selected/substitute bits tested by `0x417EE0/0x417F00` are clear.
Therefore Arsenal's 37-player user roster consumes exactly **37 RNG(200)**
draws from `0x126CF137`. Exactly one draw is below 5: zero-based roster entry
12, **Matthew Upson (player 1422)**, with draw value 4. The state after those
37 draws is **0x1AB5D762**. Non-user `0x618F80` scans append no source-fresh
bit-12 players on this boundary and consume no RNG before their bit-12 gate.

Exact next dependency: replay the two `0x619EB0` loan passes and the final
reverse-club loan-list population from **0x1AB5D762**, preserving the already
materialized transfer-list bit-8 mutations, then carry the resulting shared CRT
state into `0x425680 -> 0x4D1760` fixed-support-staff creation.


## Gate 11 first two loan passes replayed — 28 September 2026

Continuing the exact post-transfer loan-list stream from the prior
**0x1AB5D762** checkpoint closes both calls to `0x619EB0` before the final
reverse-club loan-list population.

### First 0x619EB0 pass

The first pass Fisher-Yates shuffles the canonical 895-club vector with exactly
894 scaled bounded draws and leaves **0x8B83FB28**. The shuffled vector begins
club 777. This call's mode flag is 1; the executable's early live-vs-cached club
value test exits the function immediately for the neutral first club, so this
pass consumes no nested selector RNG after its shuffle.

### Second 0x619EB0 pass

The second pass reshuffles the same vector with another 894 scaled draws and
leaves **0xB609BA3E**. Its club prefix begins:

`862, 481, 317, 256, 373, 1240, 233, 107, ...`

The one-player candidate array still contains Arsenal defender **Matthew Upson
(player 1422)**. The first seven destinations reject him deterministically
before a selector draw. Club **107 Watford** is the first destination to clear
the domestic/competition and club gates.

Upson's exact preferred-role rating is **65**. Watford's source-backed
AccessFanBase/competition inputs produce the exact `0x405590` acceptance band
**42..66**, so rating 65 passes. The next `RNG(10)` is **2**, advancing the
shared CRT state to **0xA23BE809**. Because it is below 3, `0x61ABF0` removes
Upson from the shared candidate array and returns him.

The handoff `0x41AAE0(Upson, Watford)` detects that Upson belongs to the
user-controlled club and routes to the loan-proposal/event path rather than
immediately assigning the temporary club. That path consumes one `RNG(5)`;
its result is **2**, leaving **0xBB304AA8**.

The shared loan-candidate array is now empty. Exact continuation is therefore
the final reverse-club loan-list population loop from **0xBB304AA8**. This
loop sets player status bit 12 for accepted candidates until it exhausts the
club traversal or reaches the shipped **MAX_PLAYERS_ON_LOAN_LIST = 200** cap.


## Gate 11 loan-list cap and fixed-support-staff replay checkpoint — 28 September 2026

Commit `70068a0f509f7ab00d3bfea32ea298826e95246c` extends the durable source-backed replay helper through the remainder of the fresh `0x6194D0` loan-list maintenance and into `0x425680 -> 0x4D1760` fixed-support-staff creation.

The canonical fresh path now reproduces these shared CRT boundaries:

- post-transfer-list population: **`0x126CF137`**;
- after Arsenal's 37 RNG(200) loan-candidate scan: **`0x1AB5D762`**;
- after first 895-club loan shuffle: **`0x8B83FB28`**;
- after second 895-club loan shuffle: **`0xB609BA3E`**;
- after Watford selects Matthew Upson and the user-loan proposal timing draw: **`0xBB304AA8`**;
- final reverse-club loan-list population reaches the shipped **200-player cap** after **292 eligible club visits**, ending on club **866** at **`0x472F4DFF`**;
- the one pre-staff RNG(10) in `0x425680` returns 2 and leaves **`0xA54D70C6`**;
- six fixed support-staff records of types **1, 2, 3, 4, 5, 13** each consume RNG(25) for age and RNG(2) for rating;
- the fresh Youth Team Coach (type 3) receives rating **1**;
- the shared CRT state after fixed-support-staff creation is **`0x418CAA72`**.

This closes the startup-quality bridge through the staff rating needed by the already-recovered active-training multiplier. The exact next dependency is to trace any mandatory shared-RNG consumers after `0x4D1760` and before the first Saturday `0x4EACE0` training execution. Do not attach live Saturday training until that remaining interval is proven RNG-clean or replayed exactly.


## Gate 11 pre-staff selector correction — 28 September 2026

A direct re-audit of canonical `FOOTBAL.EXE`
(`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`)
found that the prior `0x425680 -> 0x4D1760` replay omitted the mandatory
`0x5E3FD0` call immediately before fixed support-staff creation.

Instruction-level `0x5E3FD0` behavior on the fresh empty list:

- it repeatedly consumes exact scaled `RNG(37)`;
- factory `0x5E2710` covers all 37 selector values;
- all fresh factory products leave dword `+0x0C != 1` and status bit
  `+0x08 & 1 == 0`, so neither the duplicate-key path nor status rejection
  can fire;
- the only possible retry is drawing the immediately previous accepted selector;
- the canonical stream from **`0xA54D70C6`** accepts
  **33, 8, 12, 22, 2, 3, 27, 5, 0, 23, 28, 18** in exactly 12 draws, with no
  retry, and leaves **`0x418CAA72`**.

Therefore the 12 draws previously attributed to the six fixed staff were
mis-labeled. Fixed staff starts at `0x418CAA72` and yields:

```text
type 1:  RNG(25)=4,  RNG(2)=0 -> rating 1, state 0x9B8FDC7C
type 2:  RNG(25)=23, RNG(2)=1 -> rating 2, state 0xEDD8AED6
type 3:  RNG(25)=15, RNG(2)=1 -> rating 2, state 0xE274A400
type 4:  RNG(25)=12, RNG(2)=1 -> rating 2, state 0xE6E1527A
type 5:  RNG(25)=5,  RNG(2)=1 -> rating 2, state 0x7FAD04C4
type 13: RNG(25)=0,  RNG(2)=1 -> rating 2, state 0xFA1C595E
```

The corrected fresh Youth Team Coach rating is **2**, so with no fresh Training
Centre the source-backed training quality is **1.30**. The true post-fixed-staff
shared CRT state is **`0xFA1C595E`**. The previously committed claim that
`0x418CAA72` was post-fixed-staff and implied Youth Team Coach rating 1 /
quality 1.25 is superseded.

`tools/replay_gate11_transfer_list.py --loan-tail` now includes the missing
selector, asserts its exact sequence/state, and asserts the corrected fixed-staff
ratings and final state.

## Gate 11 post-fixed-staff interval proven RNG-bearing — 28 September 2026

Recovery generation 48 re-materialized the authorized FM2001 disc archive and
reverified root `FOOTBAL.EXE` as
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`
before accepting new instruction-level evidence.

The active dependency after corrected fixed-staff state **`0xFA1C595E`** is
now structurally bounded:

- `0x4A8070` dispatches existing DBRUsers through
  `0x4138E0 -> 0x42A9E0` before its Saturday `0x6194D0` pass;
- the pending/new DBRUser does not reach `0x425680` until later in that same
  `0x4A8070` routine;
- `0x425680` materializes the user's 40 training records through
  `0x61C9C0` only after `0x4D1760`;
- therefore the already-replayed startup Saturday `0x6194D0` work happens
  before active user training exists and is already outside the remaining
  bridge;
- on subsequent dates, `0x42A9E0` runs concession/sponsor timer updates and
  `0x61CA60` daily training-record maintenance before its Saturday
  `0x42AE40 -> 0x61CBA0 -> 0x61C520 -> 0x4EACE0` call;
- the containing `0x4A8070` does not reach the next global Saturday
  `0x6194D0` until after the DBRUser dispatcher returns.

The bridge is therefore definitively **not RNG-clean**. Fresh zero-wait
concession/sponsor scheduling reaches bounded CRT draws, and active
`0x61CA60 -> 0x61C6C0 -> 0x61C580` training maintenance consumes shared
RNG before the first weekly training transition.

Commit `6c591da42026ffe09310d23bae621e7aed2080f9` preserves the detailed
call-order evidence in `research/EXECUTABLE_ANALYSIS.md`.

Exact next task: close fresh-state branch conditions and tuning bounds inside
the intervening daily maintenance, replay every mandatory draw from
**`0xFA1C595E`** to the first `0x4EACE0` entry, and only then attach the
already-verified quality-1.30 weekly training primitive to calendar progression.



## Gate 11 exact pre-first-training RNG replay closed — 28 September 2026

Commit `45d03793b95e45f56e54802f4aa059a45c2a61d2` closes the mandatory
fresh daily RNG interval between corrected post-fixed-staff state
**`0xFA1C595E`** and the first active Saturday `0x4EACE0` entry.

Canonical executable evidence now fixes:

- first concession wait: `RNG(14)=4` -> **11 days**, state
  **`0xA5A88AA9`**;
- first no-sponsor wait: `RNG(7)=6` -> **13 days**, state
  **`0x73FCE2C8`**;
- neither timer repeats before first training Saturday;
- Arsenal has **37 active** fresh training records;
- all 37 take the same fresh `0x61C580` daily recovery branch, starting
  Condition **80** and threshold **50**;
- `0x41B7B0` is false for all 37 on this boundary, so the later 60-percent
  side branch does not consume RNG;
- fresh training `+0x99 = 0`, so the post-recovery event branch is skipped;
- seven daily recovery passes consume exact draw counts
  **111, 111, 111, 111, 111, 126, 142** and end at
  **`0x216C6081`**;
- final fresh Condition range is **86..93**, sum **3342**.

The remaining same-day calls before the weekly test were audited RNG-clean or
fresh-empty. In particular DBRUser construction initializes
`[user+0x6BC object +0x1800] = 0`, making `0x61D710` a no-op here.

Data-free replay helper `tools/replay_gate11_training_bridge.py` was added in
commit `169784d0e9be50571d32f27b135ed3c7bfd4e944` and locally asserted every
checkpoint above.

The startup-quality/RNG bridge is therefore closed. Exact next implementation
task: attach the already-verified weekly training primitive to normal Saturday
calendar progression with the source-backed fresh quality **1.30**, while also
preserving the recovered daily Condition-maintenance RNG ordering that now
precedes it.


## Gate 11 daily/weekly training runtime primitives — 28 September 2026

The closed pre-first-training RNG bridge is now represented by reusable runtime
primitives without prematurely wiring unresolved later-week commercial RNG into
normal calendar progression.

Implementation checkpoints:

- `7ec8d3dd935fda7f4dff75de9a84c03b7c4967aa` adds
  `RuntimePlayer.run_daily_training_condition_recovery`, reproducing the
  exact three-iteration `0x61C580` Condition-recovery RNG core with an
  explicit source-backed threshold;
- `82ee9ad492bd42f2c02f296810e0ba1a779c0aa1` adds deterministic tests for
  fresh recovery, the >90 two-stage extra-draw branch, and injured-player
  zero-draw exclusion;
- `6c863a039b8570b425bd550240135afee8c3b3b2` adds explicit GameState
  orchestration for controlled-club daily recovery, Saturday primary training,
  and their proven daily-before-weekly order using one caller-supplied shared
  RNG;
- `6809b70f0a77fcd4e87d6fe80ac139de25ea0141` adds GameState ordering tests.

The five new training tests all report **ok** in GitHub Actions. Repository
asset-policy validation also passed.

The complete reconstruction run at `6809b70f` executed **574 tests** but
finished with two failures in existing secondary-schedule assertions:

- secondary root order expected competition 181 before 170, while current code
  returns 170 before 181;
- secondary bucket-count test expects 262 nodes while current materialization
  returns 280.

Neither failing assertion is in the new training code. No reconstruction run
exists on the immediately preceding research-only checkpoints, so this note does
not claim when those scheduler expectations first became stale.

Automatic recurring calendar training remains intentionally disabled. The first
concession timer expires after 11 days, before the second active training
Saturday, and its `0x5E5330` expiry path contains nested RNG through
`0x5E5170` / `0x5E5230`. Exact next dependency: replay that first
concession expiry (and the no-sponsor expiry at day 13) on the shared stream
before claiming multi-week calendar RNG fidelity.


## Gate 11 calendar-integrated user training checkpoint — 28 September 2026

Normal GameState day progression now has an opt-in source-backed training hook.

- `b62665d8ccc3245426c636e210409f06b02c543f` adds
  `configure_user_training_calendar()` and calls configured DBRUser training
  maintenance from `GameState.advance_one_day()` after calendar post-fixture
  maintenance and before later global transfer/payroll/AI-transfer maintenance.
- The hook preserves the proven original order: daily `0x61CA60/0x61C580`
  recovery first, then Saturday `0x42AE40 -> 0x4EACE0`.
- Training remains disabled unless recovery threshold and quality are explicitly
  configured. This avoids silently inventing staff/facility/commercial scheduler
  state outside the already-source-backed interval.
- `ddab924af5fc336db74dc08d3c154a7334b6b0e0` adds regressions proving
  Saturday calendar progression consumes the same 6-daily + 12-weekly draws for
  two synthetic Fitness players as the explicit orchestration primitive, while
  an unconfigured day consumes no training RNG.

GitHub Actions at `ddab924a`:
- repository asset policy: **passed**;
- both new calendar-training tests: **passed**;
- full reconstruction suite: **576 tests run, 2 failures**, both the same
  pre-existing secondary-schedule assertions already recorded at `6809b70f`
  (secondary root order and 262-vs-280 secondary bucket count).

No new Gate-11 training failure was introduced.

The next dependency is the commercial/event RNG interleaving already mapped
through the third training Saturday in commit
`6822e7ea666749ba01ef0245ba858da009a420e4`. Materialize only the minimum
fresh concession/sponsor timer state needed to preserve those shared-RNG
checkpoints before enabling recurring multi-week training by default.


## Gate 11 commercial replay correction — 28 September 2026

Direct executable re-audit supersedes the multi-week states from
`6822e7ea666749ba01ef0245ba858da009a420e4`.

The Arsenal `0x65DBC0` selector capacities remain source-backed as
`0,16,0,20,0,12,0,14`, but `0x5E5330` tests that return value before
calling either `0x5E5170` or `0x5E5230`. Zero-capacity selectors therefore
consume no RNG.

Corrected replay:
- day 11 concession: **104 draws**, no success, state **0x2D3FF8E7**;
- day 11 recovery: **182 draws**, state **0xD4E2341D**;
- day 12 concession: **53 draws**, selector 3 / candidate 19 succeeds,
  state **0x03CA80A0**;
- day 12 recovery: **191 draws**, state **0x50CB6921**;
- day 13 concession wait: RNG(14)=8 -> 15 days, state **0x51142760**;
- day 14 sponsor wait: RNG(7)=1 -> 8 days, state **0x9533F463**;
- second weekly pre/post: **0x509630B6 -> 0xA3C5013C**;
- third weekly pre/post: **0x7B8D5F58 -> 0xE176B24E**.

Durable replay: `tools/replay_gate11_commercial_training.py`.

The earlier day-11 208-draw, day-12 188-draw and second/third-Saturday states
from `6822e7ea` are historical and must not be resumed.

Commercial runtime work now has:
- source-backed wait/reset state in `commercial_timers.py`;
- generic 25-rule candidate selection in `concession_offer.py`;
- corrected canonical selector regressions.


## Gate 11 live commercial-before-training integration — 28 September 2026

The corrected commercial mechanics are now connected to normal GameState day
progression without Arsenal-specific production constants.

Implementation:
- `ba7119876b489e0b7b300da22ba67e802e97338a` exposes the serialized
  `Buildings.dat +0x1C` concession-capacity field, exact eight
  `0x65DBC0` section ranges, bit-0x08 selector exclusion, and `0x65DB70`
  all-section denominator through `StadiumSourceState`;
- `86108af55487b147964eff6e94a4c20392db31ee` tests those stadium helpers;
- `90e789a4daf08a75d0ce5719b5e44f554855ef51` integrates
  `UserCommercialTimerState` into GameState and consumes live club
  `+0x1C`, AccessFanBase `+0x08`, stadium selector capacities,
  `RNG(800)`, `RNG(25)`, candidate-local RNG, and final `RNG(3)`;
- normal `advance_one_day()` now preserves the original DBRUser order:
  commercial timing/offer selection **before** daily recovery and Saturday
  active training;
- `4c560cb30f5ba7301c005bd39a83de346f75971d` fixes and verifies the
  synthetic ordering regression.

GitHub Actions at `4c560cb3`:
- repository asset policy: **passed**;
- commercial-before-training ordering regression: **passed**;
- full reconstruction suite: **585 tests run, 2 failures**, both unchanged
  pre-existing secondary-schedule assertions (root order and 262-vs-280 bucket
  count).

The first three-week fresh Arsenal commercial/training stream is therefore
represented by reusable production primitives. The next commercial dependency
for longer exact progression is the sponsor-offer body behind `0x617C80`;
the current timer model intentionally preserves only the already-proven
no-sponsor wait/reset behavior.


## Gate 11 training/commercial slice reload-safe; sponsor timer closed — 28 September 2026

Direct `0x617C80` disassembly proves the sponsor routine contains no hidden
offer-selection body. It only chooses the sponsor-present/no-sponsor wait range,
draws one wait when its timer is zero, and resets timer/date without RNG at
expiry. The existing commercial timer model therefore covers its shared-RNG
behavior for the modeled sponsor-presence mode.

The live Gate-11 calendar state is now reload-safe:
- `efb6043d61cc68d72016b05a2ede07c6a961c09e` adds a compact
  eight-selector concession source snapshot;
- `024a3c027c76cea14a6a5ea6dcdd06523acf5b98` decouples concession RNG
  from retaining original stadium assets after configuration;
- `939b89b92bd6668cedcf21c3cbfcda88b51d37fd` bumps internal save schema
  to **14** and persists training recovery/quality, concession/sponsor timer
  progress, and the compact concession source inputs;
- `6f2c66caa66fac773a16d3ad9cd94daa42d98293` verifies round-trip state;
- `c7650cf3723664ca5d1fcaf5cbde089240a12892` verifies commercial RNG
  still precedes training after the source-snapshot refactor.

GitHub Actions at `c7650cf3`:
- asset policy: **passed**;
- new Gate-11 tests: **passed**;
- full suite: **586 tests run, 2 failures**, both unchanged pre-existing
  secondary-schedule assertions.

The training/commercial management slice is now sufficiently integrated to move
to the next Gate-11 workflow. Scouting is next because the executable already
has a bounded `PScouting2K -> 0x4AE970 -> 0x4AF7F0` deterministic reseed and
candidate-shuffle path.


## Gate 11 scouting filter/reseed checkpoint — 28 September 2026

Commit `9c0087dbff23890a8a511ed9315a3511f11fafd3` starts the scouting
workflow audit from the canonical `PScouting2K` path instead of inventing a
generic search UI.

Verified directly from canonical `FOOTBAL.EXE`:

- `0x4AE970` walks the full player table and calls `0x4AE680` once per
  player; the returned boolean is stored at player `+0x228`;
- only players marked 1 become the primary temporary result vector;
- the predicate excludes the controlled club's registered/current players,
  then applies source-backed panel selectors, age bounds, valuation bounds,
  a four-way player classification selector, an optional list predicate,
  a threshold gate, and three exact status toggles;
- those final toggles correspond to player status bits 8, 7 and 12, with bit 12
  additionally requiring `0x41E450(player, active_user_club) == 1`;
- if none of the three status toggles is active, this final status block passes
  unconditionally;
- `0x4AF7F0` XOR-hashes three control bytes, two integerized double fields,
  five dword panel fields and its caller argument, then passes the result
  directly to CRT `srand`;
- the primary call uses argument **-1**, followed immediately by exact
  descending Fisher-Yates through `0x64D540`.

This proves that identical scouting panel state produces deterministic result
ordering independent of the incoming global gameplay RNG state.

Exact next task: finish `0x4AEAE0` secondary score construction and the
`0x4AEEA0/0x4AF330` result-mode dispatch before implementing a clean-room
human scouting action.


## Gate 11 deterministic scouting core verified — 28 September 2026

The first clean-room scouting primitive is now regression-tested.

Implementation:
- `c0dc94ff268e96a2cb3ba0765eccea5a71ef23c7` adds the exact
  `0x4AF7F0` panel-state XOR seed, CRT reseed and descending Fisher-Yates
  result shuffle plus source-backed shortlist caps;
- `c80e3d2401171fb40b143e98a36f43c43536b626` fixes the test module to
  the repository's `unittest` discovery convention.

GitHub Actions at `c80e3d24`:
- repository asset policy: **passed**;
- all four new scouting tests: **passed**;
- full reconstruction suite: **590 tests run, 2 failures**, both the same
  pre-existing secondary-schedule assertions already recorded before scouting
  (secondary root order and 262-vs-280 secondary bucket count).

The verified scouting core now covers deterministic primary ordering and the
secondary 50-candidate / 20-result cap-and-shuffle stage without assigning
unsupported UI labels to neutral panel controls.

Exact next task: finish the six `0x4AEEA0` result-sort semantics and tie
scouting panel fields to original UI labels/control strings where source-backed,
then expose the minimum human scouting action over existing RuntimePlayer state.


## Gate 11 scouting sort modes closed — 28 September 2026

Direct `0x4AEEA0` disassembly closes the six result-list qsort modes:

- mode 0: ascending player name (`+0x0C` string, then `+0x08`);
- mode 1: ascending age via `0x4173B0`, then name;
- mode 2: descending `0x41FB60` average of the active six-byte
  `+0x79..+0x7E` circular history, then name;
- mode 3: descending preferred-position display string from
  `player+0x248 -> 0x4EA800`, then name;
- mode 4: ascending club display name via `0x40DA70`, then name;
- mode 5: descending player value via `0x420570`, then name.

The original English string table contains exact scouting/list labels
`Name`, `Age`, `Position`, `Club`, and `Value`, matching modes
0/1/3/4/5. The mode-2 user-facing label remains deliberately neutral because
both `Form` and `Performance` exist in the original resources and a direct
control binding has not yet been proven.

Implementation commits:
- `69882a753c32b10bc6313ea4a59c749e45d3ba3b` adds the neutral exact
  six-mode comparator/sort primitive;
- `e00c62361d43f803e8135ca8faa370c75ecde14a` adds direction/tie tests.

Asset-policy CI at `e00c6236` passed; the reconstruction workflow was still
running when this checkpoint was written.

Exact next task: expose the minimum UI-independent human scouting search action
over existing RuntimePlayer state using the already-mapped filter, deterministic
reseed/shuffle, score/shortlist path and result sorting. Keep unresolved panel
controls and the mode-2 display label neutral rather than inventing semantics.


## Gate 11 human scouting action verified — 28 September 2026

The recovered result pipeline is now exposed as a backend human-manager action
without assigning unsupported UI semantics.

Implementation:
- `07645d340447b2fc20ae840ecb227ec7d77ad863` composes first-stage
  filtered candidates, deterministic primary reseed/shuffle, optional
  `0x4AEAE0` score/shortlist/reseed stage and final `0x4AEEA0` sorting;
- `bee6b6caebefaa8e108092bd2774729922b6ea14` regression-tests that
  exact stage order;
- `42c251c4c20f43982fdec69b9bf1eff3fbba142c` exposes
  `HumanGameplayController.search_scouting_players()` over RuntimePlayer
  state;
- `a859299f093a18517fde256f64fe20d1813c4ebb` verifies controlled-club
  exclusion, runtime secondary scoring, and strict resolver requirements for
  still-unmaterialized sort inputs.

The controller does not substitute `form_state` for `0x41FB60` and does
not invent the preferred-position display formatter or a post-appearance
valuation history. Those values are required explicitly only for sort modes
that consume them.

GitHub Actions at `a859299f`:
- asset policy: **passed**;
- all new scouting and human-scouting tests: **passed**;
- full reconstruction suite: **601 tests run, 2 failures**, both unchanged
  pre-existing secondary-schedule assertions.

Exact next task: move source-backed parts of `0x4AE680` into a reusable
RuntimePlayer/GameState predicate, including age/value/class and known status
gates. Keep status bit 7 and other unresolved panel selectors neutral until
their original labels/semantics are proven.


## Gate 11 mapped scouting first-stage filter verified — 28 September 2026

The source-backed portion of `0x4AE680` is now reusable in the runtime.

Implementation checkpoints:
- `7e7eb2f5577a3c17f856739b0b0d4ea15c20caac` adds exact inclusive
  age/value gates, mode-15 age 15..18 clamp, class mapping and status-control OR
  semantics;
- `bc7ab3de36bcfbda746fbb4f1fa8103d62bee1cc` adds focused first-stage
  tests;
- `a04cf1970dd699e2b39e5cdaa543d2bdf47370b7` corrects live
  `0x4205F0` valuation input ownership: preferred-position-0 class,
  temporary/current-club division and registered-club country;
- `868118ef4eb42dd9d01f35dd71ba8371f8a18ce7` regression-locks those
  valuation distinctions;
- `056cfc2b0c364b5a00cce646f81509c1efa83543` integrates the mapped
  filter into the human scouting action;
- `2b2ff90638f63196966ee2f8feae69d00b4f7c42` adds mapped-action tests;
- `3723512b7aa2e31203785e75fa967ad880f0990e` corrects the exact
  out-of-range class-selector behavior: values outside 0..3 bypass the class
  gate;
- `e414455e32d9d06fa00fd4fcad38a22d8aa3cb82` preserves the executable
  team-selector-before-later-metadata gate order;
- `664eb6abbaf5b609bad54b5cda37729ff1971cf7` regression-tests the
  selector-bypass edge case.

GitHub Actions at `664eb6ab`:
- asset policy: **passed**;
- full reconstruction suite: **610 tests run, 2 failures**;
- all new scouting, mapped-human-scouting and valuation tests passed;
- the only failures are the same two pre-existing secondary-schedule
  assertions.

The remaining scouting filter inputs are now narrow: the neutral team/context
selector, optional preferred-position selector, global threshold gate, status
bit 7 meaning/state, and the bit-12 + `0x41E450` loan-list condition. Exact
next task is to resolve/materialize those where direct executable/UI evidence
permits, without inventing labels.


## Gate 11 scouting country/position/threshold and loan-eligibility checkpoint — 28 September 2026

Commit `7b106a777c5d194045bb2bfe02835d632701fafe` resolves three
previously neutral `0x4AE680` gates from canonical `FOOTBAL.EXE`:

- `0x4AE610` resolves a DBRCountry context from the player's registered
  club country when club context exists, otherwise from the player's
  nationality/country source;
- panel `+0x64E0` selects same-country, different-country with
  country `+0x18 != 0`, or different-country with `+0x18 == 0`;
- the optional selector at `+0x761C/+0x766C` is exactly membership in the
  player's three preferred-position IDs through `0x4EA410`;
- the global threshold at `0x8223F4` is loaded from the literal tuning key
  **ScoutStrengthMin**;
- the compared auxiliary value is
  `floor((30 * byte + 128) / 255)` from
  `[0x876868 + player + 0x1D]`.

Follow-up instruction tracing closes the exact `0x41E450` shape used by the
scouting bit-12 control. `0x41B490` proves player status bit 11 is the already
mapped **Non-EU** state, and `0x405500` proves club `+0x10` is the
competition/division ID source.

Because scouting calls `0x41E450` only after confirming status bit 12
(the recovered loan-list state), its bit-4/not-bit-12 rejection cannot fire on
this path. The scouting-specific eligibility therefore reduces to:

- if transfer-listed bit 8 is also set: require the player's registered club
  competition ID to differ from the active user's club competition ID;
- otherwise: require different competition IDs **and** Non-EU bit 11 clear.

The remaining first-stage unknowns are now:
1. ownership/producer of the auxiliary per-player scouting byte behind
   `0x876868`;
2. status bit 7 user-facing meaning/producer.

RuntimePlayer does not yet persist the recovered bit-12 loan-list state, so the
loan-list scouting control still requires a callback despite its predicate now
being source-backed. Exact next implementation decision is to materialize that
state and the resolved country/preferred-position predicates without inventing
bit-7 semantics.


## Gate 11 recovery reconciliation: scouting history target implemented — 28 September 2026

Recovery audit found `research/CURRENT_STATE.md` lagging behind newer verified
main commits. The repository history proves the formerly active scouting
materialization task is already complete:

- `15fdc51e` / `cbb71d02` add and test exact country/preferred-position gates;
- `37d0478e` / `6fe13dca` materialize those gates in the live human scouting path;
- `25fe03dd` / `60ec5ab3` add and test exact scouting loan eligibility;
- `8dec7edb` / `f4e597a9` use live RuntimePlayer loan-list state;
- `d1baae91` through `3471644b` persist and verify the exact six-entry circular
  match-performance history and use it for scouting sort mode 2;
- `d616ba62` / `c9c1b948` implement and test the exact `0x6309D0` target
  match-performance rating with shared-CRT and separate MatchEngine RNG inputs.

The true next fidelity edge is therefore live history production after matches,
not any earlier scouting filter. Normal fixture finalization must compute the
target rating for each qualifying participant and append it through the exact
six-entry history primitive in original order. Before doing so, the semantic
match event stream must expose the source-backed secondary goal-attribution
player consumed by participant `+0x44`; delivered free-kick/corner takers are
already proven, while the open-play secondary slot remains to be confirmed.

The low-rating lift must continue to use a distinct MatchEngine RNG. It must not
be charged to or seeded from the shared MSVC CRT stream.


## Gate 11 goal secondary-attribution bridge checkpoint — 28 September 2026

Canonical `0x62C740 -> 0x62ECF0 -> 0x62F0C0` tracing resolves the last
open-play input needed by the exact target match-performance rating:

- open-play `record+0x08` = selected finisher;
- open-play `record+0x0C` = earlier attacking carrier;
- delivered free-kick/corner `record+0x08` = receiver/finisher;
- delivered free-kick/corner `record+0x0C` = set-piece taker.

Commits `2bf8169e` and `30a7eeb6` expose that optional secondary player
metadata in `ChanceRecord` and populate only the instruction-proven paths.
The event extension changes no scoring or RNG behavior. A focused regression
locks the open-play and delivered-free-kick attribution identities.

Exact next task: build the post-match target-rating/history finalizer from these
semantic counters and the already-mapped card/Form/history state. Keep the
MatchEngine low-rating RNG separate from the shared CRT stream; do not seed or
alias the two streams.


## Gate 11 live scouting performance history verified — 28 September 2026

The exact six-match scouting-performance producer is now live behind an
explicit separate MatchEngine RNG input.

Verified implementation chain:

- `2bf8169e` / `30a7eeb6` expose and populate event `+0x0C` secondary
  attribution for instruction-proven open-play and delivered set-piece paths;
- `0428277b` completes direct free-kick and penalty duplicate-taker
  attribution, matching `0x62EE20/0x62EEA0`;
- `1c57a032` exposes exact latest-history access corresponding to
  `0x41FA20`;
- `8c2f2fa8` / `e97425ff` add and test the
  `0x6309D0 -> 0x630FC0 -> 0x41F9C0` post-match target/history finalizer;
- `46fd7781` / `5d1f4722` implement and reference-test the distinct
  `0x981BF0` Numerical-Recipes/Park-Miller ran1 MatchEngine RNG;
- `0618910d` preserves secondary attribution across internal-save event
  serialization;
- `067a262f`, `b374a365` and `c767083a` integrate and verify the live
  AI/human fixture hook while preserving legacy callers when no explicit
  MatchEngine RNG is supplied.

CI initially exposed two integration defects: a historical test file had literal
backslash-n text, and new ChanceRecord secondary metadata was not serialized.
Those were fixed in `119a2130` and `0618910d`. A duplicated AI/human hook
block was then caught by the new high-level regression and fixed in
`c767083a`.

GitHub Actions at `c767083a`:
- **629 tests run, 2 failures**;
- both failures are the same pre-existing secondary-schedule assertions
  (root order 170/181 and 280-vs-262 bucket count);
- all new goal-attribution, performance-rating, history, MatchEngine-RNG,
  save-continuity and live-fixture tests pass;
- repository asset policy passes.

Exact next task: return to the two intentionally neutral scouting first-stage
inputs: status bit 7 and the auxiliary `0x876868 + player + 0x1D` byte behind
`ScoutStrengthMin`. Trace producers and UI/resource evidence; do not guess
labels.


## Gate 11 scouting final neutral inputs resolved — 28 September 2026

Recovery generation 52 re-materialized the authorized FM2001 disc archive and
re-extracted the root `FOOTBAL.EXE`. SHA-256 reverified exactly as
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`
before accepting new disassembly evidence.

### DBRPlayer +0x14 bit 7 = Out of contract

The formerly neutral scouting status bit now has converging direct evidence:

- `0x4177C0` contains the player-detachment path. On its successful branch it
  clears player `+0x14`, immediately sets bit 7 with `or al,0x80`, and writes
  `-1` into both registered/current club IDs `+0x10` and `+0x72`;
- `0x4185B0` clears bit 7 with mask `0xFFFFFF7F` during player-state
  reinitialization;
- the status-display path at `0x4E1FEB` maps bit 7 to status code **7** and
  bit 8 to status code **8**;
- the original English status sequence is ordered
  `Injured, Banned, International, Cup Tied, First Team, Subsitute, On loan,
  Out of contract, Transfer listed, Bid in, Wanted, Non EU`. This agrees with
  the independently recovered bit-6 **On loan**, bit-8 **Transfer listed**, and
  bit-11 **Non EU** mappings;
- `0x420570`, the player-valuation path already used by scouting, returns the
  zero-value branch when bit 7 is set, consistent with an out-of-contract
  player.

Bit 7 can therefore be materialized as **out_of_contract** rather than kept as
an unnamed callback.

### 0x876868 is a selected raw-skill ID, not an auxiliary table pointer

Exhaustive executable xrefs show only three references to global `0x876868`:

1. `0x4AD8E8`: initialize it to zero;
2. `0x4AE0ED`: assign the scouting selector value;
3. `0x4AE862`: read it in the first-stage filter.

The producer is fully bounded by the scouting panel constructor/event path:

- `0x4AD4F8..0x4AD51C` walks exactly 17 entries at
  `0x822538..0x822578` and builds selector records whose IDs are **1..17**;
- the selector object starts at panel `+0x7580`; its field at `+0x50`
  (panel `+0x75D0`) is initialized to zero at `0x4AD532`;
- `0x4AE0DA` reads that field, ignores sentinel `0xFFFF`, stores the selected
  ID at panel `+0x64E4`, and copies it to global `0x876868`;
- the filter at `0x4AE86B` then reads
  `BYTE PTR [player + selected_id + 0x1D]`.

Because valid selector IDs are 1..17, the address range is exactly
`player+0x1E..player+0x2E`, the reconstructed 17-byte current raw-skill
array. The previously described "auxiliary per-player scouting byte" is
therefore superseded: this gate selects one ordinary current raw skill, scales
that byte with `floor((30*raw + 128)/255)`, and compares it with the shipped
`ScoutStrengthMin` threshold. Selector value zero disables the gate.

This closes both intentionally neutral first-stage scouting inputs. The next
implementation step is to replace `status_bit_7` / `threshold_passes`
plumbing with source-named out-of-contract and selected-skill state while
preserving compatibility for callers that still use the neutral low-level
predicate.


## Gate 11 scouting Strengths/status materialization verified — 28 September 2026

The final neutral first-stage inputs are now reflected in clean-room runtime
code as well as research evidence.

Implementation checkpoints:

- `5660ff4e` adds the exact Strengths selector gate to
  `reconstruction/scouting.py`, with shipped `ScoutStrengthMin = 20`,
  selector 0 = All and selector 1..17 mapped to `current_raw[0..16]`;
- `cd1352cc` makes `search_scouting_players_mapped()` derive that gate
  directly from live RuntimePlayer skills, leaving the old threshold callback
  optional only as an additional compatibility constraint;
- the first-stage status data model now uses the source name
  `out_of_contract` rather than the neutral `status_bit_7`;
- `7156d286` / `e6bb3197` add focused pure/mapped regressions;
- CI exposed a test-fixture boundary error: raw 169 also displays as 20.
  The exact raw cutoff for displayed 20 is **166**; raw 165 displays 19.
  `867db284` / `dcff0e50` correct those regressions.

Validation at `dcff0e50`:

- **632 tests run, 2 failures**;
- both are the same pre-existing secondary-schedule assertions already tracked
  before this scouting work;
- all new scouting status/Strengths tests pass;
- repository asset policy passes.

The Out-of-contract checkbox now has exact meaning, but the ordinary runtime
producer is still intentionally not synthesized from contract expiry alone.
`0x4177C0` and `0x41ABC0` set bit 7, while `0x4185B0` and
`0x419210` clear it. Exact next task: reconstruct those transitions and
their scheduling/RNG boundary sufficiently to materialize live
`out_of_contract` state and remove the mapped-sc-predicate resolver.


## 28 September 2026 - Gate 11 live Out-of-contract lifecycle

Recovery generation 52 closed the remaining mapped-scouting status dependency
without replacing FM2001's contract logic with a simple expiry comparison.

Canonical executable tracing established the ordinary non-user monthly
`0x41ABC0` path and its caller/order:

- day-of-month 1 only through `0x4A81A0 -> 0x40BB10 -> 0x4042E0`;
- club-table then roster order;
- monthly player development runs immediately before contract maintenance;
- more than 30 days before expiry consumes no contract RNG;
- rating below 50 releases only on first `RNG(100) < 8`; that successful
  branch consumes one draw, while the non-release path consumes a second draw;
- rating 50 or above always consumes two draws and releases only when the
  second `RNG(100) < 2`;
- release additionally requires roster count >18, tenure >104 completed weeks,
  age >23, neutral `player+0x64 <= -1`, and no temporary/loan-club mismatch;
- successful release calls the transfer-list transition, sets DBRPlayer
  `+0x14` bit 7 (Out of contract), and clears `+0xC0` without directly
  detaching club IDs;
- every other due branch adds exactly 12 calendar months through
  `0x419190 -> 0x419210`, clearing Out-of-contract and the mapped
  signed-for-another-club bit.

Implementation now persists `RuntimePlayer.out_of_contract`, runs the
non-user monthly transition through the shared CRT stream, uses the live flag
in mapped human scouting without requiring an external resolver, and preserves
the flag in internal save schema 16. The compatibility resolver remains an
explicit override rather than a required producer substitute.

Focused regressions cover the exact one-vs-two draw boundary, both rating
bands, failed eligibility without an extra draw, the `0x417580` blocker/loan
shape, controlled-club skip, live scouting and save/reload continuity.

GitHub Actions at `69e42cdf0ca8a65b724d81d37b76e7bd0a34294c` ran **639
tests**. The only failures are the same two pre-existing secondary-schedule
assertions (secondary root order and 262-vs-280 bucket count); all new Gate-11
tests passed. Repository asset policy passed.

Evidence: `research/GATE11_OUT_OF_CONTRACT_LIFECYCLE.md`.

Next: reconstruct the separate user-controlled `0x41BEE0` expiry/grace/event
path. Direct tracing already proves it is not the AI rule: at least one branch
sets Out of contract only after a 21-day post-expiry grace interval, while
other expired branches can alter roster/club state. Preserve that event-driven
lifecycle rather than folding it into the non-user producer.


## 28 September 2026 - Gate 11 controlled contract expiry and renewal suggestions

Canonical `0x41BEE0` tracing closes the ordinary user-controlled contract
maintenance branch separately from the already implemented non-user
`0x41ABC0` rule.

Source-backed behavior now persisted in
`research/GATE11_CONTROLLED_CONTRACT_EXPIRY.md`:

- ordinary controlled players set **Out of contract** from exactly 21 days
  before expiry;
- the assistant-manager renewal-suggestion window opens 112 days before
  expiry and consumes exactly one shared `RNG(10)` when the `+0x164`
  suggestion latch is clear;
- rolls 0..3 continue through the exact pending-deal suppression shape;
- age >=24 plus EU/exempt code 2 selects
  `EAMAssManSuggestBosmanPlayerContractRenewalMsub`; other players use
  `EAMAssManSuggestPlayerContractRenewalMsub`;
- both are queued through the original MPMEAMail family and accepting either
  enters `EAMAmendContractsub`; suggestion creation itself does not renew the
  contract;
- `player+0x178` is now writer-bounded: deal creation increments it,
  `0x417870` removes the deal/decrements it, and club assignment resets it.
  Under the current one-deal-per-player runtime invariant,
  `deal exists && state in {3,4,5}` exactly represents the
  `0x41C6F0` suppression condition;
- at expiry, an active loan is returned before common mapped status cleanup;
- ordinary players remain attached through a 21-day post-expiry grace period;
- at exactly 21 days past expiry, `0x41EF00` removes the player's club
  training assignment, purges player-linked manager mail, removes the player
  from the club roster, stores the old club ID at `+0x74`, sets both club IDs
  to -1 and leaves Out-of-contract set;
- renewal path `0x419190 -> 0x419210` clears Out-of-contract, the
  signed-for-another-club state and the `+0x164` renewal-suggestion latch.

Implementation checkpoints:

- `a1035b91` adds neutral persistent `+0x138`, the `+0x164` suggestion
  latch and old-club `+0x74` state;
- `d915034b` / `fb9d6d63` advance internal save through schema 18 and
  preserve both player contract state and queued renewal suggestions;
- `bf1f1c2d` implements the ordinary controlled state machine;
- `3f6a156d` materializes the two exact suggestion event kinds;
- `8c8d3170` integrates AI and controlled contract maintenance in one
  first-of-month club/roster-order pass, using active loan club for branch
  ownership;
- `07c4e134` / `76790695` add live integration and save-continuity
  regressions;
- `f05d3e15` corrects a synthetic test fixture whose player registered club
  did not match its roster owner;
- `4fe32070` / `391d0845` mirror and test the original renewal-latch clear.

Validation at `391d0845`:

- **654 tests run, 2 failures**;
- both failures are the unchanged secondary-schedule assertions already tracked
  before this contract work;
- all new controlled-contract, mail, save/reload and scouting tests pass;
- repository asset policy passes.

The remaining `0x41BEE0` branch is the neutral
`player+0x138 >= 0xFE` `0xFE/0xFF` special state. Direct behavior strongly
connects it to the existing !Spare player recycle machinery, but the semantic
label has not yet been promoted from inference. Exact next task: trace the
producer/consumer link from the already mapped transfer-refusal reasons
“player has decided to retire” / “upcoming testimonial” and other direct
writers before naming or implementing that branch.


## +0x138 special controlled-contract state bounded as non-fresh compatibility path — 28 September 2026

Follow-up after the ordinary `0x41BEE0` lifecycle audited the remaining neutral
`DBRPlayer+0x138` `0xFE/0xFF` branch without assigning a speculative label.

Direct xref result inside the DBRPlayer code region:

- fresh construction writes `+0x138 = 0`;
- save/load serialization reads/writes the byte;
- `0x41BEE0` reads it, promotes `0xFE -> 0xFF`, and later clears it;
- no separate fresh-game writer that sets `+0x138 = 0xFE` was found;
- the already mapped transfer-refusal reasons “player has decided to retire”
  and “player wants to stay for an upcoming testimonial” do not directly read
  or write `+0x138`.

The special expired branch itself is still instruction-bounded: it clears
additional player state, removes the player from the old roster, moves both club
IDs to the canonical `!Spare` parking team, then clears `+0x138/+0x164`.
That strongly places it beside player recycle/retirement machinery, but it does
not prove the field's semantic name.

Because no proven fresh-game producer exists, the clean-room keeps
`contract_special_state_138` neutral and returns
`SPECIAL_STATE_DEFERRED` for nonzero special states. This is recorded as a
legacy/original-save/recycle compatibility boundary rather than inventing a
fresh-game producer. It does not block the Gate-11 fresh core-management loop.

Gate-11 audit then identified the next reachable fresh-game gap: the startup
`0x61DF90 -> 0x41E510` youth path is fully represented in the RNG replay but
not yet materialized in GameState as the user's separate 20-slot youth list and
generated-player transformation. That youth workflow is the next active task.


## Gate 11 fresh human youth list materialized — 29 September 2026

Canonical executable tracing closed the first reachable human-youth slice and
proved that youth-list membership is distinct from first-team roster membership.

Evidence is in `research/GATE11_YOUTH_WORKFLOW.md`. The recovered structure is:

- DBRUser owns a separate youth list at `+0x6BC`;
- the list has a hard cap of **20** inline **0x18-byte** records;
- record `+0x00` is player ID, `+0x04` points to the already-known
  **0xA4-byte training-state object**, `+0x08/+0x0C/+0x10` initialize to 1
  and neutral byte `+0x14` initializes to zero;
- `0x61E100/0x61E170` remove and compact records, while
  `0x61E1B0/0x61E1F0` set/read the neutral `+0x14` byte;
- `0x41E510` rewrites the selected !Spare DBRPlayer's age/name/country and
  registered-club field but **does not insert it into the first-team roster**;
- `0x61DD30` immediately produces the final fresh age-17 cohort state;
- named youth-promotion path `0x61E3D0 -> 0x417700` removes the youth record,
  moves the player between roster containers, copies the youth training state,
  applies the promoted wage and contract;
- youth release through `0x4177C0` removes the youth record and source roster
  entry before the normal free-player / Out-of-contract detachment.

A further writer trace corrected the multi-user startup replay: `0x4185B0`
sets DBRPlayer status bit 3, and `0x61DF90` excludes that bit on every fresh
candidate scan. Each user therefore rescans the player table after prior users'
selected candidates became ineligible, *before* the fixed 512-entry cap. Commit
`cac1e45b` implements this; `515d27ba` regression-locks the changed
second-user selection while preserving the same final synthetic CRT checkpoint
`0x4B68DE28`.

Implementation checkpoints:

- `43d4df83` / `205ba9c9`: persist neutral live status bit 3;
- `c681b338`: add separate `YouthTeamState`, exact generation/name ordering,
  promotion and release;
- `07237a9d`: focused youth-list/generation/promotion/release regressions;
- `c6c2e472` / `7062b76c`: preserve immutable player source identity so
  youth-mutated live names/DOB/nationality do not invalidate source-database
  save verification;
- `221587b1` / `d223457a`: expose explicit GameState/controller youth
  actions without silently consuming the already-verified post-schedule RNG;
- `5ff60b02`: persist the separate youth list and training state;
- `1d6b7a32`: internal save schema **21** persists mutable generated player
  identity separately from immutable source identity;
- `f42e6e2a` / `20300c8b`: save/reload and public controller regressions.

GitHub Actions at `20300c8b`:

- reconstruction suite: **662 tests run, 2 failures**;
- both failures are the same pre-existing secondary-schedule assertions
  (secondary root 170/181 order and 280-vs-262 bucket count);
- all new youth, save-continuity and controller tests pass;
- repository asset policy passes.

The first youth slice is therefore implemented and reload-safe, but direct
follow-up tracing found a second initializer `0x61DE40` used from
`0x425680`. It clears the youth list, generates a first cohort, runs
`0x61DD30`, then generates a second cohort before assigning a common date.
Its caller/cadence must be resolved before claiming the complete in-season youth
lifecycle. Exact next task: bound `0x425680 -> 0x61DE40` lifetime and map the
two-cohort final state/RNG ordering.


## Gate 11 pending-club youth initializer resolved — 29 September 2026

Re-extracted canonical `FOOTBAL.EXE` from the authorized disc image and verified SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

Closed the `0x425680 -> 0x61DE40` caller/lifetime boundary. The only direct chain is `0x4320BD -> 0x4A83F0 -> 0x4A83D0 -> 0x4A8070 -> 0x425680`. `0x4A8070` calls only while DBRUser `+0x10E0 != -1`; `0x425680` consumes and clears that pending club index. This is club activation/switch initialization, not seasonal youth cadence.

Resolved the two-cohort final youth state: ordinary fresh activation clears the prior list, creates four youth, post-processes those four to age 17, creates four more that remain age 15, assigns all eight the next 30-June `+0x154` date, and resets their training objects. Record clearing does not undo DBRPlayer status bit 3, so previous generated players remain excluded from later 512-entry candidate rescans.

Found a material RNG omission in the prior startup/training bridge. The two fresh four-player cohorts consume 24 mandatory shared CRT draws between the known `RNG(10)` and `0x5E3FD0`: `0xA54D70C6 -> 0xFA1C595E`. The corrected 37-way support-staff selector takes 13 attempts and the fixed-staff block ends at `0xA2FEE1E1`. Youth Team Coach rating stays 2, preserving training-quality multiplier 1.30.

Next: implement the activation-specific two-cohort youth materializer/replay, correct the transfer-list/startup replay checkpoint, then recompute the commercial-timer and first-training bridge from `0xA2FEE1E1`.


## Gate 11 activation youth implementation and corrected training bridge — 29 September 2026

Implemented the resolved `0x61DE40` activation path in clean-room code. `replay_activation_youth_generation_for_country` now performs the two global candidate rescans with prior status-bit-3 exclusions applied before each 512-entry cap. `initialize_user_youth_for_club_activation` preserves old player mutations while replacing the youth records, materializes the age-17 then age-15 cohorts, applies the common next-30-June date, and resets youth training state. Focused regressions cover both the 512-cap refill behavior and the final two-age-band state.

Corrected `tools/replay_gate11_transfer_list.py` to include the missing 24 shared CRT youth draws after the `0x425680` RNG(10). The exact corrected checkpoints are:

- post-youth / pre-selector: `0xFA1C595E`;
- 37-way selector: 13 attempts, accepted values `10,33,34,14,9,23,3,10,3,27,34,33`;
- post-selector: `0x7470CA25`;
- post-fixed-support-staff: `0xA2FEE1E1`;
- Youth Team Coach rating remains 2.

Replayed the commercial-timer / seven-day training bridge from `0xA2FEE1E1`. Fresh concession wait is now 19 days and no-sponsor wait 10 days, so neither re-fires before first active Saturday. The corrected pre-first-`0x4EACE0` CRT state is `0x4C745924`; final seven-day Condition sum remains 3342.

Next: verify GitHub Actions and the canonical data-backed replay, then update the exact Gate-11 active dependency from the completed youth initializer to the next reachable unresolved management lifecycle.

## Gate 11 post-match morale verified and advanced — 29 September 2026

Recovery generation 56 resumed from the newest canonical `main` rather than the
stale youth handoff. Commit `0b567986ec8b51b9f66c8e038de7aa9726088535`
had already integrated Premier League post-match morale into both AI and human
fixture completion.

The first CI run exposed one new morale regression in addition to the two known
secondary-schedule failures. Direct reinspection of canonical `FOOTBAL.EXE`
(`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`)
proved the implementation was correct and the test expectation was one point
low: `0x41BB10` includes an explicit final `+1` after base amount,
`RNG(2)`, leadership and age modifiers. Commit
`130a929fe1e5505a77951b7c190b1d9e374f1b57` corrected the regression.

GitHub Actions at `130a929f`:

- reconstruction suite: **668 tests run, 2 failures**;
- both failures are the unchanged secondary root-order / bucket-count
  assertions;
- all morale tests pass;
- repository asset policy passes.

The original tuning-loader names were also bounded for the next lifecycle:
`unhappynessrequestnewcontract`, `unhappynesslostmatch`,
`unhappynesswonmatch`, `unhappynesswontrophy`,
`unhappynessnotplayed`, `maximummorale`, `loanmorale`,
`signednewcontactmorale`, and `dangermoralelevel`.

Detailed evidence is now in `research/GATE11_MORALE_LIFECYCLE.md`.
Exact next task: trace the ordinary signing and loan callers
`0x419210 -> 0x41BB10(SignedNewContactMorale)` and
`0x41A9D0 -> 0x41BB10(LoanMorale)`, then integrate their exact `RNG(2)`
placement into the already-materialized transfer/contract runtime. The
request-new-contract event and trophy path remain deferred until their producer
ownership is independently closed.


## Gate 11 signing and loan morale ordering closed — 29 September 2026

Recovery generation 57 reconciled the post-`130a929f` morale commits against
canonical `main`, then re-materialized the authorized disc image and
reverified `FOOTBAL.EXE` SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

Direct executable inspection instruction-closed both active morale callers.

For `0x419210`, `SignedNewContactMorale` is loaded at `0x419283` and
`0x41BB10` is called at `0x419289`; only afterwards does `0x41928E`
clear the `DBRPlayer+0x164` renewal-suggestion latch. The clean-room now
centralizes that exact trailing order in
`apply_signed_contract_finalizer_morale`, shared by completed transfers, AI
renewals and youth contract paths.

For loans, RTTI-backed `MPMLoanPlayer::Execute` (`0x61B620`) converges on
`0x41A9D0`. That routine installs the temporary club at player `+0x10`,
performs club/status bookkeeping, clears the recovered loan-list state before
setting on-loan bit 6, and only as its final operation at
`0x41AA3A..0x41AA43` calls `0x41BB10(LoanMorale)`. The clean-room
`complete_player_loan_assignment` therefore installs the already-materialized
loan state first and consumes exactly one `RNG(2)` last. Unmapped neutral
status bits remain deliberately unguessed.

The same trace proves the fresh startup Matthew Upson/Watford loan-list path
must not gain a LoanMorale draw: the user-controlled Arsenal branch queues the
loan proposal/event and consumes its separate `RNG(5)`; it has not yet
executed `0x41A9D0`.

Implementation/test checkpoints:
- `5abaef3b`: shared signed-contract finalizer;
- `2c5e3e30`: correct AI-renewal latch/morale ordering;
- `ef319092`: materialized loan-assignment + LoanMorale-last slice;
- `1e2940da`: route youth contract paths through the same finalizer;
- `3d5ff419`, `72be50c8`, `1a545d1c`: state-at-RNG regression coverage;
- `7e798a03`: repair a stale AI-renewal test fixture that had not accounted
  for the already-implemented signed-contract `RNG(2)`.

GitHub Actions at `7e798a03`:
- reconstruction suite: **670 tests run, 2 failures**;
- both failures are the unchanged secondary root-order / bucket-count
  assertions;
- the new signing, loan, renewal and youth morale regressions pass;
- repository asset policy passes.

Detailed evidence is in `research/GATE11_MORALE_LIFECYCLE.md`.

Exact next task: independently bound the request-new-contract morale producer
around `0x5D8430 -> 0x41BA80(UnhappyRequestNewContract)`. Do not attach this
decrease to ordinary progression until the event/action ownership and reachability
are proven. Trophy morale and `DangerMoraleLevel` remain deferred behind the
same evidence rule.


## Gate 11 request-new-contract morale bounded as load-only — 29 September 2026

Canonical `FOOTBAL.EXE` RTTI identifies vtable `0x7D7D74` as
`MPMNewContractRequest`. Its action `0x5D8430` resolves the stored player,
loads `UnhappyRequestNewContract` from `0x821C20`, and calls the exact
`0x41BA80` morale-decrease primitive, so a serialized object that executes
would consume one shared `RNG(2)`.

An exhaustive constructor/factory xref audit found no ordinary fresh-game
producer. Type ID 10 in generic MPM factory `0x6139E0` constructs this class,
but the only call into that factory is the MPM deserialization loop at
`0x613F80`, itself reached from the save-load path at `0x50E108`. The
`MPMNewContractRequest` vtable is written only in that factory case and
`0x5D8430` has no direct code callers.

Therefore this morale decrease is retained as a load/compatibility boundary and
is not attached to fresh ordinary progression. The next live morale dependency
is `DangerMoraleLevel`: `0x404E25` calls `0x41B580` from the existing
controlled-club post-match roster pass, so that consumer is demonstrably
reachable and is now the active trace.


## Gate 11 danger-morale transfer-request lifecycle closed - 29 September 2026

Recovery generation 58 resumed from main
`454c118ae4369daf488d69d12680d7aaa1ef0cc1` and re-materialized the same
authorized FM2001 disc archive from the ChatGPT Library. The raw MODE1/2352
image was converted only in the temporary working container, and the extracted
root `FOOTBAL.EXE` reverified canonical SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

Direct executable tracing closes the controlled-club post-match low-morale
request path:

- `0x404E25 -> 0x41B580` runs from the existing club roster pass after each
  player's ordinary morale/Form handling;
- the player's active club must resolve to a human user;
- morale must be strictly below shipped `DangerMoraleLevel = 15`;
- the branch then consumes one shared scaled
  `RNG(ChanceAskForTransfer)` with shipped bound **30**, and only result 2
  continues;
- only after that draw does `0x41B7B0` reject status bit 8
  (**Transfer listed**) or bit 10 (**Wanted**), so blocked low-morale players
  still advance the shared CRT stream;
- success queues `EAMPlayerAskTransferListsub` inside `MPMEAMail` for
  current date + 1;
- action 0 produces `EAMAcceptTransferRequestsub`; action 1 produces
  `EAMRefuseTransferRequestsub`;
- accepted follow-up reaches `0x41B530 -> 0x420A10`, setting Transfer-listed
  bit 8, refreshing transfer value and setting Wanted bit 10;
- refusal only cleans up the request chain, without changing player morale or
  those status bits.

A separate whole-PE reference audit finds `UnhappyWonTrophy` global
`0x821C23` exactly once: its tuning-loader write at `0x505801`. It has no
live executable consumer and is therefore dormant/loader-only tuning in the
canonical executable. No trophy morale effect will be invented.

Evidence is persisted in `research/GATE11_MORALE_LIFECYCLE.md` and
`research/EXECUTABLE_ANALYSIS.md`.

Exact next implementation task: integrate the source-backed delayed
low-morale transfer-request state into the existing post-match/manager-event
runtime with exact roster/RNG order and accept/refuse consequences, including a
minimal persistent representation of status bit 10 only where required by the
proven blocker/lifecycle.


## Gate 11 low-morale transfer-request integration verified - 29 September 2026

The instruction-closed controlled-club danger-morale lifecycle is now live in
the clean-room runtime.

Implemented and verified behavior:

- the existing per-player post-match roster pass checks the controlled-club
  danger path only after that same player's ordinary morale/Form work;
- active-club ownership respects temporary loan club state;
- morale below shipped threshold **15** consumes exactly one shared
  `RNG(30)`, and only result 2 can create a request;
- Transfer-listed/Wanted duplicate blocking occurs after that draw, preserving
  shared CRT advancement even for blocked low-morale players;
- success queues persistent next-day `PlayerAskTransferList` manager mail
  rather than immediately mutating transfer status;
- accepted response sets Transfer-listed and Wanted; refusal leaves those bits
  and morale unchanged;
- RuntimePlayer now materializes original status bit 10 as `wanted`;
- internal save schema **22** persists Wanted and queued transfer-request mail;
- save/reload regression covers due-mail exposure, accepted response, queue
  cleanup and final Transfer-listed/Wanted state.

Implementation checkpoints: `b4bfc81d`, `db592412`, `99bbf3be`,
`46e73142`, `6318e345`, `53c76ef2`, `15ee8f43`, `b0c94556`,
`12bf9ac2`.

GitHub Actions at `12bf9ac2fa145958cde06ee41f0e954b99fd1e08`
ran **675 reconstruction tests**. The only two failures are the same known
secondary-schedule assertions already present before this slice; there are no
new morale/request/save failures. Repository asset policy passed.

The morale slice is therefore no longer the active Gate-11 dependency. The next
step is a Gate-11 completion audit against the roadmap criterion, "A human
manager can complete a Premier League season using the core management
systems," so the project advances only if that criterion is actually satisfied.


## Gate 11 complete; Gate 12 activated - 29 September 2026

Gate 11 is closed against its explicit roadmap criterion rather than by target
count alone.

Commit `22027de93df54fe7a83151ba642f6d0f86ecc93f` added a deterministic
38-round / 380-fixture human-manager season regression. It keeps the human
controller active through every round, completes all ten fixtures each
matchday, enables the recovered user training calendar, preserves legal
selection availability, and reaches 380 stored Premier League results / 760
table appearances with the human club on 38 played.

GitHub Actions at that checkpoint ran **676 reconstruction tests**. The only
two failures are the same long-standing secondary-schedule assertions; the new
full-season management regression passes. Repository asset policy passes.

The target-by-target audit in `research/GATE11_COMPLETION_AUDIT.md` records
live core-loop coverage for training/development, scouting, youth, morale,
injury/availability, discipline, actionable manager-event state and recurring
manager tasks. Full original management presentation remains correctly deferred
to Gate 13.

`ROADMAP.md` now marks Gate 11 complete and activates **Gate 12 - Other
competitions**.

Exact next task: audit the recovered generic competition/cup runtime against the
canonical English domestic cups (FA Cup and League Cup first) and identify the
first source-backed missing behavior required to connect them to the human
Premier League season.


## Gate 12 Cup result registry bridged to shared match virtual - 29 September 2026

Recovery generation 59 resumed canonical `main` at
`64c4f24c0e448f11f40c49a301b05b9e35e67fc0` after the English domestic-cup
startup audit and the initial Cup result-reference work.

The already-persisted sequence had established a result-token registry, exact
winner/loser ClubRef resolution, and the shared CupMatch result virtual
`0x514000`. Commit `87d3c2b0b92da0cd2441455b1ac4d8811b84f457`
now removes the remaining manual-winner handoff at that boundary:
`CupResultRegistry.record_match_resolution()` records only when the shared
virtual resolves a definitive club. A drawn/incomplete snapshot leaves the
token unconsumed so a later Replay/SecondLeg object can provide the definitive
outcome.

GitHub Actions at that checkpoint ran **690 tests**. The only two failures are
the same pre-existing secondary root-order and bucket-count assertions. All new
Cup result/progression tests pass, and repository asset policy passes.

Exact next task: trace the class-specific Cup completion producer path,
starting with FA Cup NormalRound Replay creation/completion and League Cup
TwoLeg SecondLeg linkage plus the exact tied-aggregate continuation. Do not
attach Cup nodes to GameState until this path is source-backed.


## Gate 12 replay and two-leg completion producer closed - 29 September 2026

Recovery generation 59 re-materialized the authorized FM2001 disc archive from
the ChatGPT Library, converted the MODE1/2352 image only in the temporary
analysis container, extracted the root `FOOTBAL.EXE`, and reverified canonical
SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

Direct executable tracing closes the class-specific Cup producer that had
blocked live domestic-cup progression:

- `CupMatchReplay` is constructed live at
  `0x51399E -> 0x510600` only after an unlinked NormalRound match's shared
  `0x514000` result returns null;
- the replay reverses ClubRefs, links the first match, forces the 120-minute and
  decisive tie-break flags, and is inserted through `0x615A60`;
- `FirstLegMatch` / `SecondLegMatch` are constructed by the TwoLeg builder
  at `0x4F6A02` / `0x4F6A64`; second leg reverses the participants, links
  the first leg, inherits 120-minute capability and forces the decisive flag;
- the match setup at `0x510DD7` and `0x510E06` maps Cup flags into the
  engine's 90/120-minute and decisive penalty/tie-break states;
- on a tied two-leg aggregate, `0x514000` applies the recovered away-goal
  comparison first;
- only when aggregate and away goals remain equal does
  `0x51367D..0x5136B3` execute the final tie-break, including
  `RNG(2)` fallback `0x64D540(2)` if event-derived tie-break totals still
  tie;
- score virtuals include the tie-break bytes, making the result definitive.

The detailed addresses, constructor semantics and replay-date arithmetic are
now persisted in `research/GATE12_ENGLISH_DOMESTIC_CUPS.md`.

Exact next task: implement this now-instruction-closed Cup match lifecycle in
the clean-room runtime, add deterministic FA Cup replay and League Cup
two-leg/tied-aggregate progression tests, then use those resolved outcomes as
the prerequisite for GameState calendar integration.


## Gate 12 Cup lifecycle implemented and persistent result state attached - 29 September 2026

Recovery generation 60 reconciled canonical `main` after the stale-session
handoff. The repository had already advanced beyond the producer-trace
checkpoint through:

- `e524e306`: clean-room NormalRound Replay and FirstLeg/SecondLeg lifecycle;
- `aecc94aa`: source-ordered decisive fallback after the SecondLeg away-goal
  comparison;
- `fa5af011`: decisive-score naming/tests aligned with executable ordering.

The next integration boundary has now started without rebuilding solved Cup
startup RNG/draw behavior:

- `6eca6fee` attaches a persistent `CupResultRegistry` to `GameState`;
- `7f775f7b` advances the modern internal save schema from **22** to **23**
  and serializes/restores definitive Cup outcomes;
- `5c5cc1d5` adds a full controller save/reload regression for a Cup result
  token.

GitHub Actions at `5c5cc1d50ead46fe3a83c9dc35fd8c67498f74e4`
ran **698 reconstruction tests**. The new Cup save/reload regression passed.
The only failures remain the two known secondary-schedule assertions:
`test_secondary_root_order_uses_same_crt_qsort_then_mode_filter` and
`test_secondary_container_bucket_counts_reach_canonical_staff_seed`.
Repository asset policy passed.

Exact next task: attach the already-materialized FA Cup/League Cup schedule
nodes to live GameState state, persist active per-node first-match/first-leg
state, resolve symbolic participants lazily from the Cup registry, and verify
date/due-node behavior before merging Cup fixtures into the human/AI matchday
loop.


## Gate 12 live domestic Cup schedule state verified - 29 September 2026

The first calendar-facing domestic-Cup state layer is now live without
replaying any solved startup draw RNG.

Implementation checkpoints:

- `359dbad4`: new `DomesticCupScheduleState` materializes only competition
  1 (FA Cup) and 5 (League Cup) from existing `StartupScheduleNode` objects,
  maps source week/weekday through the established season-date conversion,
  preserves symbolic ClubRefs, and tracks completed schedule-node identity;
- `f405a5b3`: deterministic regressions cover domestic filtering/date mapping,
  lazy type-1 winner resolution, SecondLeg blocking until its FirstLeg node is
  complete, and schedule-state snapshot round-trip;
- `a070aa73`: `GameState` now owns the domestic-Cup schedule and exposes
  install/due-node helpers without consuming RNG;
- `3a35be7a`: internal save schema advances from **23** to **24** and persists
  the live schedule/completion state;
- `0d6b1ff3`: full controller save/reload regression preserves a completed
  League Cup FirstLeg with its SecondLeg still pending.

GitHub Actions at
`0d6b1ff30f60241e0a038447ee06d90a60e599f3` ran **703 reconstruction
tests**. All new domestic-Cup tests passed. The only two failures are the
unchanged secondary root-order and secondary bucket-count assertions.
Repository asset policy passed.

Exact next task: persist the actual `CupMatchRuntimeState` score/link objects
behind scheduled nodes and then implement source-exact dynamic FA Cup Replay
insertion. Do not use a guessed generic replay delay; the recovered replay-date
arithmetic must be preserved before Cup fixtures enter the normal human/AI
matchday loop.


## Gate 12 persistent Cup match score/link state verified - 29 September 2026

The live domestic-Cup layer now preserves actual Cup match objects, not only
schedule/completion identity.

Implementation checkpoints:

- `b317d4aa`: `DomesticCupScheduleState` can materialize source-class
  NormalRound and TwoLeg match objects with explicit constructor policy inputs,
  keeps FirstLeg/SecondLeg objects keyed to their schedule nodes, and
  serializes completed scores plus linked-match identity;
- `c69793e4`: deterministic tests prove a completed 2-1 FirstLeg survives
  state round-trip and still links into the pending reversed SecondLeg; a
  symbolic NormalRound cannot materialize before its referenced winner resolves;
- `d0383991`: internal save schema advances to **25** for live Cup match
  score/link state;
- `e934dff5`: the full human-controller save/reload path preserves the same
  completed FirstLeg score and reconstructs the pending SecondLeg link.

GitHub Actions at
`e934dff5ccaa72066e666070201271b72dda74be` ran **705 reconstruction
tests**. All new Cup state/save tests passed. The only two failures remain the
known secondary root-order and secondary bucket-count assertions. Repository
asset policy passed.

Exact next task: close the remaining NormalRound replay scheduling input at
`0x51392A`. The clean-room must identify the source of
`selected_date_anchor[+8]`, map round `+0x28/+0x2C`, and prove conversion
to the season date before dynamically inserting a replay. Do not replace this
with an assumed fixed delay or unproven direct use of the packed replay week/day.


### 2026-09-29 - Gate 12 dynamic FA Cup replay checkpoint reconciled

- Recovered the exact `0x51392A..0x5139BA` replay-date producer and corrected
  domestic-Cup primary-container date anchoring to the first Monday on or after
  1 July.
- Canonical FA Cup replay-producing rounds use current match-completion day
  plus 14 days; the packed replay-floor branch is unreachable for those shipped
  rounds.
- Implemented reversed linked dynamic `CupMatchReplay` insertion and verified
  the replay node/match linkage survives controller save/reload.
- Verified main `a41feea2c51bc40d614c59c606467b59680bc040` in GitHub Actions:
  707 reconstruction tests ran with only the two unchanged known secondary
  schedule failures; repository asset-policy workflow passed.
- Next Gate-12 slice: bind domestic Cup execution to the post-placement,
  post-shuffle primary schedule so conflict-moved dates and global
  `0x615C10` head-to-tail ordering are preserved before human/AI matchday
  execution is enabled.


## Gate 12 shuffled-primary domestic Cup bridge verified - 29 September 2026

Commit `ccac3ba2ff6b92269574e2c4bbeebbe514cdaf22` now carries the
calendar-facing FA Cup / League Cup state from the exact Gate-4 primary
schedule result rather than the pre-placement startup node list.

The bridge deliberately separates two proven concepts instead of inventing one
global date formula:

- `0x615950` raw primary relative-day arithmetic is exposed separately from
  its Christmas exception;
- each domestic Cup's already-recovered Gregorian source date receives only the
  actual chosen-bucket displacement, so conflict moves and the Christmas skip
  survive;
- post-`0x615AE0` bucket order is retained head-to-tail for same-day domestic
  Cup execution;
- canonical `HumanGameplayController` construction now installs both the
  recovered PL fixture ordering and domestic Cup state from the same verified
  shuffled primary buckets.

GitHub Actions at `ccac3ba2` ran **710 reconstruction tests**. The only
failures are the same two pre-existing secondary root-order / bucket-count
assertions, and repository asset policy passed.

A fidelity boundary remains explicit before global PL/Cup execution: fixed
Premier League source weeks and Cup source weeks currently use separately
recovered date conventions despite sharing the primary container. The next
slice must not collapse those conventions without proving the missing transform.
It must also recover the static producer of the already-understood CupMatch
constructor policy bits before due Cup nodes can materialize automatically.


## Gate 12 constructor-policy closure reconciled - 29 September 2026

Recovery generation 62 resumed at main `4eb97457` and verified that the
constructor-policy task named in the previous handoff had already advanced:

- `71d1d65f` parses the packed DBRRound policy fields at +28..+31 and carries
  the recovered extra-time / decisive inputs into Cup schedule nodes;
- `4eb97457` keeps legacy synthetic schedule stubs compatible without
  affecting canonical startup RNG or placement behavior.

The remaining calendar gap was narrowed to one executable boundary rather than
a generic "PL/Cup date transform." The current clean-room maps PL packed
`8/3` and League Cup packed `7/3` to the same Gregorian date
(23 August 2000), while raw primary-container indices differ by seven. Because
both use the same primary container, the next trace must prove the actual
week/day arguments supplied by fixed-League builder `0x6173D0` to
`0x615950`, including any pre-call week adjustment. The Cup-specific anchor
is already instruction-closed and must not be changed merely to reconcile the
older PL helper.


## Gate 12 fixed-League date argument closed - 29 September 2026

Using the re-materialized authorized disc image, the canonical root executable
was reverified at SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

Direct disassembly closed the exact boundary that remained after
`e3335627`:

- `0x4F4500` stores DBRRound packed week unchanged and weekday-1 into the
  8-byte `League+0x60` date array;
- `0x6173D0` pushes the selected `League+0x60` entry directly to
  `0x615950`;
- no week decrement or normalization exists at the fixed-League call site;
- `0x6169F0 -> 0x64CC70` anchors primary mode 0 to the first Monday on or
  after July 1, which is 3 July 2000 for the shipped season.

This resolves the former PL/Cup source-week contradiction in favor of one
primary-container convention. The older clean-room PL date helper is seven days
early for 2000/01. It also means the executable's Christmas-Day exception
falls on packed `25/1`, not the current clean-room `26/1`.

The next checkpoint must correct those two implementation assumptions and
rerun the canonical primary schedule reconstruction before shared PL/Cup
execution is enabled.


## Gate 12 shared primary calendar correction verified - 29 September 2026

Commits `572fdd95` and `1b388b66` correct the clean-room calendar to the
instruction-closed primary ScheduleContainer convention and refresh every
affected synthetic date-sensitive regression.

Verification at `1b388b66eaa635eafcc8344a205c12a021c54f18`:

- GitHub Actions reconstruction suite: **710 tests run, 2 failures**;
- both failures are the unchanged known secondary root-order / secondary
  bucket-count assertions;
- repository asset policy: **passed**.

A direct canonical Static.dat audit found no round whose scheduled date or
replay/second-leg date is `25/1` or `26/1`. Therefore moving the
`0x615950` Christmas-Day source pair from the old clean-room `26/1` to
the executable-backed `25/1` does not move any shipped startup node. The
canonical 9,346-node primary placement and its established RNG checkpoint stay
valid.

The PL/Cup calendar transform is now closed. Gate 12 can proceed to actual
shared domestic-Cup execution.


## Gate 12 Cup AI strategy context closed - 29 September 2026

Direct executable tracing closed the remaining formation-strategy inputs for
Cup matches:

- `Cup+0x3C` is the total runtime round count. `0x4F6D60` appends each
  created round and increments this count.
- the Cup round initializer receives the zero-based round index and passes that
  same value into `CupMatch` constructor `0x510520`, which stores it at
  `CupMatch+0x50`;
- `0x409680` therefore receives
  `rounds_from_final = Cup+0x3C - CupMatch+0x50`, yielding 1 final,
  2 semifinal, 3 quarterfinal;
- Static.dat uses one-based `round_number`, so the clean-room equivalent is
  `scheduled_matchday_count - round_number + 1`;
- runtime competition `+0x18` is the negated packed competition word +15,
  already parsed as `initialization_order_value`, so Cup precedence is
  `-initialization_order_value`.

Canonical data cross-check: FA Cup is 8 rounds with packed precedence +6;
League Cup is 7 rounds with packed precedence +5.

Commit `ce419c02` carries source round number through scheduled/live Cup state
and adds `prepare_cup_ai_selection()` using the already-recovered
`cup_round_strategy_bias()`, team-rating, home/away and aggregate-deficit
components.

A separate backend boundary remains: `simulate_normal_match()` hard-codes
`build_match_phase_plan(extra_time=False, penalties=False)`. Decisive Cup
objects must not be wired through that 90-minute path until Cup
`uses_extra_time` can select the recovered extra-time phase plan.


## Gate 12 first live AI Cup execution verified - 29 September 2026

Commit `e45c02da5461bc67196e0fe86aeef53f51da304f` is the first verified
live AI domestic-Cup match path.

It composes:

- source-backed Cup AI strategy context from `ce419c02`;
- synthetic compatibility correction `6e023260`;
- the shared extra-time MatchCalculator phase plan from `25c4e5ce`;
- live scheduled Cup materialization/completion;
- both AI selections before weather;
- weather before side-0/side-1 Condition initialization;
- normal or 120-minute shared MatchCalculator execution according to
  `CupMatchRuntimeState.uses_extra_time`;
- definitive result-token completion, replay/TwoLeg lifecycle reuse;
- post-calculator Condition synchronization and home-pitch wear.

Verification: GitHub Actions ran **723 tests with 2 failures**, both the
unchanged known secondary-schedule assertions. Repository asset policy passed.

Still explicitly open before full shared gameplay: human-controlled Cup
execution, cross-competition incident/suspension date persistence, Cup gate
receipts, and post-match morale/Form.


## Gate 12 shared human PL/Cup controller verified - 29 September 2026

The live execution slice advanced through:

- `9a59dffe`: human-controlled Cup MatchCalculator/lifecycle backend;
- `fc47ab8b`: shared AI PL/Cup day execution in post-shuffle order;
- `097b0007`: tagged human pending state and schema-27 PL/Cup controller flow;
- `33111724`: deterministic mid-matchday human Cup save/reload;
- `c7583cfd`: deterministic FA Cup Replay and League Cup SecondLeg
  post-reload execution.

Verification at `c7583cfd4079e9bb58b4d93dd8efc5bd3b3282f4`: **730 tests,
2 failures**, both the unchanged known secondary-schedule assertions; asset
policy passed.

The controller no longer needs to coerce Cup identities into integer PL fixture
IDs. Pending primary matches are tagged as `premier_league` or
`domestic_cup`, and save schema 27 preserves those identities.


## Gate 12 full-primary next-match shadow verified - 29 September 2026

Commit `3291b7e1d27e3617293670ccb547bf3661c1e302` verifies the
save-persistent semantic shadow needed by the shared `0x615D10` next-team
match search.

The shadow retains every post-placement/post-shuffle primary schedule node but
does not execute unrelated competitions. It stores both ClubRefs and derives
source-backed candidate-club sets:

- type 0 direct refs are exact singleton clubs;
- type 1 winner/loser refs inherit the possible participants of their referenced
  Cup match;
- types 2/3/4 conservatively inherit possible participants from their source
  competition/context.

The date scan starts strictly after the just-played date, returns an exact next
date when a participant resolves to the target, and raises
`PrimaryScheduleResolutionPending` when an earlier unresolved symbolic node
could still contain that club. It therefore never skips a potentially earlier
primary-container fixture merely because that competition is not live yet.

Internal save schema is now **28**, and the full-primary shadow survives
roundtrip.

Verification: **735 tests, 2 failures**, both the unchanged known secondary
scheduler assertions; repository asset policy passed.

Direct executable tracing in the same slice also confirmed that primary Cup
matches reach the shared `0x404CE0` morale/Form/danger-morale routine after
the shared `0x5127A0` incident branch. Preserve that RNG order when wiring
post-match persistence.


## Gate 12 Cup gate-RNG ordering verified - 29 September 2026

Commit `5ad669d5c0569aafa75f3b190c2d71935ccd9c66` fixes a cross-system RNG
ordering boundary in live domestic-Cup execution.

- `0x513252 -> 0x5DA2F0` is after MatchCalculator and before the
  class-specific Cup completion virtual.
- AI and human Cup paths now consume the exact four `RNG(32768)` gate draws
  before `complete_scheduled_match()`.
- This prevents Cup decisive-fallback/replay completion RNG from overtaking the
  gate producer.
- Regression spies verify the four-draw suffix at the precise Cup-completion
  entry for both AI and human execution.
- GitHub Actions ran **741 tests with 2 failures**, both the unchanged known
  secondary root-order / secondary bucket-count assertions.
- Repository asset policy passed.

Special Cup revenue posting is still intentionally not guessed. Next: use the
verified full-primary schedule shadow as an all-or-nothing preflight before
shared `0x5127A0` incident persistence, then run `0x404CE0` morale/Form
only when both next-team dates are exact.


## Gate 12 shared Cup post-match preflight verified - 29 September 2026

Commit `6bfb60055938f3ad4bed5545c6cc100be0cf13bd` adds the safe
full-primary next-match preflight required before domestic-Cup incident RNG.

- both next-team dates are resolved before either side enters `0x5127A0`;
- if either side reaches an unresolved symbolic primary node, neither
  incident nor morale/Form RNG is consumed;
- when both dates are exact, home/away incidents run first, then home/away
  `0x404CE0` morale/Form in executable order;
- MatchCalculator Condition synchronization remains live in both cases;
- home pitch wear remains live because that branch is RNG-clean;
- the earlier four `0x5DA2F0` gate draws still precede Cup completion.

GitHub Actions ran **745 tests with 2 failures**, both the unchanged known
secondary scheduler assertions. Repository asset policy passed.

Next domestic-Cup-specific target: close the special gate-revenue posting
semantics without guessing the both-controlled-clubs policy. Broader primary
competition support will later reduce pending shadow lookups and allow the
shared post-match branch to execute universally.


## Gate 12 English Cup gate-policy adapter verified - 29 September 2026

Commit `f2abbff45dc95aab6eb0ecc93db0e5db4c2d4f3f` composes the
already-recovered English Cup attendance source inputs into one runtime policy
adapter.

- country-root storage order feeds the exact FanFactor selector;
- Cup round index feeds the recovered final/semi/quarter/earlier modifier;
- the host club's owning competition supplies the English valuation/division
  category;
- category selects seating reference 30/20/16/12/9 and exact 0.75 terrace
  reference;
- no special Cup revenue is posted yet.

Verification: **747 tests, 2 failures**, both the unchanged known secondary
scheduler assertions; asset policy passed.

The remaining domestic-Cup-specific finance boundary is now narrowly the
special category-1/category-2 posting policy when the Cup flag allows both
controlled participants to receive postings.


## Gate 12 Europe position-reference bridge verified - 29 September 2026

The English domestic-Cup execution slice is no longer allowed to hold the whole
gate behind one inaccessible binary detail. The remaining special Cup
category-1/category-2 both-controlled-participants posting policy is recorded as
an explicit fidelity/source-access gap: repository evidence proves the Cup
branch and independent postings, but the canonical executable/disc source was
not found in connected Google Drive, Dropbox, or ChatGPT Library during this
session, so no business-policy label is invented.

Gate 12 therefore advanced to Europe, starting from the already-canonical
startup materialization rather than rebuilding draws.

Commit `0feb1278ec2cfebc07379732a19ef8ab2f733777` implements the first
live European progression primitive:

- `CupResultRegistry` now persists rankings by
  `(competition_id, competition_context)`;
- ClubRef type 2 resolves its zero-based competition-position selector from that
  live ranking;
- missing rankings remain unresolved rather than falling back;
- rankings can be refreshed after table changes;
- internal save schema advances to **29** and roundtrips the ranking registry.

Verification: **752 tests, 2 failures**, both the unchanged known secondary
scheduler assertions; repository asset policy passed.

Next: live child/procedural-League group state and the distinct ClubRef type-3
Champions-League-group-to-UEFA resolver.


## Gate 12 European live group-state integration checkpoint - 29 September 2026

Recovery generation 66 resumed at main `ebcbaee` without rebuilding the
already-added exact-or-pending procedural League model.

Two implementation commits advance the live European bridge:

- `17250101` attaches Champions League child procedural-League state to
  `GameState` from the persisted full-primary schedule shadow. Child
  competition IDs 14 and 167 are retried independently, so phase 1 can
  materialize while phase 2 remains pending on symbolic type-2 positions.
- Recording a live group result refreshes the exact
  `(competition_id, competition_context)` ranking in `CupResultRegistry`.
  If the proven points / goal-difference / goals-for keys become ambiguous, the
  previously published ranking is withdrawn instead of leaving a stale type-2
  resolution.
- A newly exact phase-1 ranking immediately retries pending phase-2 group
  materialization without consuming startup/draw RNG.
- `0d50d17` advances the internal save schema to **30** and persists live
  procedural-League fixtures/results alongside the already-persistent type-2
  ranking registry.

The full-primary shadow remains the canonical persisted source of European
schedule identity; startup allocation, MiniLeague construction and schedule
placement are unchanged.

Exact next target after CI reconciliation: expose due European `league_match`
entries from the shuffled primary order and run them through the shared
MatchCalculator without guessing ClubRef type-3 semantics or the still-untraced
equal-key ranking fallback.


### European group ranking lifecycle correction verified

The first CI pass on the live group integration exposed that publishing a
currently-unique mid-group table could resolve phase-2 type-2 refs before the
source group schedule was complete. `f81b1b61` corrects that lifecycle:
position rankings are now progression-visible only after every group fixture is
finished. `867262db` verifies the corrected behavior.

GitHub Actions at `867262db85c2955eea56e277718df13773d847cc` ran
**762 reconstruction tests with 2 failures**, exactly the two unchanged known
secondary-schedule assertions. Repository asset policy passed.

Exact next target: add European child `league_match` entries to the exact
post-shuffle primary execution order and connect their scored results to the
now-verified procedural-League state.


### 2026-09-29 - Gate 12 European type-3 UEFA dependency closed

- Resumed from current GitHub state after stale-worker recovery; main had
  already advanced through European knockout AI execution, human primary
  routing and generic European schedule save/reload.
- Added an end-to-end regression using two live competition-14 child groups to
  derive the ClubRef type-3 second-place pool and feed it into a competition-10
  UEFA knockout.
- Corrected the regression to use the canonical primary schedule shadow and a
  matching source competition identity on reload.
- Verified checkpoint:
  `474086bb26fe7185b0022ea84568653b443d8e0f`.
- GitHub Actions reconstruction suite ran **780 tests** with only the two
  unchanged known secondary-schedule failures.
- Repository asset policy passed.
- Gate 12 now advances to the roadmap's next slice: other required English
  league/divisional structures.


### 2026-09-29 - Generic primary LeagueMatch bridge verified

- Generalized the Europe-specific live procedural-League materializer into
  `refresh_primary_procedural_leagues(competition_ids)`, retaining the
  Champions League wrapper and defaults.
- Parameterized `install_primary_matchday_order()` so source-backed
  procedural-League IDs can be exposed in canonical shuffled bucket order.
- Added a non-European synthetic competition regression proving selected
  `league_match` nodes can materialize, become due in bucket order, execute
  through the shared MatchCalculator path, and persist their live table result.
- Verified checkpoint:
  `30bba781d568098c2cd28ba8153a57710ea70f34`.
- GitHub Actions ran **781 tests** with only the two unchanged known
  secondary-schedule failures; repository asset policy passed.
- Next: prove exact English division IDs and primary/secondary schedule-container
  ownership from source evidence before wiring real divisional competitions.


### 2026-09-29 - English divisional LeagueMatch runtime verified

- Canonical competition data and the recovered DBRCompetition +0x38 schedule
  selector prove that England's root procedural Leagues are IDs **2, 3, 4, 7**
  (Division 1, Division 2, Division 3, Conference), all in the **primary**
  schedule container. No English root procedural League belongs to the
  secondary container.
- Added `partition_root_procedural_league_ids()` so container ownership is
  derived from parsed source records rather than a guessed English ID list.
- Canonical verification now asserts primary `(2, 3, 4, 7)` and secondary
  `()` for country/region 26.
- Canonical gameplay construction now includes those source-derived IDs in the
  exact primary matchday view and materializes them through the already-verified
  generic `LiveProceduralLeagueState` bridge alongside European IDs 14/167.
- Added deterministic four-division save/reload continuation coverage.
- Verified code checkpoint:
  `91008587337fd53dc55023a2a1a6508505928639`.
- GitHub Actions ran **783 tests with 2 failures**, exactly the two unchanged
  known secondary-schedule assertions. Both new English-divisional tests
  passed; repository asset policy passed.
- Evidence: `research/GATE12_ENGLISH_DIVISIONS.md`.
- Next: audit the source-backed English cross-division season transition,
  including promotion, relegation, and any playoff competitions, before
  changing club competition membership.


### 2026-09-29 - English cross-division season transition verified

- Recovered the 28-row `DBTLeagueAllocations / DBRLeagueAllocation` table
  directly from canonical `Static.dat` and instruction-closed its seven-dword
  packed layout against `FOOTBAL.EXE`.
- Proved annual finalization iterates the sorted allocation rows and exchanges
  the selected clubs' **current competition memberships** one slot pair at a
  time. This is the real promotion/relegation mechanism, not advisory metadata.
- Canonical English rows prove the exact PL/D1/D2/D3/Conference/Conference 2
  movement rules plus the Division 1/2/3 playoff-winner exchanges. The English
  chain performs **14 paired membership swaps**.
- Added playoff competitions 11/12/13 to the existing live primary Cup runtime.
  Their source allocation instructions resolve entrants as D1 3rd-6th, D2
  3rd-6th, and D3 4th-7th.
- Preserved the canonical Conference 2 DummyLeague ranking produced during
  startup and published it to live ranking state without a second RNG pass.
- Added gameplay-safe exact Premier final ranking publication. If the recovered
  points / goal-difference / goals-scored keys leave an unresolved tie, the
  transition remains blocked rather than using the display-only club-ID
  fallback.
- Added a pure `LeagueAllocation` exchange engine, live GameState integration,
  and a separate mutable club-competition-membership map so immutable source
  Club records remain unchanged.
- Internal save schema is now **33** and preserves live club competition
  memberships across save/reload; source allocation definitions are reloaded
  from the verified database.
- Verified checkpoint:
  `64baafb8772cc7d6a003ed92c6df41eec41c33a9`.
- GitHub Actions ran **792 tests with 2 failures**, exactly the two unchanged
  known secondary-schedule assertions. Repository asset policy passed.
- Evidence: `research/GATE12_ENGLISH_SEASON_TRANSITION.md`.
- Next: trace and implement original next-season regeneration from the
  post-transition memberships. Do not reuse stale prior-season schedule state
  or rerun Conference 2 startup ranking outside the original rollover order.


### 2026-09-29 - Annual primary season regeneration primitive verified

- Continued Gate 12 from the verified English membership-transition checkpoint.
- Corrected an annual calendar fidelity issue: primary `0x615950` skips the
  actual Gregorian **25 December**, not a permanently hard-coded
  week-25/weekday-1 coordinate. The 2001/02 season therefore moves
  week 25 / weekday 2.
- Direct annual/startup tracing proves `League::init 0x4F5150` uses shipped
  real fixtures only on mode-1 first-season setup. Annual mode 0 always takes
  procedural builder `0x6170F0`, including Premier League ID 0.
- Instruction-closed `0x615AE0` as the same per-bucket Fisher-Yates already
  modeled by `shuffle_primary_schedule_buckets()`; annual rebuild consumes a
  fresh bucket-order RNG stream after competition initialization.
- Added `reconstruction/season_regeneration.py`, a non-mutating annual primary
  materializer that overlays live post-promotion club memberships, treats all
  Leagues procedurally, uses the new season calendar, and carries one caller
  CRT stream through competition construction and bucket shuffle.
- Synthetic regression proves a promoted club replaces a relegated club in the
  year-two Premier League schedule and no `fixed_league_match` nodes are
  reused.
- Verified code checkpoint:
  `09a5c269e82da597f114b66e71b1416de7f14f2b`.
- GitHub Actions ran **797 tests with 2 failures**, exactly the unchanged known
  secondary-schedule assertions. Repository asset policy passed.
- Evidence: `research/GATE12_NEXT_SEASON_REGENERATION.md`.
- Next: close cross-season Cup qualification/enumeration and DummyLeague
  regeneration semantics before atomically replacing live GameState season
  objects.


### 2026-09-29 - Annual qualification recovery reconciliation

- Recovery generation 71 resumed from main
  `17cdca03bcda376df8acaf807763c386bcb8cc1c` without replaying the already
  persisted annual Cup/DummyLeague source work.
- The recovered branch already proved that annual type-3 League/Dummy sources
  require finished-season rankings, annual Cup sources require the just-finished
  two-slot Cup enumeration, and Conference 2 is invalidated and lazily re-sorted
  from post-swap membership when the new FA Cup first consumes it.
- Added a regression for the new
  `primary_mode0_root_finalization_order()` helper. It proves
  `0x616A70 -> 0x411150` preserves country source order while reversing the
  per-country root initialization chunk.
- Verified code checkpoint:
  `cb4f8abd41c0ac5ff3cf7df03d0295393ab7b8ec`.
- GitHub Actions ran **802 tests with 2 failures**, exactly the two unchanged
  secondary-schedule assertions. Repository asset policy passed.
- The remaining source-level blocker before a live annual qualification
  snapshot is deliberately narrower: the repository does not yet record which
  positional slot, `Cup+0x40` or `Cup+0x44`, receives the completed result
  club versus the opposite/finalist path at `0x4F8F80`. That ordering will
  not be guessed.


### 2026-09-29 - Atomic annual primary runtime replacement verified

- Closed the remaining positional Cup finalization ambiguity from canonical executable evidence: 0x4F8F80 writes the completed result/winner club to Cup+0x40, then stores the opposite final participant at Cup+0x44. 0x4F5770 enumerates those slots as (winner, loser).
- Concurrent Gate-12 work added a strict live annual qualification snapshot: required League/Dummy rankings and required Cup final pairs must be present; missing live state raises rather than falling back to shipped historical qualification values.
- Added a year-two Premier League compatibility projection: annual procedural competition-0 league_match nodes are converted into a fresh PremierLeagueState using emission identity plus schedule-index matchdays, so the human/AI/table interface continues without reusing 2000/01 fixed fixture rows.
- The shared primary-order bridge now tags both first-season fixed PL nodes and annual procedural PL nodes as premier_league, and reconstructs exact shuffled per-matchday PL scheduler order from either representation.
- Added a non-mutating English membership-transition preview, so annual qualification capture, promotion/relegation, materialization and state replacement can validate before live membership is changed.
- GameState.install_annual_primary_regeneration() constructs a fresh Premier League, Cup registry/schedules, procedural-League set, full primary shadow, matchday order and PL scheduler order before one assignment boundary. Old results, Cup outcomes/rankings, schedule state and prepared match environments are not retained.
- HumanGameplayController.regenerate_annual_primary_season() captures qualification before membership exchange, materializes on a cloned controller match_rng, installs the season atomically, and commits the CRT state only after success. A failed preview/materialization consumes neither live state nor live competition/match RNG.
- Source round/allocation definitions are reattached from the verified database after save/reload rather than duplicated in the save payload.
- Verified checkpoint: 3e571f6b3cc4273e7542c96577522f2435b94699.
- GitHub Actions ran **812 tests with 2 failures**, exactly the two unchanged known secondary-schedule assertions. Repository asset policy passed.
- Canonical annual qualification source classes are now bounded: played Leagues (0, 17, 21, 27, 31, 40, 50, 54) and 44 DummyLeague sources. Canonical startup already makes the played sources live.
- Next: make the complete annual qualification snapshot available in a real canonical season. Preserve/publish every required DummyLeague ranking with no extra RNG, then make required Cup sources (1, 5, 9, 10, 19, 23, 33, 91, 98, 101) live through their finals so the rollover transaction can run without a shipped-data fallback.


### 2026-09-30 - Annual qualification-source continuity verified

- Recovery generation 73 resumed from main
  `3c90bd77d074c65e53dc373d1033c6225413fb1c` and preserved the already
  persisted qualification-Cup and DummyLeague work.
- Confirmed all required startup DummyLeague rankings were already published
  from the one canonical lazy-sort pass, and the additional annual Cup sources
  now have live runtime ownership, human/AI routing, final-pair extraction, and
  schema-34 persistence.
- Found and fixed a cross-season continuity defect in
  `HumanGameplayController.regenerate_annual_primary_season()`: canonical
  startup kept every played annual type-3 League source live, but the default
  year-two installation retained only English roots plus Champions League child
  groups. Annual regeneration now derives the played qualification-source set
  from the canonical allocation requirements and keeps those Leagues live
  without duplicate IDs.
- Added regression coverage proving the default rollover carries played annual
  sources into the new primary runtime. Also completed the synthetic
  qualification-snapshot fixtures with the separate qualification-Cup owner
  introduced by schema 34.
- Verified code checkpoint:
  `39d8e4ec4bfccea35671ca30c8dfee3505bcf1b9`.
- GitHub Actions ran **817 tests with 2 failures**, exactly the two unchanged
  known secondary-schedule assertions. The new annual continuity and
  qualification-snapshot tests passed; repository asset policy passed.
- Next: execute a real canonical primary season through every required
  played-League ranking and Cup final, capture the complete live qualification
  snapshot, then perform the atomic year-two regeneration and verify the new
  primary runtime end to end.


### 2026-09-30 - Qualification Cup autonomous primary routing verified

- Traced the live primary AI-day path after the annual qualification-Cup owner
  work. The scheduler already tagged qualification-Cup entries and the generic
  match dispatcher could execute them, but
  `GameState.primary_entries_due_today()` omitted the qualification owner.
  A calendar-driven season therefore would have silently skipped Cup sources
  19/23/33/91/98/101.
- Added the missing due-owner projection and a focused regression proving a
  scheduled qualification-Cup entry becomes due through the global primary
  matchday order.
- Verified checkpoint:
  `e0a69e8e0d65b9549363e90ace8ee6e68fe74e67`.
- GitHub Actions ran **818 tests with 2 failures**, exactly the two unchanged
  secondary-container assertions. The new qualification-Cup routing test
  passed; repository asset policy passed.
- Full-season tracing exposed the next narrow scheduler boundary: dynamic FA
  Cup replays are inserted into the live Cup owner and full-primary shadow, but
  not yet into `primary_matchday_order`. Source evidence proves
  `0x5139BA -> 0x615A60` inserts the replay and proves its date, but the
  repository does not yet prove same-day linked-list insertion order after the
  initial bucket shuffle. Do not guess append/prepend semantics.
- Next: close `0x615A60` dynamic replay insertion ordering from source-backed
  evidence, integrate that exact order, then run the real canonical annual
  qualification + atomic rollover audit.


### 2026-09-30 - Canonical annual rollover audit staged behind replay-order guard

- Traced the autonomous primary-season path far enough to expose one remaining
  scheduler-fidelity boundary: runtime FA Cup Replays are created through
  `0x51392A..0x5139BA -> 0x615A60` after the startup primary bucket shuffle,
  while persisted Gate-4 evidence proves head insertion only for the different
  startup routine `0x615950` before `0x615AE0`. No persisted instruction
  trace proves the post-shuffle same-day insertion position of `0x615A60`.
- Corrected the full-primary shadow documentation so its tuple prepend is not
  misrepresented as scheduler-order evidence.
- Searched repository research/history, connected Dropbox, connected Google
  Drive, and the current execution workspace for the authorized canonical
  executable or a saved `0x615A60` trace. None was accessible in this session.
- Added an explicit fidelity guard: if a dynamic FA Cup Replay reaches its due
  date without a source-ordered primary scheduler entry,
  `GameState.primary_entries_due_today()` raises instead of silently skipping
  the replay or guessing append/prepend semantics.
- Added regression coverage for that guard.
- Added `reconstruction/canonical_annual_rollover_audit.py`. It constructs the
  canonical runtime from the authorized game directory, advances only through
  the shared primary AI scheduler, waits for both the complete live annual
  qualification snapshot and English transition, then performs the existing
  atomic regeneration and validates year-two membership, RNG, Premier League,
  primary-order, and played annual-source continuity.
- Verified code checkpoint:
  `70307af0549f6bacd4bc1951e3cdb6ef63df0c5b`.
- GitHub Actions ran **819 tests with 2 failures**, exactly the two unchanged
  secondary-container assertions. The new replay guard passed; repository asset
  policy passed.
- The audit has not been run against canonical game data because the authorized
  FM2001 files are not currently accessible through GitHub, Drive, Dropbox, or
  the execution workspace.
- Next: recover/source-close exact `0x615A60` dynamic replay insertion order,
  then run the canonical annual audit against the authorized game directory and
  close the year-two Gate-12 proof if it passes.


## Gate 12 completion - canonical annual rollover passed (30 September 2026)

Gate 12 closed after the authorized canonical real-data season completed the
full annual qualification dependency graph and atomically generated year two.

Key evidence:

- fresh-game calendar corrected to the recovered 4 July 2000 startup boundary;
- annual Cup child procedural Leagues derived from source relationships, adding
  WCC group phase 192 alongside Champions League phases 14/167;
- two-leg final enumeration corrected to use the unique decisive outcome in the
  highest Cup round;
- player source identity preserves the raw joined-current-club date across
  internal save/reload;
- recovered League comparator 0x4F45E0 supplies the short-name byte-string
  tie-breaker to European group rankings;
- complete qualification captured 4 June 2001 after 335 simulated days;
- all ten annual Cup sources and all required played/DummyLeague rankings were
  present;
- atomic rollover applied 28 membership changes, consumed 15,539 annual draws,
  moved controller RNG 0xCE9A6E40 -> 0x6F763739, produced 380 new Premier
  League fixtures over 150 primary-order dates, and retained every played
  qualification-source League.

Full reconstruction suite at implementation checkpoint 6a966c0 ran 828 tests
with exactly the two pre-existing secondary-schedule failures. Repository asset
policy passed.

See `research/GATE12_COMPLETION_AUDIT.md`.

Gate 13 is now active. Exact next slice: inventory and restore the original
main-menu / TeamSelect presentation using authorized original resources while
keeping presentation separate from the stable simulation backend.


## Gate 13 front-end foundation checkpoint - 30 September 2026

- Re-read only the persisted front-end/TeamSelect executable evidence needed by
  the active gate.
- Confirmed the ordinary initial PStartMenu is constructed inline immediately
  after `PREMINTRO.TGQ`; later navigation identifies it as screen `0x323`.
- Confirmed PStartMenu event/control ID `2` is the New Game path into
  TeamSelect.
- Confirmed TeamSelect control `0x29` returns to PStartMenu and control
  `0x2A` enters the recovered Start/Continue path `0x4C41C0`; the latter is
  the embedded `Button@ease_2001` at TeamSelect `+0x3690`.
- Confirmed the current Tk prototype still couples widgets directly to
  `HumanGameplayController`; Gate 13 will introduce a presentation/navigation
  boundary instead of duplicating simulation logic.
- The authorized 511 MB FM2001 source archive is available again. The current
  file service can materialize it, but this recovery execution runtime cannot
  inspect the mounted ZIP bytes and the file service itself does not parse ZIP
  contents. No original UI asset was guessed or imported.
- Added `research/GATE13_FRONTEND_FOUNDATION.md` as the canonical first
  Gate-13 presentation checkpoint.
- Next: regain byte-level archive access, inventory the exact PStartMenu /
  TeamSelect graphics, strings and layout resources, then import the minimum
  original slice with provenance before implementing recognizably original
  rendering.


## Gate 13 navigation boundary CI checkpoint - 30 September 2026

- Added `reconstruction/front_end_state.py` as a presentation-only state
  boundary for the first recovered original front-end slice.
- Preserved the confirmed original identifiers literally:
  PStartMenu screen `0x323`, New Game control `2`, TeamSelect Back
  `0x29`, and TeamSelect Start/Continue `0x2A`.
- Unknown controls fail closed rather than receiving invented behavior.
- TeamSelect Start/Continue emits a presentation/application command and does
  not import or execute gameplay/simulation code.
- Added five focused unit tests in `reconstruction/test_front_end_state.py`.
- GitHub Actions at checkpoint
  `ffcbbccfd0601b91a19415e7f1b4503de0785bd5` ran **833 tests with 2
  failures**, exactly the two unchanged secondary-schedule assertions:
  `test_secondary_root_order_uses_same_crt_qsort_then_mode_filter` and
  `test_secondary_container_bucket_counts_reach_canonical_staff_seed`
  (280 recovered vs 262 expected). The new Gate-13 tests passed.
- Repository asset policy passed.
- No original graphic/layout resource has yet been imported or replaced. The
  next fidelity task remains byte-level inventory of the authorized PStartMenu /
  TeamSelect source resources.


## Gate 13 secondary visual-reference checkpoint - 30 September 2026

- Located a public screenshot of the original PC PStartMenu showing the blue
  technical-grid/wireframe presentation, central FOOTBALL MANAGER 2001 mark,
  and visible `START NEW GAME`, `CONTINUE`, `LOAD GAME`, and
  `QUIT TO WINDOWS` buttons.
- Located the corresponding team-selection screenshot showing the blue
  competition hierarchy, yellow selected row, Premier League identity panel,
  `MAIN MENU`, `START GAME`, and original pointer-instruction callouts.
- Cross-checked the visuals against the already-proven PStartMenu screen
  `0x323`, New Game ID `2`, TeamSelect Back `0x29`, and
  Start/Continue `0x2A`.
- Recorded the screenshots only as secondary visual evidence in
  `research/GATE13_VISUAL_REFERENCE.md`. They are not imported assets and
  their 512x512 web representations are not treated as canonical coordinates.
- Reconfirmed primary source-disc evidence for
  `FM2001_Art/Generic/bground.444`: 800x600 and SHA-256
  `9db0d71daf70d77b4f5f2307304bb8c5eac4ee3a07a85f2828b570fbbf3b7fb9`.
- Exact shipped UI asset extraction remains the next dependency.


## Gate 13 source-inventory dependency tooling - 30 September 2026

- Added `reconstruction/gate13_source_inventory.py` so the authorized source
  archive can be inventoried deterministically as soon as byte-level access is
  available.
- The tool supports extracted directories, direct ZIP members, supported disc
  images, and optional nested-disc inspection through 7-Zip without placing raw
  disc images in Git.
- It carries the already-proven `FM2001_Art/Generic/bground.444` path,
  SHA-256 and 800x600 header as a provenance check.
- Candidate discovery deliberately includes the complete
  `FM2001_Art/Generic/` directory plus conservative presentation-name hints;
  it does not invent final asset identity from screenshot appearance.
- Added six unit tests covering path normalization, generic front-end
  inventory, direct ZIP hashing, nested-disc dependency reporting and 7-Zip
  listing parsing.
- The current ChatGPT execution container still cannot open the materialized
  511 MB source ZIP, so the tool has not yet been run against Daniel's
  authorized archive in this session.


## Gate 13 source-inventory CI checkpoint - 30 September 2026

- GitHub Actions verified `4067b9a05ebe35b585e70b682fbf9e958e1dce87`.
- All six new `test_gate13_source_inventory` tests passed.
- The full reconstruction suite ran **839 tests with 2 failures**, still exactly
  the unchanged secondary root-order and secondary bucket-count assertions.
- Repository asset policy passed.
- The Gate-13 source-inventory utility is therefore verified independently of
  the current source-ZIP mount limitation.


## Gate 13 provenance-safe asset importer - 30 September 2026

- Added `reconstruction/gate13_asset_import.py` for the deliberate import step
  after source inventory/staging.
- The importer rejects archive/disc containers and path traversal, enforces the
  repository's 95 MiB tracked-file limit, preserves the original source-relative
  path under `original_assets/source/`, computes SHA-256, and updates
  `original_assets/MANIFEST.md`.
- The known `bground.444` path receives stricter validation: the import must
  match the already-recorded canonical SHA-256 and 800x600 header before any
  repository copy is made.
- Added five tests covering destination/provenance layout, container rejection,
  manifest insertion, byte-identical copying and bad-background rejection.
- No original asset has been imported yet because source ZIP bytes remain
  inaccessible to this ChatGPT execution runtime.


## Gate 13 asset-import CI checkpoint - 30 September 2026

- GitHub Actions verified `70f81a041eb372b902cbeb8087979882d66d7233`.
- All five new `test_gate13_asset_import` tests passed.
- The full reconstruction suite ran **844 tests with 2 failures**, still exactly
  the unchanged secondary root-order and secondary bucket-count assertions.
- Repository asset policy passed.
- The navigation boundary, source-inventory utility, and provenance-safe asset
  importer are now all independently regression-covered. No original asset has
  yet been imported because this recovery session's container/Python runtime
  returns a container-level `ClientError` when opening the materialized
  511 MB source ZIP.
- Historical project evidence confirms the prior successful source-access path:
  materialize the same Library archive, extract the raw disc image, convert its
  MODE1/2352 sectors to temporary ISO9660, then inspect/extract the authorized
  files. The next source tooling should reproduce that proven conversion path
  rather than re-investigate the already-bounded front-end contract.


## Gate 13 raw MODE1/2352 source conversion tooling - 30 September 2026

- Historical project evidence repeatedly records that the authorized Library
  archive contains a raw **MODE1/2352** disc image and that successful earlier
  source recovery converted it transiently to ISO9660 before file extraction.
- Extended `reconstruction/gate13_source_inventory.py` to reproduce that
  exact representation boundary instead of assuming 7-Zip can read the raw
  BIN directly.
- The converter validates each 2352-byte Mode-1 sector's standard sync pattern
  and mode byte, then writes only the 2048-byte user-data payload beginning at
  offset 16. The raw source is never modified or committed.
- Deep ZIP inventory now extracts nested disc-image members with Python's ZIP
  reader, detects raw Mode-1 BIN images, converts them to a temporary ISO, and
  then hands that ISO to the existing filesystem inventory path.
- Added three focused conversion/detection tests in addition to the existing
  Gate-13 source-inventory tests.


## Gate 13 MODE1 conversion CI checkpoint - 30 September 2026

- GitHub Actions verified `9a6bd853010e6492f3f96f89e68dc0f0dea68e3a`.
- All three new MODE1/2352 conversion/detection tests passed, together with the
  existing Gate-13 source-inventory tests.
- The full reconstruction suite ran **847 tests with 2 failures**, still exactly
  the unchanged secondary root-order and secondary bucket-count assertions.
- Repository asset policy passed.
- The historically documented raw-disc conversion dependency is now
  regression-covered. Remaining source-access tooling can focus on the
  resulting ISO9660/Joliet filesystem rather than raw-sector interpretation.


## Gate 13 durable-source recovery and native ISO integration checkpoint - 30 September 2026

- Read the new durable source locator and resolved the canonical private Library
  archive at
  `/FM2001/Original Source/The-F-A-Premier-League-Football-Manager-2001_Win_EN_Disc-Image.zip`.
- Library metadata matched the recorded identity exactly:
  `file_00000000010c8209961739423e78473b`,
  `libfile_0ce96709612c81919f30acce4b4bdfbd`, and
  **511,121,336 bytes**.
- Materialization itself succeeded and reported the raw ZIP at
  `/mnt/data/fm2001-source/The-F-A-Premier-League-Football-Manager-2001_Win_EN_Disc-Image.zip`.
- The current CAAS/container runtime still fails with a container-level
  `ClientError` even for a simple existence/listing operation on that
  materialized path. This distinguishes a working persistent source locator and
  successful Library materialization from the remaining execution-container
  byte-access failure.
- Added a read-only repository-native ISO9660/Joliet path to
  `reconstruction/gate13_source_inventory.py`. ISO filesystem inventory and
  candidate extraction no longer require 7-Zip after MODE1/2352 conversion.
- Deep ZIP inspection can now extract a nested raw MODE1/2352 BIN, convert it
  to temporary 2048-byte ISO sectors, and pass the result to the native
  `IsoImage` reader. Non-ISO container formats retain 7-Zip as an optional
  fallback.
- Added regression coverage for direct native Joliet inventory/extraction and
  for nested ZIP -> MODE1/2352 -> ISO9660/Joliet inventory without 7-Zip.
- Implementation commits:
  `784a9095f072f25c6980fe0ffc346e9d8db67576` and
  `971bea6ce8caffa778cd713d1e0718907154f32d`.
- GitHub Actions had not yet reported workflow runs/statuses for those two
  commits at checkpoint time, so this entry does **not** promote them to the
  latest CI-verified baseline. The prior verified baseline remains the
  847-test MODE1 checkpoint until CI evidence is available.


## Gate 13 native ISO inventory CI verification - 30 September 2026

- GitHub Actions run `36679027696` verified
  `971bea6ce8caffa778cd713d1e0718907154f32d`.
- The full reconstruction suite ran **851 tests with 2 failures**, exactly the
  two unchanged secondary-schedule assertions:
  `test_secondary_root_order_uses_same_crt_qsort_then_mode_filter` and
  `test_secondary_container_bucket_counts_reach_canonical_staff_seed`
  (280 recovered vs 262 expected).
- Both newly added Gate-13 source tests passed:
  `test_builtin_iso_reader_inventories_and_extracts_candidate` and
  `test_deep_zip_mode1_inventory_no_longer_requires_7zip`.
- Repository asset policy passed for the implementation checkpoint.
- This promotes `971bea6` to the latest verified Gate-13 implementation
  baseline. The remaining blocker is not source location or source-path
  tooling: the persistent Library file resolves and materializes successfully,
  while the current CAAS execution container still raises `ClientError`
  before it can read the materialized bytes.


## Gate 13 complete disc-catalog checkpoint - 30 September 2026

- Extended the native ISO9660/Joliet source inventory so a deep source run now
  records **every file on the recovered disc filesystem**, not only files that
  match Gate-13 presentation-name heuristics.
- Each catalog entry records normalized source path, exact byte size, and ISO
  extent. Candidate classification remains separate, preserving the distinction
  between complete source evidence and heuristic prioritization.
- This is required for opaque screen/layout/string resources whose filenames may
  not include terms such as menu, team, start, or button.
- Added regression assertions proving that the synthetic nested
  ZIP -> MODE1/2352 -> ISO9660/Joliet path reports the full disc catalog.
- Implementation/test commits: `608fadd34cedd0759992e0decf143e05cc3032ac`
  and `a07d23d7bb2014078bcc82ca5cf2c360b94a0aca`.
- GitHub Actions run `36683075430` ran **851 tests with 2 failures**, exactly
  the two unchanged secondary-schedule assertions. The deep Gate-13 source
  inventory test passed, and repository asset policy passed.
- The remaining external dependency is still CAAS byte access to the already
  resolvable/materializable private Library ZIP; no source re-upload is needed.


## Gate 13 exact source-selection checkpoint - 30 September 2026

- Added repeatable `--extract-path <source-relative-path>` support to the
  Gate-13 source inventory so opaque files discovered from the complete disc
  catalog can be selected intentionally without extracting unrelated contents.
- Exact path selections are recorded in the JSON report for reproducibility.
- A selected exact path overrides heuristic classification with
  `candidate_reason = "explicit-path"`.
- Missing requested disc paths now emit an explicit warning instead of silently
  producing an empty staging set.
- Cleaned duplicated/stale Gate-13 source-inventory documentation in
  `reconstruction/README.md`; the documented MODE1/2352 -> ISO9660/Joliet
  path now correctly uses the repository-native reader, with 7-Zip described
  only as an optional fallback for other image formats.
- Implementation/test commits:
  `14e0986da1f8dd385eac1dd34a62ef9f5f69482c`,
  `cdf8b622ae736437a745dfbb1de30cfee7482f02`,
  `57cf974f81c999f308a3930dae967efc32caac36`, and
  `657065478a9edf3ce930b1cd2e15e28b93baee28`.
- GitHub Actions run `36683324250` ran **854 tests with 2 failures**, exactly
  the two unchanged secondary-schedule assertions. All three new exact-path
  tests passed, and repository asset policy passed.
- The source toolchain is now ready for a working execution container to:
  (1) materialize the durable Library ZIP, (2) emit the full disc catalog,
  (3) identify PStartMenu/TeamSelect resources, and (4) selectively stage only
  those exact resources for provenance import.


## Gate 13 saved-catalog query checkpoint - 30 September 2026

- The CAAS execution container remains globally unavailable: even a control
  command containing only `printf 'container-health'` returns the same
  container-level `ClientError`. The authorized Library ZIP still resolves and
  materializes successfully, so this remains an execution-environment outage,
  not a lost-source condition.
- Added `reconstruction/gate13_catalog_query.py` so a successfully generated
  full-disc Gate-13 report can be searched repeatedly without re-reading or
  reconverting the 511 MB source archive.
- The utility filters the persisted `disc_files` catalog by case-insensitive
  substring, extension, top-level directory, and regex, and can summarize
  top-level directory and suffix counts to expose likely UI/layout/string
  resource families.
- Added four regression tests covering combined filters, regex selection, and
  catalog summaries. Updated `reconstruction/README.md` with the query and
  exact-path selection workflow.
- Implementation/test commits:
  `f40564b486e612169099f30fbd3ed5e35dc09178` and
  `964d9389454109f9abf498d5b7d6cb5a97696908`.
- GitHub Actions run `36685634820` ran **858 tests with 2 failures**, exactly
  the two unchanged secondary-schedule assertions. All four new catalog-query
  tests passed and repository asset policy passed.
- Next real-source sequence remains: materialize the durable Library ZIP in a
  functioning container -> deep inventory once -> query the saved full catalog
  iteratively -> exact-path stage the minimum PStartMenu/TeamSelect resource
  slice -> provenance import.


## Gate 13 query-to-staging and search-plan checkpoint - 30 September 2026

- Extended the saved-catalog workflow so `gate13_catalog_query.py --paths-only`
  emits exact source-relative paths, one per line.
- Extended `gate13_source_inventory.py` with repeatable
  `--extract-path-file` support. UTF-8 path lists ignore blank lines and
  `#` comments, normalize separators, and merge with direct
  `--extract-path` selections.
- Added focused regressions for both path-list emission and path-list loading.
- GitHub Actions run `36685946489` ran **860 tests with 2 failures**, exactly
  the two unchanged secondary-schedule assertions. The new query-to-staging
  tests passed.
- Updated `reconstruction/README.md` with the reproducible sequence:
  query saved full catalog -> emit paths-only shortlist -> feed shortlist back
  through `--extract-path-file` -> stage only selected resources.
- Added `research/GATE13_CATALOG_SEARCH_PLAN.md`, which records the first
  evidence-bounded real-catalog search sequence. It separates confirmed source
  anchors and executable identities from screenshot-only UI labels, so visible
  strings are used as search hints rather than guessed filenames.
- Current container status is unchanged: a trivial control command still
  returns CAAS `ClientError`, while the durable Library ZIP remains resolvable
  and materializable. Therefore real-disc byte inventory is still the exact
  external dependency; no source re-upload is required.


## Gate 13 exact-only asset staging - 30 September 2026

- The active source inventory still cannot run against the authorized ZIP because
  both the container shell and Python kernels return CAAS `ClientError` even
  for trivial control operations. GitHub source and CI remain available.
- Corrected a discrepancy in the prior exact-path workflow: `--extract-path`
  previously selected named files **in addition to** all heuristic candidates.
  A new opt-in `--only-explicit` mode limits ISO/Joliet candidate reporting and
  extraction to the selected paths while retaining the complete disc-file
  catalog. It rejects empty path selections.
- Added three regression tests for selection-only staging, rejection of an
  empty selection, and preservation of the full catalog in the report.
- Code/test commits: `943ba45d132ecd1aea242ec5c1f3bf6589b9bc50`
  and `114336aceb5d0bc7a844dbd7c7d3b439ee84d50f`.
  Documentation updated in `8e87401867b36230c5b194235f89f9c26b8dee4a`.
- GitHub Actions run `36688232893`: **863 tests, 2 failures**, exactly the
  same secondary root-order and bucket-count assertions. All three new
  exact-only Gate 13 tests passed; repository asset policy passed.
- Exact next task remains real source-disc byte inventory and evidence-driven
  PStartMenu/TeamSelect asset selection, not another speculative UI design.


## Gate 13 source-access recovery and safe staging checkpoint - 30 September 2026

- Recovered canonical `main` from `5eca3ee3009e6352e567c7bea708a8f8b51e4dee` and
  reread `CURRENT_STATE.md`, continuation protocol, and the durable Library
  locator rather than restarting completed investigation.
- The exact 511,121,336-byte authorized Library ZIP still lists and
  materializes successfully. A direct file-size check still encounters
  container-level `ClientError` before byte access; the Library text
  reader does not parse this binary ZIP. No real original assets have
  been inspected or imported in this recovery.
- Found that source-path normalization retained `..` components, permitting
  unintended extraction outside a staging root for crafted nested ZIP paths.
  Reject parent traversal and drive-prefix paths before staging; this does
  not change known canonical FM2001 resource paths.
- Commits `60776deba2ed600889427fddf58ded1562ee2560` (guard) and
  `03bc53b7bb71d3af6f1452727e9857ccbb328c29` (regressions).
- GitHub Actions run `36690708130`: **865 tests, 2 failures**;
  both new source-path tests passed, and the only failures are the
  two long-standing secondary-schedule assertions. The repository
  asset-policy workflow also passed.
- Continue the exact Gate-13 dependency when executable byte access returns:
  run the native deep ZIP -> MODE1/2352 -> ISO9660/Joliet inventory;
  follow `research/GATE13_CATALOG_SEARCH_PLAN.md`; stage only the
  evidence-backed PStartMenu/TeamSelect slice with
  `--extract-path-file --only-explicit`; provenance-import the originals.


## Gate 13 verified background metadata and independent CI - 30 September 2026

- Resumed from canonical `main` checkpoint `c6e2aa387b1150e847bef9f5cb26f5954a496137`.
  The private original 511,121,336-byte Library ZIP still resolves and
  materializes, but even a trivial execution-container command fails with
  CAAS `ClientError`. No original resource bytes were inspected or imported.
- Verified from existing original-disc evidence in `EXECUTABLE_ANALYSIS.md`:
  `FM2001_Art/Generic/bground.444` is exactly **222,616 bytes**, 800x600,
  SHA-256 `9db0d71daf70d77b4f5f2307304bb8c5eac4ee3a07a85f2828b570fbbf3b7fb9`.
  Its size was not previously enforced at the initial unextracted inventory
  boundary. Added an expected-size field to the source report and a warning
  for any size mismatch visible directly from disc metadata, plus a regression.
- Added a separate Gate-13-only GitHub Actions workflow, allowing presentation
  work to report genuinely green without hiding the two known unrelated
  secondary-schedule failures in the full suite.
- Code/test/workflow commits:
  `8dd88575a0d9b0310c423704ca42f80064654abb`,
  `174136760703e3300feb3432abf526afda6f28dd`,
  `5635215678b11459b07203ee4bf2606593505a70`.
- CI: focused Gate-13 run `36693094247` **38/38 passed**;
  repository asset-policy run `36693094248` **passed**.
  Full-suite run `36693078539`: **866 tests, 2 failures**, only the
  long-standing secondary root-order and bucket-count assertions.
- Updated `GATE13_CATALOG_SEARCH_PLAN.md` with the canonical background size
  and exact-only staging flag (`4bfad7ec1564b573df54198482aa94fda3b8be42`).
- Exact next task remains the same: regain byte-level source access in a
  functioning container, run the full original-disc catalog, then identify,
  hash, selectively stage, provenance-import and bind the original
  PStartMenu/TeamSelect resources. Do not redesign substitute graphics.


## Gate 13 menu-to-gameplay application handoff - 30 September 2026

- Resumed from canonical `main` checkpoint
  `6e804c23dd12b9d11538b7e8937fc7ac48fc6996`. Verified the private
  authorized original archive still cannot be opened by the local execution
  container: a basic container-health command immediately failed with CAAS
  `ClientError`.
- Implemented `reconstruction/front_end_session.py`, an isolated headless
  application seam linking the recovered `FrontEndState` control IDs to the
  existing `HumanGameplayController` without rendering substitute graphics
  or importing simulation from the presentation-state module.
- Confirmed PStartMenu New Game event `2` constructs a new gameplay backend
  before leaving the menu; backend-construction failure keeps PStartMenu
  active. Team choice remains presentation state until the confirmed
  TeamSelect Start/Continue event `0x2A` invokes backend
  `select_club`. Rejected choices remain retryable; Back `0x29`
  clears the presentation choice without synthesizing a backend reset.
  The implementation currently supports only the Premier League backend
  subset, **not** the original complete country hierarchy.
- Added 9 targeted regression tests covering dispatch order, lazy
  production factory wiring, unsupported controls, missing and rejected
  choices, duplicate-start prevention and Back behavior.
- Source/test/workflow commits:
  `8c07cc004fb1e0bd6344ed9714ee32db20dfbe9f`,
  `91c02c17d72066e01e5d40dbaef46f1dbbd0a2be`,
  `240b08374ec42d46b33816aa907dcad7aaa6c9d8`.
  Updated focused CI path filters in
  `9154b720373125172fe3e6cc8cfa8ae22b2c35b2` so future session
  edits trigger Gate-13 checks.
- Dedicated GitHub Actions run `36694601308`: **47 of 47 focused Gate-13
  tests passed**. Asset policy run `36694601279` also passed.
  Full reconstruction run `36694465472`: **875 tests, only the two
  established secondary-schedule failures**, and all nine new bridge
  regressions passed.
- Documented the new headless seam and its current boundaries in
  `research/GATE13_FRONTEND_FOUNDATION.md` and
  `reconstruction/README.md`.
- The missing next dependency remains unchanged: open the original
  authorized disc archive in a functioning execution container, run the
  native Gate-13 inventory, extract/hash original graphics and layout,
  provenance-import the minimal first slice, and bind those resources to
  the now-tested session/navigation seam.


## Gate 13 loose-ZIP + nested-disc source staging - 30 September 2026

- Resumed from current `main` HEAD `b714ad82ab642a5b2417062ed846898f98ba72aa`.
  Confirmed `CURRENT_STATE.md` and incremented the runtime recovery
  generation to 84 rather than restarting completed Gate-13 work.
- A control container command and a control Python-kernel command still
  returned global CAAS `ClientError`. The canonical private Library ZIP was
  listed and materialized again at its known 511,121,336-byte size.
  No original source bytes were accessible through the execution runtime.
- Fixed a real source-ingestion gap: the earlier `--only-explicit` and
  `--extract-path` implementation correctly selected resources inside nested
  ISO/Joliet disc images but could not select or stage **loose, opaque
  resources directly inside the outer source ZIP**. `inventory_zip` now
  applies the same exact-path filter and byte staging for the loose layer,
  while still discovering nested disc images.
- Avoided a redundant second read/hash pass of the ZIP's loose candidates.
  The deep inventory now returns its original nested-image list from the
  first pass; a mixed ZIP regression explicitly proves the outer ZIP
  inventory is called once.
- Implementation/test commits:
  `2de3e846bfd5db0d05674d8e3467d5f7a9216bbe`,
  `0531c81089536d6fa028fdf69f6555b66c7ce1f0`,
  `da79bc53077255a91e657583761f426c1977065c`,
  `e66ae4eb39785cd0f5478921258250ecc9dd9a4e`.
  Documentation corrected in `86d67332f3fd7356275ec58ff5199023728b4200`.
- CI: focused Gate-13 run `36697061364` **50/50 tests passed**;
  repository asset-policy run `36697061327` **passed**.
  Full reconstruction run `36697061476`: **878 tests, only the two
  long-standing secondary-schedule failures**. No new failures.
- Next: execute the native deep inventory against the real authorized ZIP
  as soon as the global execution environment becomes available. Inspect
  both its direct ZIP candidates and its nested disc catalog, then follow
  `GATE13_CATALOG_SEARCH_PLAN.md` to select, hash, source-import and render
  the original PStartMenu/TeamSelect assets through the verified front-end
  session boundary. Do not recreate substitute game art.


## Gate 13 combined source-catalog and collision-safety checkpoint - 30 September 2026

- Resumed canonical main at `fc4ff776ae2f86c549eb1c1381e33a3937e9cdb0`;
  execution container and both Python runtimes still returned global CAAS
  `ClientError` even to trivial health checks, so no source files could
  be opened from the private Library materialization.
- Fixed a material discovery gap: the report now records **every outer ZIP
  member** with normalized path, byte size and disc-image classification in
  `zip_files`, alongside the full nested `disc_files` catalog. Previous
  reports omitted unrelated/opaque loose ZIP members from catalog queries.
- Queries now inspect both catalogs by default, label each match's source
  layer, support `--layer zip|disc|both`, retain compatibility with older
  disc-only reports and refuse ambiguous duplicate paths when printing a
  reusable `--paths-only` selection.
- Exact-path staging refuses case-insensitive duplicates within a ZIP,
  cross-layer ZIP-versus-ISO collisions and overwriting preexisting
  staging files. A selected disc container cannot be staged as ordinary
  UI art. Raw `.bin` files are now identified as nested disc images by a
  valid MODE1 sector signature, not extension alone, so ordinary opaque
  `.bin` interface resources remain accessible.
- Representative commits: full ZIP catalog `e5d80792e943354fd788ba980349497342089d07`;
  combined queries `1905a1d5636526c3979eb7542868b82489a3099b`;
  tests `1ac9d9f40c77f4e7adcf68370d1bac7073248589` and
  `91f800556b684f8d32c1e1bd0b245f33c81f3a46`;
  collision checks `3885baec44b8558b7ec069ccc54b55c1c502dfbe`,
  regression fixtures `d8019826bb2b6972d8b79f6277367276bffe6259`;
  signature-based raw BIN identification `22c935fe93cddb37925d0615f93001393a37b817`
  with corrected tests `19e599f34c3330a5d258902d5311649f62271ecb`.
- CI: Gate-13 run `36698353585` **61/61 passed**;
  full reconstruction run `36698353568` **889 tests, 2 failures** (only
  two established unrelated secondary-schedule expectations);
  asset-policy run `36698353633` passed. Previous intermediate run
  caught and helped correct classification of an opaque UI `.bin`.
- Next: execute the real original source inventory, use both source catalogs
  to identify authentic PStartMenu/TeamSelect resources, source-verify the
  minimal asset slice and attach it to the already-tested front-end session.


## Gate 13 direct validated MODE1/Joliet inventory - 30 September 2026

- Source archive continuity rechecked: the canonical private Library ZIP
  is still present, exactly 511,121,336 bytes and successfully
  materializes. The execution-container health/file-stat command still
  fails with global CAAS `ClientError`; no actual original source bytes
  were read this session.
- Replaced the expensive **raw MODE1/2352 -> full temporary ISO** conversion
  on the ordinary deep-inventory path with a virtual ISO9660/Joliet reader
  over the original extracted raw BIN. Before browsing it, the inventory
  validates every original physical sector, including sectors that are not
  referenced by the sampled file tree. The independent offline conversion
  helper remains available for manual comparison.
- Virtual reader `RawMode1IsoImage` supports directory descriptors,
  Joliet names, cross-sector reads and exact file extraction while rejecting
  invalid sector headers. Focused synthetic tests verify a genuine
  MODE1/Joliet sector fixture and corrupted-sector failure.
- Exact requested-path staging now emits `unresolved_explicit_paths` in
  the machine-readable JSON report. With `--require-all-explicit`, missing
  resources return a failing exit code **after the report is written**,
  so interrupted/partial asset selection is not silently accepted.
- Representative commits: `9ec674ce5294925eaf709a99ed1111b77a5a3876`
  (strict staging), `8d44283fb09be4325a4a0ce7ee238dcb8a8f022e`
  (strict regression), `d69962f275743e74cb16d6826b672c34eb43433b`
  (virtual reader), `97abf8ae69b56eac01ccaeedc8fe19421a350e23`
  (reader tests), `9e40bf7ad803d720e6ea277c212a2c6ec8891646`
  (native inventory integration), `2e25d31eaaf71ec30c4575f50b591fe57aae031d`
  (full-sector validation test), and `bf49cb5130acf450c5a578c6af9a8387332ff6f0`
  (corrected Python fixture literals).
- CI: focused Gate-13 run `36698841038`: **66/66 passing**;
  full reconstruction run `36698840900`: **894 tests, exactly the two
  already known unrelated secondary-schedule failures**;
  asset-policy run `36698841075`: passed.
- Updated `reconstruction/README.md` and the first-slice catalog
  search plan with the virtual-reader workflow and strict staging requirement.
- Next required Gate-13 dependency remains first-hand original-source
  discovery and evidence-backed PStartMenu/TeamSelect visual asset import.


## Gate 13 verified source-to-original asset provenance - 30 September 2026

- Closed a previously unguarded source-provenance transition:
  `gate13_asset_import.py --inventory-report <selected-report.json>` now
  accepts exactly one hashed extracted candidate with matching normalized
  path, staged byte size and SHA-256. It rejects ambiguous/colliding
  candidates, inventory listings without extracted bytes, tampered staged
  data, and any selected report with unresolved exact paths. Where
  `--hash-source` recorded the original outer archive's SHA-256, the
  importer retains that digest in manifest provenance notes.
- Earlier format work established that some legitimate UI data may have
  opaque `.bin` filenames. The importer now permits these **only when**
  a selected-source receipt proves the expected data is not a nested raw
  BIN disc-image container. The default source-relative validator still
  rejects `.bin` imports without this proof, and other raw containers
  stay forbidden.
- Integrated synthetic end-to-end regression covers
  `ZIP -> exact-only source inventory -> selected JSON report ->
  hash-verified opaque UI .bin import -> original_assets manifest`.
  No actual copyrighted resource was committed.
- Commits: importer `532959f2bec8e2fda31bc11d52753715ef42b016`,
  provenance/fail-closed tests `3de9ea3163e125106e74b79ae787290efc3826b7`,
  end-to-end source receipt regression
  `1cf7af7ebccba34c6f414d1c3df2f82fb2346686`.
  Updated both the reconstruction README and Gate-13 catalog plan for
  `--inventory-report` and `--hash-source`.
- CI: focused Gate-13 run `36699473176`: **71/71 passed**;
  full reconstruction run `36699473326`: **899 tests, only the same
  two established secondary-schedule failures**;
  repository asset policy `36699473263`: passed.
- The private original ZIP continues to list/materialize at the
  expected 511,121,336-byte size; global CAAS shell and Python execution
  health checks still fail. The authentic UI resource catalog, byte
  inspection and minimal visual import are therefore **not yet done**.
  This must remain the first step in the next workable execution context.


## Gate 13 original EA444 compressed coefficient / quantization recovery - 30 September 2026

- Recovered from canonical main `8a7ab48ebda52d494324e36b4b64c253e86fc8e8`
  after an extension stale-activity interruption. Reused the actual
  original source archive, original hash-verified executable, staged
  original UI assets and previous work; no reconstruction restart.
  Incremented `agent-runtime` recovery generation to **88**.
- Verified all **12/12 local source-backed tests** across the
  original `.444` compressed bitstream, exact original embedded
  `TQIA_DAT` Huffman/zigzag tables, and original sparse run/signed
  amplitude/escape coefficient parsing. Separate first-component scans
  succeeded against all **17** real first-slice original graphic assets.
- Implemented and committed
  `reconstruction/ea444_bits.py`,
  `ea444_tables.py`, `ea444_coefficients.py`,
  `ea444_quantization.py` and `ea444_quantized_block.py`
  with companion standard CI and opt-in real-source regressions;
  focused Gate-13 workflow includes all of those test modules.
- Directly recovered 64 original quantization seeds from `.rdata`
  VA `0x7DABF0` and SHA
  `6fb2af66cb6a51e4b3fa7da9bacab417fa40f180aa0c18c85adb2550c04c89eb`.
  Reconstructed exact signed x86 `IMUL/SHL/SHR/ADC` conversion from
  source values into the live fixed-point coefficient scales.
  Verified actual `main_menu_bground.444` first component has
  eight-bit DC scale 15, 14 nonzero AC, 93-bit entropy length,
  original signed grid DC 983040 and grid SHA
  `d074fa03f380438bfccbdf88dc2375f700434891889399e4750fc7bc2c75c2d7`.
- Bounded the original inverse 8×8 path: caller `0x7B95D0`
  performs eight first-pass `0x7B9360` transforms over source
  contiguous 8-element arrays into 36-byte-stride scratch rows,
  then eight second-pass `0x7B94C0` transforms. The first pass
  has an explicit DC-only shortcut at `0x7B948E`.
- Detailed firsthand address-level research and pending pixel-color
  boundaries are in `research/GATE13_EA444_DECODER_TRACE.md`.
  The private original full-disc catalog remains in the current
  execution workspace; two attempts to save a Library copy failed
  with `container_session_expired`, but the original source ZIP is
  persistently available via `ORIGINAL_SOURCE_LOCATOR.md`.
- Hosted GitHub Actions were **not** dispatched in this continuation:
  the workflow was intentionally converted to manual/PR to conserve
  included minutes. Do not present newest module tests as hosted-CI
  certified until a real run is checked.
- Exact next work: recover verified initialized inverse-transform
  constants and both original x87 8-point passes and then post-IDCT
  conditional channel/color conversion from the hash-verified original
  executable. Test actual images before claiming visual fidelity or
  declaring Gate 13 complete. Continue Gates 14–17 only after
  preceding audit.


## Gate 13 exact PStartMenu primary action recovery - 30 September 2026

- Continued after source access and EA444 pixel recovery; did not restart prior
  work. Canonical source/executable remain the verified originals.
- Recovered PStartMenu screen-specific setup `0x4C1BA0` and dispatch
  `0x4C3770`. Primary visible controls are events 1–4:
  Continue, Start New Game, Load Game and Quit to Windows.
- Direct language loader `0x635F30` proves the exact English.idx positions
  used by those four controls are 0, 1, 2 and 6 respectively.
- Exact Button@ease_2001 positions are:
  Continue `(181,478)`, Start New Game `(7,478)`, Load Game
  `(355,478)`, Quit `(181,508)`.
- Runtime atlas handle `0x946590` is initialized from original
  `GenericButtonsAndBars/button_type_1.444`; source geometry 169x575 and
  runtime initializer width/height 169x25 prove all four visible rectangles
  are 169x25.
- Common button font handle `0x9197E0` is loaded from original
  `Fonts/Zurich_BdXCn_BT_20pixel.fnt`.
- Added exact layout/action metadata and tests, recovered all four
  PStartMenu commands in `front_end_state.py`, and recorded address-level
  proof in `research/GATE13_PSTARTMENU_LAYOUT.md`.
- Separately optimized the exact EA444 inverse transform using an equivalent
  2^25 integer denominator rather than per-row Fraction allocation.
  100,000 randomized local differential cases matched the former exact
  Fraction calculation; source-backed main-menu/TeamSelect decoder tests
  remained bit-identical and completed locally in ~13 seconds for the
  inverse+decoder test modules.
- Next work continues immediately with the original Zurich 20-pixel font and
  Button@ease_2001 frame-state behavior, then full authentic PStartMenu
  composition and TeamSelect.


## Gate 13 first-screen regression and pointer integration - 30 September 2026

- Reconciled recovered original PStartMenu event 1 with the older session
  regression test: Continue, Load and Quit now have explicitly tested
  command-only dispatch, without implicit New Game backend construction.
  Added existing original menu and TeamSelect layout tests to Gate 13 CI.
  PR #5 passed focused workflow `36725002444` and asset checks, then merged
  on `main` as `b204d01189dbfa6de5a624f5f4769ffb27ea37f7`.
- PR #6, exact first-screen pointer input, adds headless mapping from the
  confirmed four PStartMenu action rectangles and two TeamSelect Back/Start
  rectangles to the existing session boundary. Background clicks and
  unrecovered hierarchy rows produce no invented event. Regression tests
  cover half-open rectangle edges, all four menu commands, and TeamSelect
  New Game/Back/Start semantics. Focused workflow `36725905158` and asset
  policy `36725904605` both passed; squash-merged as
  `bf643d3ac6a7869842770174a6d7b3477689e895`.
- Both checkpoints remain Gate 13; original font glyph metrics, button
  atlas animation-state binding, complete original graphic composition and
  hierarchy selection remain next. No new whole-suite pass is claimed.
- Authorized private source ZIP was found under its canonical Library path;
  the materialization service reported the complete archive, but local
  execution tools returned `ClientError` even on trivial echo/print. Do
  not reinterpret this temporary tooling failure as unavailable source.


## Gate 13 original font, button-atlas and menu-source integration - 30 September 2026

- Resumed from exact `main` head `2ef1d249`; found that a predecessor
  worker already committed the original EAUK 224-glyph bitmap font parser and
  original Zurich glyph-mask tests. Did not redo that first-hand recovery.
- Merged PR #7 as `973e082`: binds four executable-proven PStartMenu
  event/language indices to exact EAUK font raster masks. Corrected the
  focused workflow, which previously included `test_ea_font.py` in path
  filters but omitted it from the actual unittest invocation. Hosted
  workflow `36729337643` and asset policy `36729337666` passed.
- Merged PR #8 as `0a999a1`: checksums the original PStartMenu and
  TeamSelect button source atlases and preserves their exact 23 vertical
  RGBA frames without assigning speculative input-state semantics.
  Hosted workflow `36729704209` and asset policy `36729704079` passed.
- Merged PR #9 as `0425d80`: checksum-verified original source loader for
  global/PStartMenu backgrounds, original executable image tables,
  button atlas, Zurich font, English STR/IDX and four caption masks.
  Reuses the independently verified full 800x600 base-composition SHA
  without claiming complete source-faithful button placement/rendering.
  Hosted Gate-13 workflow `36730124709` and policy `36730124841` passed.
- Local shell/Python execution was checked again and both trivial calls
  returned `ClientError`. Opt-in first-hand licensed-source integration
  remains unrun here; canonical Library archive is still recorded for
  rematerialization. Next source-bound research is exact Button@ease_2001
  frame-state/caption alignment; meanwhile useful TeamSelect bundle work
  does not require inventing native state transitions.


## Gate 13 two-screen resource integration and exact original-file recovery plan - 30 September 2026

- PR #10 merged as `96cafb5`: original TeamSelect background overlay,
  23-frame original action atlas and 16 source-backed row origins now have
  a dedicated hash-verified resource bundle. Focused run `36730496426`
  and asset policy `36730496711` passed.
- PR #11 merged as `fccb8c2`: new first-screen presenter binds the already
  tested PStartMenu/TeamSelect source bundles to the existing session and
  original rectangle click translator. Headless tests cover original
  geometry/control resources and proven multi-screen navigation, but do not
  assign unproven native button animation frames or hierarchy team IDs.
  Focused run `36730750307` and policy `36730750418` passed.
- PR #12 merged as `4220259`: selected only ten source-backed first-screen
  original asset paths, pinned the prior first-hand source SHA-256s, and
  implemented a fail-closed canonical source ZIP/inventory/staged-byte
  validator. `research/GATE13_FIRST_SCREEN_RESOURCE_PLAN.md` contains exact
  extraction, verification and intentional provenance-import commands.
  Synthetic/report regressions passed focused run `36731158020` and
  asset policy `36731158181`. No source files were silently imported.
- The original 511,121,336-byte private ZIP was located again via Library
  listing at its canonical recorded path/ID. Trivial local shell and Python
  execution repeatedly produced `ClientError`, including a fresh shell
  retry after these merges. This blocks new original executable disassembly
  and licensed source-byte staging/real-pixel tests, not source availability
  or the already verified GitHub changes. Runtime remains working for
  normal recovery; exact next original addresses/commands are reconciled
  in CURRENT_STATE.md.


## Machine-readable Gate 13 status-mirror correction - 30 September 2026

- After the six verified Gate-13 source-backed integration pull requests and
  exact ten-asset source selection plan, found a stale top-level machine
  status discrepancy: `project_status.json` still said `current_gate=12`
  and named a superseded Gate-12 task, despite its lower-level
  `active_gate=13`, the authoritative ROADMAP and CURRENT_STATE correctly
  indicating Gate 13.
- Corrected `project_status.json` at `70f45a5348ac69172011f5231a4db5ef24839cae`
  to mark Gate 13 active, Gate 14 next, Gate 17 the sole full-mission
  completion boundary. Explicitly separated confirmed private Library
  source availability from the current execution environment's repeatable
  `ClientError` on trivial shell/Python calls. Recorded newest passing
  Gate-13 and repository policy workflow IDs and retained the last known
  full-suite two secondary-schedule failures without implying a new full
  reconstruction pass.
- This is a canonical status-consistency correction, not a Gate-13 closure,
  native-executable trace or new licensed-source run.


## Gate 13 original TeamSelect hierarchy art - 1 October 2026 (KST)

- Started from main `cb70119`; reconciled the source-critical native
  Button@ease trace still pending with the independent, existing
  TeamSelect hierarchy resource hashes and frame dimensions.
- PR #13 merged `1edb4deb1063613a92bab08c7aea9153002d76f5`:
  source-SHA-gated original hierarchy animation and bar strips,
  retained top-to-bottom source RGBA without invented animation/selection
  state, carried those source assets into the TeamSelect resource loader
  and first-screen presenter, and extended synthetic plus opt-in
  first-hand source regressions. Focused Gate-13 run `36734520993`
  and repository asset-policy run `36734520580` passed.
- The actual hierarchy-source total dimensions and pixel composition
  are still pending renewed original-byte execution. Both native shell
  and alternate visible Python trivial commands returned `ClientError`.
  Native Button@ease frame-state and caption baseline remain the exact
  critical next source trace; the Gates 13–17 mission is not complete.


## Gate 13 bounded canonical Button executable tracing preparation - 1 October 2026 (KST)

- PR #14 merged `a42782047e6cfa673ef88f36773b37bf9be63e04`:
  canonical SHA-verified PE32 i386 mapping of six previously sourced
  button/menu/font code neighborhoods, deliberately unvalidated
  raw-pointer candidate scanning, optional bounded linear disassembly,
  and private-output guard. Synthetic PE tests and opt-in original-source
  smoke tests were added; no copyrighted executable bytes or trace dump
  were imported. Focused CI `36735030753` and asset policy
  `36735030926` passed.
- Exact execution instructions and manual CFG/vtable adjudication
  procedure are in `research/GATE13_BUTTON_STATE_TRACE_PROCEDURE.md`.
  The critical actual native state mapping and font placement were not
  inferred from the scanner. Source access still awaits a usable
  container/shell after reproducible trivial `ClientError` failures.


## Gate 13 lossless original-pixel diagnostics preparation - 1 October 2026 (KST)

- PR #15 merged `addc1f2dab50fdccdf7e7517ab22bdf1fbd1a35b`:
  standard-library lossless original RGBA PNG reference exporter,
  separate source-order button/hierarchy atlas frames, uncolored
  original Zurich glyph-alpha PGM exports and JSON of recovered
  source-bound control geometry/string indices. No native animation
  frame order or baseline/color was invented. Synthetic exact-pixel
  roundtrip/private output tests passed focused CI `36735502617`
  and asset-policy run `36735502710`.
- Updated `research/GATE13_FIRST_SCREEN_RESOURCE_PLAN.md` with the
  exact private licensed-source export invocation for when the
  canonical executable and ten original first-screen files can be
  executed/staged again. The actual private original-byte export and
  direct original Button@ease control-flow trace remain outstanding;
  this implementation is deliberately a first-screen diagnostic,
  not a verified Windows 11 frontend/release.


## Gate 13 source-pixel live developer diagnostics - 1 October 2026 (KST)

- PR #16 merged `7fc92fedd6f660a878348a34a02055027b63c9cb`:
  a pure source-pixel/known-coordinate preview model and developer-only
  Tk live viewer now display the checksum-pinned original first-screen
  backgrounds and manually selected source atlas frames, route known
  control clicks through the existing original first-screen presenter,
  and isolate explicit numeric team-ID testing in an external diagnostic
  sidebar rather than inventing original TeamSelect hierarchy semantics.
  Labels remain diagnostic metadata, not visually positioned original
  glyphs. Focused mocked-Tk/synthetic CI `36736154217` and asset-policy
  check `36736154071` passed.
- The actual original licensed graphics/Windows desktop smoke test,
  original idle/hover/pressed atlas-frame mapping, font baseline/color,
  complete hierarchy interaction, other management screens and Gate 13
  audit are still outstanding. This is a development-only visual bridge,
  not a verified replacement/release UI.


## Gate 13 new original Button trace candidates and strict firsthand-source audit - 30 September 2026 UTC

- Startup confirmed main `4fb9221cf4701d3dcc65cfd939d346700d0933eb`,
  the predecessor worker's original-pixel live developer viewer milestone,
  and current Gate 13. The newly added debug viewer/exporter were
  already merged; did not repeat them.
- Direct execution of trivial shell commands returned `ClientError`
  twice, so no new native executable disassembly or original first-screen
  licensed-asset run was claimed. Previous private Library archive
  retention remains the source recovery route.
- PR #17 merged `4f98316c2be65e0e42925006dbfa045d410483f6`:
  added bounded first-screen **class-vtable** raw-pointer candidates and
  optional Capstone candidate-only near-direct CALL/JMP leads to known
  code and plausible class-vtable text targets. Updated the canonical
  private executable source-trace CLI and analyst instructions. All
  generated edges are labeled unconfirmed; vtable identity, native
  Button@ease frame state and Zurich text semantics are NOT claimed.
  Focused Gate-13 run `36739026011` and asset-policy run
  `36739026154` both passed, with Capstone installed in focused CI.
- PR #18 merged `9682a50d0d670b41eb77dc643a293085be4043b2`:
  provides a single private, fail-closed first-hand audit for the
  canonical actual original ZIP, the precise ten staged Joliet resources,
  verified exact original executable, decoded first-screen background
  pixels, four recovered original Zurich masks, both original 23-frame
  action atlas families and original hierarchy art. It writes a small
  private source-evidence receipt only when the *actual files* validate.
  Hosted synthetic rejection tests passed focused run `36739577933`;
  asset-policy run `36739577928` passed. **No real licensed-original
  audit was run in this recovery.**
- Updated `research/CURRENT_STATE.md` with exact native source-trace,
  real-disc audit, provenance import, and remaining Gate 13-17 actions.
  This is source-ready tooling, not a Gate 13 closure or verified
  Windows 11 release.

 
## Gate 13 recovery: source-order hierarchy diagnostics and original Button input-anchor consolidation - 1 October 2026 KST

- Canonical starting main `40660eee5487a21d35e377e7040a0f638d6c3d56`, Gate 13
  active; recovery generation 96 on `agent-runtime`.
- Again tested trivial direct shell execution: `container.exec` returned
  `ClientError`. Original source ZIP remained listed at the exact
  private Library `/FM2001/Original Source/` path. Therefore NO new
  actual executable disassembly, original ZIP staging or first-hand
  real-asset pixel audit is claimed in this recovery.
- PR #19 `b488bf5380b5ef65bc833832b0a8e97acbeb5690` adds private
  developer-only independent, lossless, source-indexed inspection of
  original TeamSelect hierarchy animation and bars in a separate
  sidebar. Native image positions, frame-state meanings, country/team
  labels and click behavior remain unresolved. Initial focused CI
  `36742266401` found a mocked-Tk image-clearing assertion error;
  after correcting it, focused CI `36742383607` and asset policy
  `36742383367` passed. Only the corrected branch was merged.
- Previous canonical-executable research already recorded
  `Button@ease_2001::input` at `0x64F7A0` and a real TeamSelect
  owner click path, with state-bit helpers at `0x64F3E0`,
  `0x64F710` and `0x64F750`. The recent source inspector had
  been missing these **existing original-byte facts**. PR #20
  `38b6f3a65ed567fd2f33846d6bace7669b62c90c` now feeds
  them to bounded canonical-code windows and optional direct-call
  candidate scans, and consolidates the concrete owner/bit-state
  graph in `research/GATE13_BUTTON_STATE_TRACE_PROCEDURE.md`.
  Focused CI `36742776548` and asset policy `36742776481`
  passed.
- Exact next source-critical step: restore original binary execution
  access; inspect the already confirmed Button input/state code and
  separately resolve the true native **draw frame selection** and
  Zurich caption origin/colors, followed by strict physical canonical
  ten-asset source-byte/pixel audit, deliberate provenance import,
  completed original management presentation, Gate 13 audit and
  Gates 14-17 through a real Windows 11 release.

 
## Gate 13: calibrated original Button RTTI/vftable inspection - 1 October 2026 KST

- Recovery started at main `a0b978fc53a0bff2e596105f36831f576a2ad12b`;
  canonical `CURRENT_STATE.md`, `CONTINUATION_INSTRUCTIONS.md`,
  `AUTO_CONTINUE.md`, current runtime and Gate13–17 roadmap checked.
- Reattempted basic `container.exec` and `python.exec`: both still
  returned `ClientError`. No new private original executable bytes
  or original-disc verification happened.
- PR #21 merged as `6e2e67564486d9578f109106f28bb22f05a7049c`:
  adds a bounded source-grounded 32-bit MSVC class RTTI→COL→CHD→
  vftable candidate locator for the previously established original
  `Button@ease_2001` class. Its unconfirmed code pointer slots
  can augment existing optional near-direct-edge searches, but
  NOTHING equates these leads to original virtual draw/update
  methods or native state-to-frame mapping. Hosted focused CI
  `36745808069` and asset-policy `36745808627` both passed.
- PR #22 merged as `9931c289cce45e957a5b1dd178f06acae01576b7`:
  grounds this new parser against an independently known original
  TeamSelect decorated TypeDescriptor `0x81EC10` and class
  vftable `0x7C7650`. Its private opt-in test requires the
  exact known-positive source reference to be recovered before
  accepting any extrapolation to the unknown Button class table;
  hosted synthetic tests verify positive and tamper/wrong-address
  rejection. Focused `36746061863` passed 191 tests with
  source-gated tests skipped as expected; asset policy
  `36746061738` passed.
- Actual canonical-original RTTI calibration and source-byte scan
  remain UNEXECUTED due to tool infrastructure. Do not infer that
  passing hosted synthetic CI establishes any native Button
  frame-index or Zurich text-placement fact.
- Full mission remains Gate13→Gate17, with a genuinely tested
  clean Windows11 install required for completion.

 
## Source-evidence-limited secondary test contracts and newly passing full suite — 1 October 2026 KST

- After Gate13's original-byte shell remained unavailable, examined
  legacy full reconstruction CI run `36699473326`: exactly two
  longstanding secondary-schedule assertions failed across 899 tests.
  `research/EXECUTABLE_ANALYSIS.md` independently supports reverse
  qsorted country-root traversal and World Cup 174 before Euro 171,
  but explicitly warns not to assume exact relative order of
  equal-key Other-country roots.
- A separate pre-existing firsthand Gate11 checkpoint in
  `research/PROGRESS.md` establishes **262** mode-1 schedule
  nodes, **45** nonempty buckets, **217** raw
  `0x615BE0/0x615AE0` shuffle draws after
  `0xCAB0B953`, finishing at **`0x61D6DFA2`**.
  The old handwritten test vector purported to contain those
  counts but in fact summed to **280**, and had never been
  independently verified per-bucket against original bytes.
- PR #23 squash `3ed8661faee4a73496ffb3674a7f97d0ddb24fa6`
  corrects both TEST EVIDENCE BOUNDARIES, not original simulation
  behavior: root traversal test checks reverse sorted array
  and proven World Cup before Euro; RNG test explicitly uses
  a SYNTHETIC 262/45 aggregate partition with mathematically
  known 217 raw draws. It records the unproven exact tie
  permutation and actual per-date secondary bucket vector
  in `research/FIDELITY_GAPS.md`, documented with precise
  provenance in `research/SECONDARY_SCHEDULE_TEST_CONTRACT_AUDIT.md`.
- Narrow PR-only full reconstruction CI was enabled for changes
  to these two vulnerable test modules; ordinary main commits
  still do not dispatch the full suite. This PR passed the
  **FULL** reconstruction run `36747022836`: **1,019 tests,
  21 expected source-gated skips, no failures**.
  Repository asset-policy run `36747022951` passed.
  Passing synthetic tests do NOT validate original per-bucket
  fidelity, original gated visual-source checks, native Button
  transitions or clean Windows 11 release behavior.


## Recovery 98 Gate13 source-verification safety and original League comparison integration (1 October 2026 KST)

- Initial verified main HEAD `76b083ac19d0e37d1175b64989f27016b129ba3e`,
  Gate13 active; read canonical `CURRENT_STATE.md` and
  `project_status.json` before changing code.
- Direct shell and both private/visible Python execution probes failed
  `ClientError` even for trivial output; a fresh direct root-workdir
  shell attempt also failed. The exact canonical source ZIP
  (511,121,336 bytes) was re-listed in the private Library,
  without re-upload or counterfeit source substitution.
- PR #24 `5b1bd361a922f1696e6c0fba963e9082a2e8fe55`
  closes the proven RTTI CLI fail-open gap, requiring
  prior known-positive original TeamSelect reference before
  publishing Button vftable candidates. Focused Gate13 CI
  `36750381283` and asset policy `36750381374` passed.
  No real-original opt-in analysis was executed due to infra failure.
- PR #25 `b7d30e557f5411aad4bd62431998d5ffd390faf7`
  connects the previously verified native League 0x4F45E0
  comparator and source CP1252 club short-name ordering to
  PL table display and management rank-sensitive consumers.
  Hosted first full run `36750875054` caught four legacy
  minimal finance `.table()` stub compatibility errors;
  all were fixed with new regression coverage. Final full
  `36751032575` passed 1027 tests, 21 expected source
  skips; asset `36751032716` passed.
- PR #26 `71d235e9c4478ad08c04127d949351339a013a87`
  uses the same actual source-name resolver for complete
  Premier League ranking publication after last match,
  rather than withholding provable ties because only
  display code knew original CP1252 names. Incomplete,
  non-CP1252 or exactly indistinguishable native keys
  still refuse a fabricated ranking. Full reconstruction
  `36751321715` **1029 passed (21 expected skips)**;
  asset `36751321748` passed.
- Exact native control and original visual resource
  validation remain dependent on working byte-execution
  infrastructure. Gate13 full original management
  presentation and audit are NOT complete. Do not
  infer native 23-frame Button atlas state, Zurich baseline
  or Windows11 release from green hosted synthetic tests.


## Recovery 99 management source-data presentation seam — 1 October 2026 KST

Native byte execution remained unavailable (`container.exec ClientError`) at
the verified `c4a8603992935ee800fd06ddadd4c2f6de899593` resume point. The
worker therefore continued only source-backed presentation/runtime separation,
without inventing proprietary visual behavior.

- PR #27 / `0ecf3258c21f66806741807d2056008b7743c190`: immutable
  controlled-club/squad/fixture/table view data, preserving live roster source
  order, fixture source insertion order and the already recovered native League
  comparator output. Gate13 focused CI `36754613939`: 199 passed. Asset
  policy `36754613931`: passed.
- PR #28 / `278916e4479fc5ec53d12126d31a4b1894c20b4f`: human formation,
  XI/bench IDs, exact four tactical runtime values and Captain/Penalty/Corner/
  Free-Kick priority lists. Gate13 `36754954095`: 201 passed. Asset
  `36754954127`: passed.
- PR #29 / `1d2bce7a1b22c9112b3a19b2e4e454c771557992`: player-profile
  source/runtime projection of CURRENT state only; hidden development target
  bytes intentionally excluded. Gate13 `36755334639`: 203 passed. Asset
  `36755334392`: passed.
- PR #30 / `6c0abb541bc7b8badec9793a10c687f710897e50`: neutral Balance
  ledger/objective and active transfer Proposal/Deal/Contract/Schedule data.
  Unresolved account/negotiation labels stay numeric/neutral. Gate13
  `36755982345`: 206 passed. Asset `36755982172`: passed.

The full hosted reconstruction baseline remains `36751321715`: 1029 tests,
21 expected source-gated skips, no failures. Recovery99 did not rerun the full
suite because these changes are isolated read-only Gate13 presentation seams
with dedicated focused CI; a later gate/release audit must run the full suite
again.

Exact critical next action remains actual canonical-source analysis when byte
execution returns: hash-gated original PE32 RTTI canary -> Button draw/update
state-to-23-atlas rows -> Zurich placement/color -> strict ten-source
ZIP/executable/pixel audit -> provenance import -> authentic management
presentation. If byte execution is still unavailable, continue only additional
already-recovered management data seams (messages/training/scouting), never
invent original visual or control semantics.

## Recovery 101 Gate13 resource coverage audit - 1 October 2026 KST

- Verified canonical main `9bb117f9403821982c112d649305cb0121cd1c4d`; did not
  repeat the already merged PR #33 full-suite integration or presentation /
  simulation separation audit.
- Re-resolved the durable Library source ZIP and materialized the expected
  511,121,336-byte file successfully. Trivial `container.exec` and trivial
  Python execution immediately returned `ClientError`, so no source-byte
  trace, import or native graphical claim was made.
- Audited Gate 13's original-resource criterion against
  `GATE13_REAL_DISC_INVENTORY.md`,
  `GATE13_FIRST_SCREEN_EXACT_PATHS.txt`,
  `GATE13_MANAGEMENT_SOURCE_DATA_BRIDGE.md`,
  `GATE13_PSTARTMENU_LAYOUT.md` and `original_assets/MANIFEST.md`.
  The authorized disc contains broad original presentation material, and
  backend presentation data exists for most roadmap screens, but only the
  PStartMenu/TeamSelect family has a pinned exact resource slice. Normal-play
  management screen resource/layout/navigation correlation is still open.
- Added `research/GATE13_RESOURCE_COVERAGE_AUDIT.md` with a per-screen coverage
  matrix and explicit non-closure boundary. The Gate 13 resource criterion
  remains unchecked; this prevents data-seam progress from being mistaken for
  original UI completion.
- Latest full hosted integration evidence remains run `36760160986`: 1,050
  tests, 21 expected original-source-gated skips, zero failures. Gate 13 remains
  ACTIVE and the Gates 13-17 mission is not complete.

## Gate 13 PScouting2K presentation contract verified - 1 October 2026 KST

- Merged PR #35 as `5a4224e651b4b4a7051eb3afe1e5f4b8d8aff44e`.
- Added immutable source-backed `PScouting2K` presentation metadata for the
  already-proven RTTI/vtable identity, event-31 search chain, deterministic
  reseed anchor and six native result-sort modes/directions.
- Explicitly kept original captions, screen/control IDs, geometry, artwork,
  font placement and navigation absent rather than guessing them.
- Focused Gate-13 run `36767384902` passed **219 tests with 19 expected
  source-gated skips**.
- Full reconstruction run `36767384882` passed **1,055 tests with 21 expected
  source-gated skips** and zero failures.
- Asset-policy run `36767384938` passed.
- Retried trivial container execution after CI; it still returned
  `ClientError`. The private original source is materialized but direct byte
  execution remains blocked, so no new Button/Zurich/physical-source claim is
  made.
- Gate 13 remains ACTIVE; Gates 14-17 and the Windows 11 release audit remain
  mandatory.

## Gate 13 first-screen manifest readiness guard verified - 1 October 2026 KST

- Merged PR #36 as `947fc7d26e6383a7da15113994baf858a44dd609`.
- Added `gate13_first_screen_manifest_readiness.py`, a fail-closed post-import
  audit for all ten pinned PStartMenu/TeamSelect source originals.
- The guard validates exact manifest source paths, canonical repository
  destinations, `original` form, pinned source SHA-256 values and current
  tracked-file hashes. Partial provenance cannot pass.
- Focused Gate-13 run `36768095800` passed **226 tests with 19 expected
  source-gated skips** and zero failures.
- Repository asset-policy run `36768095889` passed.
- Prior full reconstruction baseline remains `36767384882`: **1,055 tests,
  21 expected source-gated skips, zero failures**.
- The real manifest remains incomplete for the ten-file slice because direct
  private byte execution is still blocked; no import completion is claimed.

## Gate 13 tactics / Team Orders presentation contract verified - 1 October 2026 KST

- Merged PR #37 as `c43ce7d308c187ea9ee82698abba1c82e7af5896`.
- Promoted prior-firsthand `PFormation2k` and `PTeamOrders2K` evidence into
  immutable presentation metadata without adding guessed screen controls or
  layout.
- Formation contract preserves vtable `0x7C1AB4`, DBRUser region
  `+0x70C`, magic `0x074A3216`, five records at `+0x714`, and
  `0x1F4` record size.
- Team Orders contract preserves categories 0..3 as captaincy, penalties,
  corners and free kicks, with original English resource strings used only as
  corroboration rather than guessed control bindings.
- Focused Gate-13 run `36768744626`: **227 tests, 19 expected source-gated
  skips, zero failures**.
- Full reconstruction run `36768744640`: **1,063 tests, 21 expected
  source-gated skips, zero failures**.
- Asset-policy run `36768744578` passed.
- Gate 13 remains ACTIVE; original tactics art/layout/interaction/navigation and
  the source-critical Button/Zurich/import path are still open.

## Gate 13 PTickets presentation contract verified - 1 October 2026 KST

- Merged PR #38 as `cca08a22f33aebfab230afd6ced70e28bf552c10`.
- Promoted already instruction-locked `PTickets` evidence into immutable
  presentation metadata: DBRUser ticket object `+0x694`, size `0x7C`,
  season-ticket fields, terrace/seating prices, 26 section states and exact
  terrace/seating recommendation/helper attribution.
- Added a fail-closed controlled-club ticket-state presentation view over the
  existing runtime without introducing simulation or finance mutation.
- Focused Gate-13 run `36769405085`: **230 tests, 19 expected source-gated
  skips, zero failures**.
- Full reconstruction run `36769405053`: **1,066 tests, 21 expected
  source-gated skips, zero failures**.
- Asset-policy run `36769404960` passed.
- Original PTickets visual resources, widget bindings, layout and navigation
  remain unresolved, so Gate 13 remains ACTIVE.

## Gate 13 Messages / News presentation contract verified - 1 October 2026 KST

- Merged PR #40 as `ab51a607f9576f68179ea7c0c531d594c6b411ee`.
- Added immutable manager-mail presentation metadata for the already-proven
  `MPMEAMail` family, ordinary/Bosman renewal suggestions and
  `PlayerAskTransferList` request actions.
- Preserved the important negative boundary that cross-family inbox interleave
  and sorting are not yet proven.
- Focused Gate-13 run `36772292710`: **233 tests, 19 expected source-gated
  skips, zero failures**.
- Full reconstruction run `36772292682`: **1,069 tests, 21 expected
  source-gated skips, zero failures**.
- Asset-policy run `36772292765` passed.
- Gate 13 remains ACTIVE; original Messages/News visual resources, layout,
  controls and navigation are still open.

## Gate 13 Training presentation contract verified - 1 October 2026 KST

- Merged PR #41 as `22254782bf396f192c9db38b1b518628177ece65`.
- Added immutable Training.cpp presentation metadata for the 40 × 0xC8 record
  family, embedded training offsets, fresh defaults, seven method/profile
  mappings and source daily/weekly update chain.
- Deliberately kept the original Training screen class unknown because persisted
  primary evidence does not pin one.
- Focused Gate-13 run `36772718356`: **234 tests, 19 expected source-gated
  skips, zero failures**.
- Full reconstruction run `36772718243`: **1,070 tests, 21 expected
  source-gated skips, zero failures**.
- Asset-policy run `36772718259` passed.
- Gate 13 remains ACTIVE; original Training visual resources/layout/navigation
  and the private Button/Zurich/source-import critical path remain open.

## Gate 13 League-table presentation contract verified - 1 October 2026 KST

- Merged PR #42 as `bffa017331788958344b598ea44f3f6b5e002477`.
- Promoted native League comparator `0x4F45E0` into immutable presentation
  metadata: points DESC, played ASC, goal difference DESC, goals for DESC,
  goals against ASC, source short-name CP1252 bytes ASC.
- Preserved the fail-closed boundary for identical full original keys instead
  of inventing a stable qsort tie order.
- Focused Gate-13 run `36773050542`: **235 tests, 19 expected skips, zero
  failures**.
- Full reconstruction run `36773050532`: **1,071 tests, 21 expected skips,
  zero failures**.
- Asset-policy run `36773050761` passed.
- Original League-table art/layout/controls/navigation remain open.

## Gate 13 Fixtures / Results presentation contract verified - 1 October 2026 KST

- Merged PR #43 as `a346762f0fcfc54cdb17fbd0d1787a539dfa8fd7`.
- Promoted DBTRealFixtures/DBRRealFixture/DBTRounds identities and fixed League
  source-order construction into immutable presentation metadata.
- Preserved the key non-claim that backend source order is not the recovered
  original Fixtures/Results screen sort.
- Focused Gate-13 run `36773557317`: **236 tests, 19 expected skips, zero
  failures**.
- Full reconstruction run `36773557140`: **1,072 tests, 21 expected skips,
  zero failures**.
- Asset-policy run `36773557226` passed.

## Gate 13 Player Profile presentation contract verified - 1 October 2026 KST

- Merged PR #44 as `0e2d9e03b61f691be5f63ebbb7b57018cbfdbf45`.
- Added DBTPlayers/DBRPlayer backend identity metadata, retaining approximate
  RTTI/accessor addresses as anchors rather than exact canaries.
- Locked current skills at +0x1E..+0x2E versus development targets at
  +0x2F..+0x3F, with development targets deliberately not exposed as proven
  original profile UI.
- Focused run `36773922844`: **237 tests / 19 expected skips / 0 failures**.
- Full run `36773922864`: **1,073 tests / 21 expected skips / 0 failures**.
- Asset policy `36773922713` passed.
- Direct shell retry still failed immediately with `ClientError`.


## Gate 13 Squad presentation contract verified - 1 October 2026 KST

- Recovery 104 re-listed the canonical private 511,121,336-byte authorized
  source ZIP from `/FM2001/Original Source/` and successfully materialized it
  into the current workspace. The source is present.
- Private byte execution remains an infrastructure blocker: after one trivial
  shell probe succeeded, repository/file access, subsequent shell probes and
  private Python all returned `ClientError`. No new native Button/Zurich,
  pixel, ten-resource or executable claim was made.
- Merged PR #45 as
  `de3091f7102d178aafb5604b3eeca2561bf04a97`.
- Added the immutable Squad backend presentation contract for team roster
  `+0x244` / count `+0x294`, participant collector `0x510CD0`,
  active/substitute predicates and setters, DBRPlayer `+0x14` selection
  masks, removal helper and preserved roster iteration order.
- Kept the original Squad screen class, row sort, columns, graphics, geometry,
  controls and navigation explicitly unresolved.
- Focused Gate-13 run `36780212525`: **238 tests / 19 expected skips /
  0 failures**.
- Full reconstruction run `36780212535`: **1,074 tests / 21 expected skips /
  0 failures**.
- Asset-policy run `36780212608` passed.
- Next source-backed fallback task is the manager-home / remaining-screen
  evidence-and-blocker inventory. The native Button/Zurich/ten-resource path
  regains priority immediately if private execution recovers.


## Gate 13 management-screen evidence ledger and catalog audit verified - 1 October 2026 KST

- Added `research/GATE13_MANAGEMENT_SCREEN_EVIDENCE_LEDGER.md`, replacing
  the vague manager-home/remaining-screen blocker with a per-surface evidence
  matrix.
- The ledger distinguishes proven presentation classes from backend/event-only
  identities and feature-family leads. In particular, no persisted original
  Manager Home panel identity is currently proven.
- Added a reproducible whole-disc query plan for every named Gate-13 management
  surface and a strict correlation-before-import rule.
- Merged PR #46 as
  `ca7f6cfd9c5fae01ac9c454ad14603076979262b`.
- Added `gate13_management_catalog_audit.py`, which groups saved catalog
  path candidates by screen family while explicitly keeping
  `binding_proven = false`; the default nested-disc layer avoids the outer
  ZIP wrapper's Football Manager name creating false manager-home hits.
- Focused Gate-13 run `36781127596`: **243 tests / 19 expected skips /
  0 failures**.
- Asset-policy run `36781127819` passed.
- No full reconstruction run was launched for this isolated catalog/reporting
  tool because the workflow intentionally excludes it; PR #45 remains the
  latest full integration baseline at **1,074 tests / 21 expected skips /
  0 failures**.
- Post-merge private shell execution still returns `ClientError` even for a
  trivial stat of the already materialized canonical ZIP. Source availability
  is confirmed; execution is the blocker.
- No further screen semantics will be invented. The exact next action remains
  TeamSelect RTTI canary -> Button 23-frame state mapping -> Zurich text trace
  -> strict ten-resource audit/import as soon as private execution works.

## 1 October 2026 KST - Recovery 120 source recovery succeeded, execution failed before byte audit

- Resumed canonical main `c36b7047dbcfc1f99a916a9997debb706ec08eb0`.
- Trivial shell execution initially worked; direct GitHub cloning failed only
  because the isolated container had no DNS route to `github.com`.
- Re-resolved and materialized the exact 511,121,336-byte authorized private
  source ZIP from the durable Library locator.
- After materialization, both a trivial shell file probe and a separate private
  Python process failed with `ClientError` before execution, so no new
  original-byte fidelity claim is made.
- Runtime remains continuous/working. Exact next action is the persisted
  TeamSelect RTTI -> Button -> Zurich -> ten-resource path as soon as stable
  process execution returns.
## Gate 13 canonical Button/Zurich trace and ten-resource import - 1 October 2026 KST

- Fetched canonical GitHub state, verified the local clone was clean and
  fast-forwarded local main to `c36b7047dbcfc1f99a916a9997debb706ec08eb0`.
- Located the authorized original ZIP locally. Its 511,121,336 bytes matched
  SHA-256 `677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`.
  The repository inventory tool privately extracted `footballmanager.exe`,
  which matched `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
- Installed Capstone 5.0.9 to private task storage outside Git. The expanded
  trace passed the fail-closed TeamSelect TypeDescriptor `0x81EC10` / vftable
  `0x7C7650` canary and yielded one Button RTTI candidate. Constructor writes
  corroborated TypeDescriptor `0x81AD90`, COL `0x7E0B90`, CHD `0x7E0B80` and
  vftable `0x7BF4CC`.
- Recovered the native 23-frame model: group lengths `(11,11,1)`, frames
  `0..10` for enabled/mask-4-clear, `11..21` for enabled/mask-4-set and `22`
  for disabled. Pointer-inside mask `0x8` advances subframes and pointer-out
  retreats. Mask-4's user-facing name remains deliberately unclaimed.
- Recovered shared Zurich Button caption setup: style `0x2000`, centered
  21-pixel native line, 0/0 offsets, 16-bit values `0xFFFF` normally and
  `0x0000` for group 1. Implemented exact PStartMenu line origins and retained
  native values without an unsupported RGB reinterpretation.
- Ran the strict ten-path selection and firsthand source audit successfully,
  then imported all ten exact originals one at a time with provenance. The
  first-screen readiness guard and repository asset-policy guard pass.
- Preserved raw executable/disassembly/pixel reports outside Git. No ZIP,
  executable, disc image or uncontrolled dump was added.
- Added `research/GATE13_BUTTON_NATIVE_TRACE.md`, native state/caption code and
  focused synthetic plus opt-in exact-source regressions.
- Gate 13 remains active. Next is whole-disc management catalog correlation,
  TeamSelect hierarchy/wider management presentation only where source-bound,
  and the real Windows graphical/normal-play audit before Gate 14.

## Gate 13 native captions and Scouting composition - 1 October 2026 KST

- Opened PR #47 from canonical main `af2b3ec1c3d498e8774156d599faceb69e6de8b7`.
- Integrated source-backed PStartMenu Zurich caption overlays into the private
  800x600 developer view. Caption origin comes from the recovered native
  geometry; color conversion is limited to the invariant all-bits-off/on
  endpoints `0x0000` / `0xFFFF`.
- Added exact source-frame -> native Button group/subframe inversion and
  regression coverage.
- Added `original_scouting_resources.py` for the proven
  `PScouting2K::0x4AB150` composition only:
  `background_alpha_1.444` = 571x16 repeated 20 times at
  (207, 192+17*n), and `background_2.444` = 295x45 at (206,543).
- Hosted tests directly verify the committed Scouting source bytes still match
  their pinned SHA-256 values and original EA444 header geometry.
- Initial Gate-13 run `36813979522` exposed one stale GUI test expectation
  (5 canvas images vs 9 after four captions); the Scouting tests themselves
  passed. The expectation was corrected without changing runtime behavior.
- Final focused Gate-13 run `36814179046`: **249 tests / 20 expected skips /
  0 failures**. Asset-policy run `36814179303` passed.
- PR #47 squash-merged to main as
  `757e8fec77f688bab893e155fee0bb82eaa97b6f`.
- Cloud process execution remains unavailable (`ClientError` before process
  start), preventing a new private Squad resource/executable correlation and
  the Windows graphical smoke test in this worker. Exact next source task is
  one Squad resource -> true panel-owner binding, followed by the real Windows
  first-screen/normal-play audit.

## 1 October 2026 KST - Gate 13 Squad resource ownership recovered

- Re-synchronized clean local main at
  `cad50f8d9fa45f57608971db3eff5f2bbc817d47` and read recovery generation 124.
- Re-verified the authorized ZIP and canonical executable hashes, then reused
  the private whole-disc catalog and Capstone environment.
- Enumerated and extracted the four exact Squad catalog candidates. Exact
  literal/loader/wrapper tracing and RTTI recovered `PSquadScreen`,
  `FormationText`/`PSquadPitch`, and the four actual shared `blue_toggle`
  consumers.
- Provenance-imported all four resources and added fail-closed hash, native
  geometry, owner-boundary and `PSquadScreen` origin tests.
- Preserved exhaustive binary reports outside Git. No archive, executable,
  disc image or uncontrolled dump was added.

## 1 October 2026 KST - Gate 13 Squad controls and captions source-bound

- Continued from clean canonical checkpoint `bc25db9c4d98d1e6038d485822e6a74fdc95af1c`.
- Traced the three `PSquadScreen` top controls through their embedded object
  offsets, generic registration method and numeric IDs: 3/4/5 at
  `+0x37A4/+0x37F8/+0x384C`.
- Counted the canonical language loader's sequential 16-bit reads from its
  first `English.idx` entry and proved globals `0x982110/0x98210C/0x982108`
  are entries 2490/2491/2492.
- The committed original English language pair resolves them exactly to
  `1ST & RES`, `1ST FORM`, and `RES. FORM`.
- Added a fail-closed language-binding contract and regressions. The first
  control's distinct setup flag and all atlas-frame state names remain
  deliberately unresolved pending a separate transition trace.

## 1 October 2026 KST - Squad view transitions and FormationText geometry

- Proved the two embedded roster panels are `CBasePlayerList` instances and
  recovered their 228x520 rectangles plus the embedded 412x432
  `PSquadPitch` rectangle.
- Traced `PSquadScreen::0x4B8E70`: controls 3/4/5 select first+reserve,
  first+formation and reserve+formation by rebinding the left player list,
  toggling native mask 1 on the second-list/pitch containers, and storing
  pitch team index 0 or 1.
- Proved `PSquadPitch::0x4B3C80` constructs 22 paired `FormationText` rows at
  y=25..382 in 17-pixel steps, with IDs 12..55. The form cell is 23x16 at
  x=279 and the bar is 81x16 at x=303.
- Confirmed both frame sizes directly from native wrapper initializers rather
  than dividing atlas height. Raw disassembly remains private outside Git.

# 2026-10-01: concrete Squad rows and FormationText mapping recovered

- Reverified the canonical executable SHA-256 and regenerated the expanded
  private Squad trace outside Git.
- Recovered the concrete list/row RTTI hierarchy, 20-row layout, source-bound
  player/role/name/Condition/form/rating columns, neutral filter-code mapping,
  status-icon binding, and empty-row branches.
- Recovered exact `FormationText` groups `(2,1,1)`, ordinary hover rows 0/1,
  complete-formation row 2, and the fail-closed generic row-4 boundary.
- Added durable constants and focused tests; no proprietary/raw source entered
  Git. Next: real Windows PStartMenu/TeamSelect graphical audit.
- Focused affected tests: 14 passed with one expected source-gated skip. The
  263-test Gate-13 list had no Squad failure; its sole failure is the existing
  case-only duplicate-path assertion under Windows filesystem semantics.



## 1 October 2026 KST - Gate 16 multi-season save/reload continuation verified

- Recovery 129 resumed canonical main, preserved Gate 13 as the earliest
  incomplete validation gate, and continued independent Gate 16 work-ahead.
- Extended the existing three-season synthetic live-world stress with five
  internal controller save/reload round-trips: mid-season in each of the three
  seasons and immediately after both annual primary regenerations.
- The stress compares complete controller snapshots before and after every
  reload, then continues the same live world through 380 fixtures per season
  while rechecking table, roster, Condition, Form, suspension and monthly
  development invariants.
- Identified and fixed a concrete post-rollover save-continuity defect:
  internal source validation had rebuilt immutable source fixture identity from
  the live Premier League, but annual mode deliberately replaces that live
  league with procedural fixtures. Database-backed GameState now retains the
  original fixture identity, and restore reconstructs it from the already
  validated source database. Wrong-database rejection remains strict.
- Initial full run `36835600174` reached and successfully reloaded the first
  post-regeneration state, then failed only because the test incorrectly
  required year two to reach 160 results within 180 calendar days. That bound
  omitted the legitimate summer off-season, so the harness was corrected to a
  one-year 370-day bound without weakening any game-state invariant.
- Final reconstruction run `36836256569` passed **1,125 tests with 22
  expected original-source-gated skips and zero failures** on PR head
  `dcf739a6f747fc024e4fbd1038a68a05661e08f4`.
- Repository asset-policy run `36836256308` passed.
- PR #55 squash-merged as
  `73ca421609cc6e929156c72f5b021b02a6efca3b`.
- Gate 16 remains work-ahead only. Canonical real-data multi-season evidence,
  broader competitions, sustained autonomous transfer churn, wider seed
  coverage and remaining long-duration state-growth risks are still open.


## 1 October 2026 KST - Gate 16 autonomous transfer churn verified

- Recovery 130 resumed canonical main at
  `2002304642f9fcbdcc336ce3e4cd358c64d85de7` with Gate 13 still the earliest
  incomplete validation gate and PR #57 as the exact independent cloud-safe
  task.
- The first full-suite attempt, run `36837615509`, executed 1,129 tests with
  22 expected source-gated skips and found three errors in the new five-year
  transfer-churn stress. All three exposed the same pre-existing production
  defect: contract month arithmetic could construct an impossible Python date
  when day 29/30/31 targeted a shorter month.
- The source-backed month count remains unchanged. Because the exact original
  end-of-month normalization could not be re-disassembled in the current
  execution allocation, the runtime now uses a bounded compatibility rule:
  preserve the source day when valid, otherwise clamp to the target month's
  final valid day. The unresolved original behavior is explicitly recorded in
  `research/FIDELITY_GAPS.md`; no source-fidelity claim was invented.
- Added ordinary, leap-February and multi-month month-end regressions while
  retaining the five-year/260-week transfer-churn invariants: exact roster
  ownership, seller floor, bounded roster size, one movement per successful
  acquisition, no transient transfer-container leakage, residency cooldown and
  deterministic seed signatures.
- Final reconstruction run `36840977540` passed **1,130 tests with 22
  expected source-gated skips and zero failures** in 278.116 seconds.
  Repository asset-policy run `36840977536` passed.
- PR #57 merged to main as
  `71676cb9a5b5b89b60b037c8f4426dc72a58e682`.
- Gate 16 remains work-ahead only. The next independent cloud-safe risk is one
  long shared-primary scheduler stress spanning Premier League, domestic Cup,
  European Cup, qualification-Cup and procedural-League owners. Dynamic FA Cup
  replay insertion remains fail-closed and must not be guessed.


## 1 October 2026 - Gate 16 mixed shared-primary scheduler stress verified

Independent Gate-16 work-ahead now includes one long synthetic calendar that
executes five live primary owner types through the retained Gate-12 global
order: Premier League, English domestic Cup, European Cup, annual-qualification
Cup and procedural League.

PR #58's first full run (`36842205701`) produced exactly two new errors. Both
came from the stress fixture shrinking the Premier League to two clubs while
the source-backed League strategy requires the canonical competition cut-line
structure. Production logic was not weakened. The fixture was repaired to keep
a valid 20-club Premier League table while exposing only one bounded PL entry
through the mixed primary order.

The repaired stress now requires the complete dated execution signature to
equal the retained primary order exactly, completes eight events for each
non-PL owner, checks event-proportional Cup/procedural state, preserves roster
ownership and valid player condition/form/injury/discipline state, and
replays identically from the same CRT seed. Daily post-fixture maintenance is
live; transfer/payroll maintenance remains covered by the separate five-year
transfer-churn soak. Decisive synthetic Cup nodes deliberately leave the
unresolved fail-closed dynamic FA Cup replay insertion boundary unchanged.

Verification on final PR head
`8bc252fdc5f0c960cd4cb8845a6fe1711b6a211d`:
- reconstruction run `36846018068`: **1,132 tests**, **22 expected
  source-gated skips**, zero failures;
- asset-policy run `36846018016`: passed.

PR #58 squash-merged as
`24447d846b96fe68d2eba7c17d0053de638e43ef`.

Next cloud-safe Gate-16 target: combine repeated annual regeneration with
internal save/reload and measure serialized/state growth so replaced
season-owned structures cannot accumulate silently. Canonical real-data
multi-season evidence remains separately required, and Gate 13 remains the
earliest incomplete validation gate.


## 1 October 2026 - Gate 16 annual regeneration/save-growth soak verified

- PR #59 extended the existing destructive annual-regeneration soak with **12
  consecutive annual replacements and 12 exact schema-34 internal save/reload
  round-trips** in the existing 20-club synthetic annual world.
- Before each rollover the outgoing season is deliberately dirtied with one
  Premier League result and one prepared-match environment. The new season must
  replace those structures, restore an exact 380-fixture scheduler, and retain
  one stable structural shape across Premier League fixtures/results, scheduler
  state, primary shadow/order, Cup owners and procedural-League owners.
- Every cycle compares the complete human-gameplay snapshot before and after
  reload and requires byte-identical compact JSON after reserialization.
- Compact save length may vary with dates/RNG integers, so the test uses a
  deliberately generous **4 KiB max-minus-min payload spread** only as a
  corruption detector. It is not an original FM2001 save-size claim.
- Final reconstruction run `36847418060` passed **1,133 tests** in 159.081
  seconds with **22 expected source-gated skips and zero failures**.
  Repository asset-policy run `36847418038` passed.
- PR #59 squash-merged as
  `a9ec833173a92a4b8b3c2238d91943c159f7fa92`.
- Gate 16 remains work-ahead only. Next cloud-safe state-growth target is
  periodic save/reload during five-year autonomous transfer churn, with
  movement history required to remain exactly event-proportional and transient
  transfer containers required to stay empty.


## 1 October 2026 - Gate 16 transfer history save/reload continuation verified

- PR #60 added yearly schema-34 `GameState` round-trips to the existing
  five-year/260-week autonomous-transfer churn at weeks 52, 104, 156, 208 and
  260.
- The persistence fixture uses a separate immutable synthetic source database,
  so reloading cannot validate against player ownership already mutated by the
  live transfer run.
- Each checkpoint requires exact before/after state-snapshot equality,
  byte-identical compact JSON reserialization, exact movement-history count,
  empty transient proposal/deal/bid-log/scheduled-transfer containers, and
  complete roster-integrity invariants.
- The complete periodically reloaded five-year run must match a never-reloaded
  run from the same CRT seed across successful acquisition count, ordered
  movement history, per-player movement counts, final rosters, autonomous buy
  counters, final RNG state and final date.
- Final reconstruction run `36849081411` passed **1,134 tests** in 298.926
  seconds with **22 expected source-gated skips and zero failures**.
  Asset-policy run `36849081409` passed.
- PR #60 squash-merged as
  `c640e5cb7dad46926e67a35caa34b83deb99c2cf`.
- Recovery 132 also re-established private canonical source access: the exact
  511,121,336-byte Library disc archive materialized successfully; its canonical
  ZIP SHA-256 matched, and direct ISO-9660 extraction produced `Master.dat`,
  `Static.dat`, `English.str`, `Core.str` and `FOOTBAL.EXE` matching all
  pinned repository hashes. The next Gate-16 target is therefore canonical
  shipped-data multi-season execution rather than another synthetic stress.


## 1 October 2026 - Recovery 133 canonical multi-season execution allocation failed

- Resumed canonical `main` at `120400bd1ce25e449897e927e00dfa9f945076eb`
  and restored `agent-runtime` to continuous/working as recovery generation
  133 before substantive work.
- The fresh execution allocation initially launched one trivial shell process
  successfully (`Python 3.13.5`, `git 2.47.3`). A direct repository clone then
  failed because the shell could not resolve `github.com`; connector-backed
  GitHub reads remained healthy.
- The canonical 511,121,336-byte disc archive at Library path
  `/FM2001/Original Source/The-F-A-Premier-League-Football-Manager-2001_Win_EN_Disc-Image.zip`
  was materialized successfully into the workspace. An older portable FM2001
  bundle was also located only as a potential transport/bootstrap source, with
  the explicit requirement that every runtime module used be reconciled to
  current `main` before execution.
- Before hashes or canonical runtime execution could be re-run, every later
  shell process and the independent Python process path failed before start
  with `caas.internal.errors.ClientError`. Therefore this recovery does not
  claim a canonical multi-season pass, a new source hash receipt, or any new
  gameplay fidelity result.
- The next executable task remains the canonical shipped-data multi-season
  Gate-16 audit on one continuous runtime through repeated annual
  qualification/regeneration. The runtime stays `working` so automatic
  recovery can move this task to a healthy execution allocation.


## 1 October 2026 - Recovery 134 canonical multi-season runner and runtime bootstrap

- Resumed canonical main `1282b5477d4cfed173cc19111a5480876178aa8b` and
  advanced `agent-runtime` to recovery generation 134. The fresh allocation's
  first shell launch failed before process start with
  `caas.internal.errors.ClientError`, so no canonical private execution or new
  source-hash receipt is claimed from this allocation.
- Rather than repeat the dead process path, PR #63 added the dedicated
  fail-closed `reconstruction/canonical_multiseason_audit.py` runner plus four
  repository-side control-flow tests and
  `research/GATE16_CANONICAL_MULTISEASON_AUDIT.md`.
- The runner waits for the same live annual qualification boundary used by the
  proven Gate-12 canonical audit and never synthesizes standings, Cup results,
  qualification, membership swaps, or RNG state. Each cycle requires a
  complete 380-fixture/20-club Premier League, coherent roster/membership
  references, atomic RNG and membership transition, exact regenerated
  scheduler coverage, retained played qualification-League owners, and a
  stable fresh season-owned structural shape.
- Final PR head `d7d230af935accb0e24f81a46f34a346c9c768fc` passed full
  reconstruction run `36857099351`: **1,138 tests in 295.693 seconds, 22
  expected source-gated skips, zero failures**. Asset-policy run
  `36857099441` passed. PR #63 squash-merged as
  `c12df0dde85bb477392c25b97f8b9ca3254b2837`.
- Recovery 132's successful reconstruction-runtime Actions artifact
  (`recovery132-reconstruction-runtime`, artifact `11155211053`, digest
  `sha256:9167302c608882161954109d617824422671d2999d69006bff5d662adeb2c4d6`)
  was downloaded through the GitHub connector and persisted in the Library at
  `/FM2001/Working Runtime/FM2001-reconstruction-runtime-120400bd.zip`
  (688,773 bytes). Its reconstruction code is rooted at
  `120400bd1ce25e449897e927e00dfa9f945076eb`; main changes through Recovery
  133 touched only research/status files, so it is a valid engine bootstrap.
  It predates the new runner file itself.
- Exact next task remains the real canonical shipped-data multi-season run.
  Future recovery should materialize the canonical disc archive and runtime ZIP
  through Files before starting a shell, eliminating dependence on in-sandbox
  GitHub DNS/network access, then execute the merged runner and persist its JSON
  evidence.


## 1 October 2026 - Recovery 134 all process execution paths confirmed blocked

- After merging/checkpointing the canonical multi-season runner, Files
  successfully materialized the canonical 511,121,336-byte source archive and
  the persistent 688,773-byte reconstruction runtime ZIP into the execution
  workspace without requiring a shell.
- The independent user-visible Python environment was then invoked solely to
  verify/access those files and also failed before process start with
  `caas.internal.errors.ClientError`.
- This confirms the remaining blocker in Recovery 134 is the execution
  allocation itself. Repository access, canonical source availability, runtime
  transport, CI, and the audit runner are all available. No canonical season
  was executed and no source hash was re-verified in this failed allocation.
- Exact next action: in the next healthy allocation, materialize the same two
  Library ZIPs before launching a process, extract them outside Git, re-verify
  the pinned canonical files, place/invoke the merged multi-season runner, and
  execute at least three consecutive qualification/regeneration cycles.


## 1 October 2026 - Recovery 135 canonical multi-season execution

Recovery 135 restored a sustained execution allocation and moved the Gate-16
canonical multi-season task past the Recovery-134 infrastructure blocker.

The authorized source and persisted reconstruction runtime were materialized
outside Git. The complete raw MODE1/2352 image passed sector validation across
268,549 sectors. Canonical `Master.dat`, `Static.dat`, `English.str`, and
`Core.str` hashes matched, and the executed multi-season runner matched the
current GitHub blob.

The exact seed-1 three-rollover run advanced for about 22 minutes before the
runner deliberately failed its fresh-season growth guard on cycle 2:

`(380,380,5735,9344,291,371,311,13)` ->
`(380,380,5737,9346,291,373,311,13)`.

The delta is narrowly localized: +2 European Cup schedule nodes and the same +2
entries in the shared primary and shadow schedules. Premier League,
domestic-Cup, qualification-Cup and procedural-League structure remained
stable. No Gate-16 pass is claimed. Next work is to identify those exact
European competition/round nodes, determine whether annual participant-driven
underfill legitimately changes node cardinality or whether nodes accumulated
across seasons, encode the result in regression coverage, and rerun the
canonical audit.


## 1 October 2026 - Recovery 137 canonical seed-1 multi-season audit passed

- PR #65 fixed the audit-only procedural shared-primary projection boundary and
  passed asset-policy run `36867367968` plus full reconstruction run
  `36867368043`.
- PR #65 squash-merged as
  `7f3f83eb98b9f29039b691197505dbe74c8b0851`.
- The exact authorized shipped-data seed-1 audit then completed three
  consecutive annual qualification/regeneration cycles with exit code 0 in
  **1,617.49 seconds**, ending on **2003-06-02**.
- Every cycle completed all 380 Premier League fixtures, retained 30,064 live
  roster references, applied 28 annual membership changes, and passed the
  roster, membership, scheduler, atomic RNG and current-regeneration projection
  invariants.
- Fresh shape diagnostics were
  `(380,380,5735,9344,291,371,311,13)`,
  `(380,380,5735,9344,291,371,311,13)`, and
  `(380,380,5737,9346,291,373,311,13)`. The final variation is the
  already-proven qualification-dependent UEFA Cup node change, not accumulation.
- Exact hashes, CI IDs, snapshots, RNG states and structural diagnostics are
  persisted in
  `research/evidence/GATE16_CANONICAL_MULTISEASON_SEED1_RECOVERY137.json`.
- Gate 13 remains the earliest incomplete validation gate. Recovery 137 has
  launched the same canonical three-rollover audit with player seed 2 to widen
  real-data seed coverage while the Windows graphical audit remains deferred.


## 1 October 2026 - Recovery 137 canonical seed-2 pass and Gate 16 readiness audit

- The second authorized shipped-data canonical run used player seed 2 and
  completed three consecutive annual qualification/regeneration cycles with
  exit code 0 in **1,440.49 seconds**, ending on **2003-06-02**.
- Fresh shapes were
  `(380,380,5731,9340,291,367,311,13)`,
  `(380,380,5735,9344,291,371,311,13)`, and
  `(380,380,5735,9344,291,371,311,13)`. Each variation projected exactly
  from that cycle's current regeneration; no stale cross-season Cup or shared
  schedule state accumulated.
- Exact seed-2 evidence is stored in
  `research/evidence/GATE16_CANONICAL_MULTISEASON_SEED2_RECOVERY137.json`.
- `research/GATE16_READINESS_AUDIT.md` reconciles the roadmap criteria against
  the 30-rollover soak, six-seed complete-season stress, multi-season
  save/reload, five-year transfer churn, mixed-primary stress and the two
  canonical three-rollover seeds.
- All present Gate-16 criteria are prevalidated by work-ahead, but Gate 16 is
  deliberately **not** marked complete while Gates 13-15 remain incomplete.
- The next independent cloud-safe task moves back to Gate 15: recover the exact
  secondary startup equal-key permutation and per-date mode-1 bucket vector
  from the canonical executable/real input, replacing the current synthetic
  aggregate-only partition without inventing native qsort behavior.

## 1 October 2026 - Recovery 138 real Windows first-screen audit passed

- Rehashed the authorized ZIP and canonical executable, freshly extracted the
  four canonical gameplay files, and verified their pinned hashes.
- The first audit attempt correctly failed because private staging omitted
  `FOOTBAL.EXE`; the unchanged harness passed after the already-verified
  executable was added under its canonical name.
- The real Windows 11 Tk path passed live canvas/image/caption checks and the
  source-backed PStartMenu -> TeamSelect -> Back interaction sequence.
- Private receipt SHA-256:
  `b61d56dde7fc3ee7d25451cc993f545c28217cb28347a05921d379efe932e9b4`.
- Gate 13 remains open on TeamSelect hierarchy semantics and broader original
  management presentation.

## 1 October 2026 - Recovery 139 TeamSelect hierarchy owner trace

- Canonical executable RTTI/disassembly identifies the 16 native
  country/competition controls and 24 club controls, including exact setup
  coordinates, control IDs, and owner-object offsets.
- Recovered the English country order and country -> competition -> club
  population path without screenshot inference.
- Focused tests lock these durable constants. Visual frame-state, exact
  competition filtering, and club selection remain next; Gate 13 stays active.

## 2 October 2026 - Recovery 142 private execution reblocked; Gate 14 TGQ conversion contract

- Resumed from canonical main `fab51646abac21f078fdfa6fd6bed1091010ca33` and advanced the runtime lease to recovery generation 142 with `mode=continuous` / `status=working`.
- One initial trivial shell probe succeeded. The exact canonical 511,121,336-byte source archive was then resolved from Library path `/FM2001/Original Source/The-F-A-Premier-League-Football-Manager-2001_Win_EN_Disc-Image.zip` and materialized successfully.
- Immediately afterward every shell launch, the independent Python execution path, and a later trivial shell reprobe failed before process start with `caas.internal.errors.ClientError`. Therefore Recovery 142 makes no new source-hash, executable-hash, TeamSelect selection-payload, or upgraded Windows graphical claim.
- Under the deferred-blocker policy, independent Gate-14 work continued instead of repeating the dead execution path. PR #71 added a fail-closed startup-TGQ conversion contract: exact source validation must pass before deterministic non-overwriting FFmpeg plans are produced, and converted MP4/H.264/AAC output must pass exact stream-count, 320x480 geometry, 25 fps, original decoded-frame-count, `yuv420p`, and 22,050 Hz stereo FFprobe checks.
- The conversion checkpoint deliberately does not launch FFmpeg, claim playback, rename the unresolved wrapper bit as a confirmed skip semantic, or invent fade/scaling/interlace behavior.
- PR #71 head `cb9ce3836252ee3bf05a259f805f573502032b18` passed full reconstruction run `36897544475`: **1,149 tests, 22 expected source-gated skips, zero failures**. Asset-policy run `36897544592` passed. It squash-merged as `ea1e7c6bb25c35243a992c4a33d02038ddb3abc3`.
- Gate 13 remains the earliest incomplete validation gate. The exact private next action is still the bounded TeamSelect `0x4D8E90` / `0x4D9240` selection-record and Start-resolution re-trace followed by the upgraded real-Windows audit. While execution remains unavailable, the next independent cloud-safe task is a private Gate-14 conversion/probe receipt runner around the now-verified contract.



## 2 October 2026 - Recovery 143/144 TeamSelect selection-record closure

- Recovery 143 restored process execution, rematerialized the canonical 511,121,336-byte source archive outside Git, and reverified both shipped `footballmanager.exe` copies at SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
- The bounded original-byte trace closed the long-standing TeamSelect contradiction. `0x4D9240` resolves a private 0x30-byte per-row rollback record whose first dword is initialized to `-1`. `0x4D8E90` saves the clicked club's displaced manager reference/state there, then passes the clicked club itself to `0x413BB0`; user initialization `0x4258D0` binds that club at user `+0x5B4`. Deselection removes the created user and restores the saved manager state.
- TeamSelect is therefore source-proven multi-user rather than a single provisional selection-record ID. `0x4DA4D0` hard-stops at six global users and can also stop earlier when manager availability is exhausted. Start event `0x2A` enters `0x4C41C0` with the already-created user list; it does not translate the rollback record into a gameplay club ID.
- PR #74 implements the corrected boundary: ordered multi-club selection persists across country/competition navigation, clicked rows use canonical club IDs, the six-user cap is fail-closed, and the present single-manager backend refuses multi-user Start rather than silently discarding users. Detailed source evidence is in `research/GATE13_TEAMSELECT_USER_SELECTION_TRACE.md`.
- PR #74 head `5ee87bae88d5c429908f18b47aa46650bc1913a1` passed Gate-13 focused run `36905144322`: **276 tests, 21 expected source-gated skips, zero failures**. Asset-policy run `36905144376` passed.
- Recovery 144 resumed after an interrupted response and reconciled the canonical status ledgers before merge. The next validation boundary is a new real Windows 11/Tk audit of the corrected TeamSelect click/select/deselect/Start behavior; the older Recovery-138 graphical receipt predates this mapping and remains historical evidence only.


## 2 October 2026 - Recovery 144 PMenu management-shell route

- Continued immediately after PR #74 merged as `38b8daedcc85ba5f875aca075ad6c9ea852bcd7a`; Gate 13 remained active because the corrected Windows graphical audit and normal-management presentation were still open.
- The canonical executable remained locally available and hash-verified. The post-TeamSelect new-game tail calls `0x4C2FB0(1,0,0)`; that function constructs `PMenu` through ctor `0x482830`, vtable `0x7C3DE8`, RTTI `.?AVPMenu@@`.
- `PMenu::0x482960` reads neutral user route state at `+0x10E8` through `0x42C6A0`. The user constructor `0x424CA0`, reached by TeamSelect user creation `0x413BB0`, explicitly calls setter `0x42C6B0` with zero, proving fresh users start in route state 0.
- Route state 0 selects PMenu panel code `0xCE`; factory `0x47AEC0` case `0x47AF2D` allocates the panel and calls `0x4B8240`, which installs `PSquadScreen` vtable `0x7C5CA4`. Therefore fresh new-game management content begins on Squad, not on an unproven generic Manager Home panel.
- Route state 1 selects code `0x25A`; factory case `0x47C6D1` calls `0x448640`, whose panel vtable is `0x7C00C8` / `PLeagueTables`. PMenu then clears nonzero route state to zero. Other nonzero values use the Squad route and are likewise cleared.
- Added `reconstruction/original_management_shell.py` plus regressions and `research/GATE13_MANAGEMENT_SHELL_ROUTE.md`; reconciled the management-screen/resource/separation audits and corrected the roadmap suggested order. The real Windows/Tk corrected first-screen rerun remains a separate validation requirement.


## 2 October 2026 - Recovery 145 PMenu row chrome and menu topology

- Resumed canonical main `3adf75e713c70dd3a3cddf9f5df9db6e34e19b5d` after PR #75 had already merged; no TeamSelect or fresh-route work was repeated.
- Reused the still-healthy private canonical executable/source staging and continued from `PMenu` into its concrete row-class family: `CMenuList`, `PBaseMenuRow`, `PTitleMenuRow`, `PChildMenuRow`, `MenuTitleArrow`, `MenuBackgroundToggle`, and the title/child selection bitmap classes. The row builder advances in exact 29-pixel steps.
- Source-bound four original management-menu resources through literal path, raw handle, wrapper and concrete row setup: `menu_arrow_anim.444` + `submenu_main_box.444` for title rows, and `menu_anim.444` + `menu_main_box.444` for child rows. Their exact source sizes, SHA-256 values and EA444 geometries are persisted in `research/GATE13_PMENU_CHROME_TRACE.md` and `reconstruction/original_pmenu_chrome.py`.
- Re-read all four selected files from the authorized private source. All matched the persisted hashes, byte sizes, dimensions and original `64 ff 00 ff` EA444 descriptor. Heights resolve to exact 29-pixel stacks of 22, 3, 23 and 4 rows.
- Recovered the nine-root static menu tree at `0x947638` plus every child array. The implementation retains unresolved label globals as `None`/fail-closed. Only exact main-English loader/global correlations are named, including Team, Analysis, EAMail, Stats, Team Orders, Training, Youth Team, League Tables, Cup Tables, Stadium, Development, Maintenance, Cash Flow, Tickets and Contracts.
- A separate array at `0x9475A0` contains Formation/Stats/Ind Orders/Specific Roles/Team Orders, but its owning navigation edge is not yet proven and it is deliberately kept out of the main root hierarchy.
- `menu_anim_disabled.444` and `GenericButtonsAndBars/menu_arrow.444` were found and checked privately but are not promoted as PMenu-row resources because their ownership/state meaning is not yet source-proven.
- Exact next work after hosted validation: recover unresolved PMenu row label globals, font/color/clipping and state-to-frame mapping and/or provenance-import the four already-correlated assets. The corrected real-Windows PStartMenu/TeamSelect audit remains separately open.


## 2 October 2026 - Recovery 146 PMenu localization, font and background-state mapping

- PR #76 was revalidated after recovery and squash-merged as `addd82b7a8a5efddd83abb698f08d08c71ebcaf9`. Focused Gate-13 run `36911756061` passed **288 tests with 21 expected source-gated skips and zero failures**; asset-policy run `36911756170` passed.
- Continued directly from the merged PMenu tree rather than repeating row-resource ownership. A bounded parse of the canonical main English loader `0x635F30..0x64C7D4` found exactly **2,714** assignments through `0x64E320`, matching all 2,714 entries in the canonical `English.idx`. This closed every modeled PMenu label global by exact loader destination rather than an inferred address pattern.
- Root captions are now exact: Team, Transfers, Calendar, TABLES, Analysis, ADMIN, ACCOUNTS, EAMail and GAME OPTIONS. Modeled children are likewise exact, including Squad, Indiv. Orders, Transfer List, Scouts, Player/Club Search, League Fixtures, Charts, RATINGS, Trophy Cupboard, Overview, Support Staff, and SAVE GAME / SETTINGS / RETURN TO MAIN MENU.
- Static init `0x603640` and load path `0x604252..0x60429F` bind PMenu wrapper `0x87BEA0` to font object `0x9269F0` loaded from `Fonts/Zurich_BdXCn_BT_16pixel.fnt`. The already provenance-imported source file matches 79,722 bytes, SHA-256 `9dc371caba34823b0d6ba6fd4c5e82f94775de1168daa5dad936b70a6e4f9732`, a 1526x17 atlas and 18-pixel recovered line height.
- `PTitleMenuRow::0x47A7E0` and `PChildMenuRow::0x47A990` both supply exact grayscale component triples `(0,0,0)` and `(255,255,255)`.
- `MenuBackgroundToggle::0x47AC00` is now modeled with neutral bit positions only: bit1 `0x2`, bit3 `0x8`, bit15 `0x8000`. Source row index is 3 when bit1 is clear; otherwise 2 when bit15 is set; otherwise 1 when bit3 is set; otherwise 0. At 29 pixels per row this yields source y offsets 87/58/29/0. No hover/down/disabled semantic names are assigned without further evidence.
- Remaining PMenu source work is narrowed to the 22-row title-arrow and 23-row child-arrow animation/state mapping, any still-unresolved clipping/text-origin behavior, and shell/background resource ownership. Four row `.444` assets are source-correlated but still await intentional provenance import because the GitHub connector only exposes UTF-8 content writes; the 16px font is already imported.

- Direct binary-import transport was reprobed in Recovery 146. The GitHub connector exposes only UTF-8 contents writes, while shell `git ls-remote https://github.com/BrannMolvik/premier-league-manager-2001-research.git HEAD` failed because `github.com` could not resolve. The four proven menu-popup binaries therefore remain staged/private and unimported; this is an infrastructure/transport limitation, not missing provenance or source ownership.


## 2 October 2026 - Recovery 148 PMenu arrow animation closure

- Resumed after PR #77 had already merged as `2f59e163e873051a9bc691f6d6c04033f678ad20`; no label/font/background-state work was repeated.
- Traced the shared bitmap animation engine. `0x652AE0` maps neutral bits to states 2/1/0 by bit-`0x2` / bit-`0x8000` precedence. `0x652780` remaps frame position across state changes with exact integer division, and `0x6527F0` increments or decrements the frame according to source bit `0x8`. All bits/states remain semantically unnamed.
- Child-arrow frame-count override `0x5D62F0` yields 11/11/1 frames for states 0/1/2. Generic source-offset method `0x652860` concatenates those ranges, accounting for all 23 rows of `menu_anim.444` exactly.
- `MenuTitleArrow` overrides source offset at `0x4825A0` and frame count at `0x5D50E0`. Its 30x638 source is therefore 11 frames of 30x58, correcting the earlier provisional 22x29 interpretation. State 0 uses frames 0..10; state 1 fixes frame 10; state 2 fixes frame 0.
- Bounded PMenu constructor/setup/method tracing shows no direct original-resource handle owned by PMenu itself. `PMenu::0x47AB40` creates/configures the embedded CMenuList at +0x68 with raw setup args `(0,0,201,504,16,29,0,0,0)`; concrete menu graphics remain bound by row classes. This is not proof that the screen lacks a visible inherited/application background.
- Exact next task after hosted validation: downstream source-backed management panel composition/navigation or remaining PMenu text-origin/clipping details; real Windows corrected audit and binary asset-import transport remain open.

- PR #78's first focused CI run `36915612026` exposed one incorrect regression expectation, not a production/source-model mismatch: a state-0/frame-10 -> state-1 transition first maps to frame 10, then the same native tick sees source bit `0x8` clear and retreats to frame 9. The test is corrected to `(1, 9)`; this preserves the recovered `0x652780` + `0x6527F0` sequence instead of changing implementation to satisfy the test.


## 2 October 2026 - Recovery 149 Calendar, Tables and League Fixtures identities

- PR #78 merged as `f61146fa5dd644ecebbf032effda10dab60d7299`. Its repaired focused run `36915849517` passed 298 tests with 21 expected source-gated skips; asset-policy run `36915849434` passed.
- Continued directly through the canonical management panel factory `0x47AEC0` using exact PMenu IDs already recovered from the static tree.
- Factory dispatch and RTTI now prove `0x259 Calendar -> PCalendar2k` (case `0x47C62B`, ctor `0x47CCB0`, vtable `0x7C2F04`), `0x25A League Tables -> PLeagueTables` (case `0x47C6D1`, ctor `0x448640`, vtable `0x7C00C8`), `0x25B Cup Tables -> PCupTable2000` (case `0x47C67E`, ctor `0x44EC80`, vtable `0x7C0A78`), and direct `0x25C League Fixtures -> PLeagueFixtures` (case `0x47C724`, ctor `0x46D470`, vtable `0x7C24B8`).
- This closes the prior Fixtures/results concrete panel-identity gap for League Fixtures. Screen art, geometry, row sorting/order, date/result bindings and full navigation remain open rather than inferred from the class name.


## 2 October 2026 - Recovery 150 League Fixtures resource ownership

- PR #80 merged as `9da4c89f67aaba7b263354591497d596ca50edd1` after focused Gate-13 run `36916343766` passed 303 tests with 21 expected source-gated skips and asset policy passed in `36916343760`.
- Continued directly inside source-proven `PLeagueFixtures` setup `0x46AA70` and the canonical static graphic initializers.
- Bound six exact original paths to raw/wrapper handles and privately revalidated their original disc bytes: four 24x13 fixture boxes plus 132x52 horizontal and 24x528 vertical grid graphics. Every file matched the persisted SHA-256, byte size, dimensions and EA444 descriptor.
- `fixtures_vert_grid.444` wrapper `0x9449F0` is passed to `0x5D5280` exactly 12 times at `(378+29*n,98)`; `fixtures_hori_grid.444` wrapper `0x944A30` is passed exactly 24 times at `(241,235+14*n)`. The source helper calls are preserved rather than pretending resource dimensions equal logical cell dimensions.
- The four 24x13 wrappers `0x944B30/0x944AF0/0x944AB0/0x944A70` are selected inside contiguous PLeagueFixtures methods around `0x46CA40..0x46D25B`; their exact runtime state/result meanings remain open pending data-flow trace.


## 2 October 2026 - Recovery 151 League Fixtures box states and visible text

- PR #81 merged as `4420e2d12386b749653cbc4202cd2d3f190c1ebe`; focused Gate-13 run `36917169429` passed 309 tests with 21 expected source-gated skips, and asset-policy run `36917169401` passed.
- Continued from the already-recovered four 24x13 box wrappers into `PLeagueFixtures` row/update methods around `0x46CA40..0x46D2F9`.
- Runtime fixture `+0x44` initializes to zero near `0x5104CF`; `0x511370` sets bit 0 before its post-match processing. The League Fixtures row/update code tests that same bit. Populated fixtures with bit 0 clear use `date_fixtures_box.444`; bit 0 set uses `played_fixtures_box.444`.
- The bit-0 path reads signed fixture words `+0x3C/+0x3E` through `0x513E70/0x513E80` and exact format string `0x81C504 = "%i:%i"`. Independent `0x5112A0` copies MatchCalculator side-indexed score fields `+0xD4C/+0xD50` into those fixture words, source-proving the displayed score semantics.
- The bit-clear path calls fixture date accessor `0x510A20`, decomposes the date through `0x64CCD0`, and formats day/month with exact string `0x81C4F8 = "%02i.%02i"`.
- Current/previous selected indices at `PLeagueFixtures+0x109B4/+0x109B0` drive `toggled_fixtures_box.444`: the refresh path restores a previous index to its base played/date/red boxes, then overlays all 24 cells of the newly selected index with the toggled wrapper.
- Empty fixture slots choose red versus date from a separate boolean/table-identity predicate. Its football meaning remains intentionally unresolved rather than guessed.


## 2 October 2026 - Recovery 153 League Fixtures matrix and grid navigation

- Resumed from canonical main `cac2e5e92a6a195bf1a271e517ed90b5535f9908`; PR #82 had already merged, so prior League Fixtures panel/resource/cell-state work was not repeated.
- Closed the former empty-slot red predicate. The embedded `PLeagueGrid` at `PLeagueFixtures+0x1CF0` stores its outer panel pointer at `+0x2C`. Both compared 0x4C-stride header families are RTTI-proven `ClubText` arrays; `ClubText::0x5D5490` stores the exact supplied club pointer at `+0x48`. Equality of row and column `ClubText+0x48` selects `red_fixtures_box.444`. This is the same-club self-fixture diagonal.
- Matrix builder `0x46D950` prepares the selected competition member list through `0x4F4940`, assigns each resolved club a temporary zero-based matrix index at `club+0x2A0`, and allocates repeat layers from `0x616F40(selected_competition) / 2` using the original truncating integer sequence.
- The builder scans the global fixture chain-head region at `0x947AD8` over exactly `0x5D4` bytes = 373 heads. It accepts only virtual kind-code 1 fixtures for the selected competition, rejects fixture status `+0x44 bit 0x20`, requires both side club references, and inserts by `layer*N*N + left*N + right`. Same-pair duplicates advance by exactly `N*N`, preserving chain encounter order. Bit `0x20` remains intentionally unnamed beyond “matrix-exclusion bit”.
- The 12 visible column ClubText controls show competition members starting at panel offset `+0xA4`; the 24 row controls are layer-major `row = layer*N + club_index`. Left/right paging changes `+0xA4` by exactly 12 and clamps to 0 / `club_count-12`.
- Pointer method `0x46D300` reduces valid grid-relative coordinates by exact integer divisions `dx//29` and `dy//14`, then selects column 0..11 and row 0..23. Companion `0x46D390` performs the same lookup and calls `0x488C80` only for a non-null fixture; this downstream action remains address-only pending semantic proof.
- Added fail-closed clean-room helpers/regressions for the same-club diagonal, neutral candidate filters, repeat-layer slots, paging, selector bounds and pointer coordinate mapping. Exact next work after CI is remaining surrounding League Fixtures controls/navigation or the next highest-priority Gate-13 screen slice.


## 2 October 2026 - Recovery 154 League Fixtures country and League selectors

- PR #83 merged as `7381efcf9ca912d684406effc5ff3b4da1f2d1d8`; final focused Gate-13 run `36922149326` passed 323 tests with 21 expected source-gated skips and asset-policy run `36922149239` passed.
- Continued inside `PLeagueFixtures::0x46AA70` / `0x46D840` / `0x46E040` rather than repeating the matrix trace.
- RTTI proves both selector arrays are `fmRadioTextSm@fm2001_ctrls` (vtable `0x7D6AB8`): eight country controls at `+0x110` and six League controls at `+0x3B8`, each 0x4C bytes. A separate `LeagueFixRadioButton` class exists elsewhere and is not misapplied to these arrays.
- Exact country order/events are England 26/event1, Germany 33/2, Italy 40/3, Spain 73/4, Scotland 66/5, France 31/6, Holland 24/7, Belgium 9/8. Active country is `+0x64`; one selected-League index per country is retained at `+0x68..+0x84`.
- Initial selection comes from current club competition identity `DBRClub+0x10` and country ID `DBRClub+0x14`: the competition identity is resolved to its runtime object, then country helper `0x410FF0` finds that exact object in the country competition array. The clean-room helper fails closed if that identity is absent.
- `0x46D840` reads country competition array/count at `+0x48/+0x4C`, dynamically casts `LeagueBase` (TypeDescriptor `0x818AA0`) to concrete `League` (TypeDescriptor `0x818978`) through `__RTDynamicCast 0x668995`, retains resolved League pointers at panel `+0x88`, and uses exact `League+0x14` captions. The screen owns six League controls; unused controls are source-cleared/hidden.
- Dispatcher events 1..8 select country indices 0..7 and rebuild League radios + matrix + view; events 9..14 select League indices 0..5 and rebuild matrix + view. No generic modern competition merge/filter is introduced.
- Added exact selector helpers/regressions covering country IDs/order/events/offsets, RTTI/control addresses, six-League bounds, exact captions/selection state, current-League lookup and event dispatch. Exact next task after CI is remaining League Fixtures non-selector shell/action semantics or the next highest-priority Gate-13 presentation slice.


## 2 October 2026 - Recovery 155 League Fixtures PMatchInfo navigation

- PR #84 merged as `501707f396aa2af7ca66dffcd7a5ecf8189c4df7`; Gate-13 run `36923762250` passed 330 tests with 21 expected source-gated skips and asset-policy run `36923762398` passed.
- Continued from the previously address-only `PLeagueGrid::0x46D390 -> 0x488C80` populated-cell action. The grid loads the exact matrix fixture pointer, skips null cells, and pushes that fixture pointer directly into `0x488C80`.
- `0x488C80` calls fixture virtual slot `+0x18`, reads a signed 16-bit link index from the returned object `+0x40`, and resolves a secondary linked context through global `0x8755F8`. Missing/sentinel/unresolvable context exits without constructing a dialog.
- With a resolved context, `0x488C80` allocates exactly `0x1828` bytes and calls constructor `0x487580`. That constructor begins from `PExplodingDialog` vtable `0x7C0D54` / TypeDescriptor `0x81BB38` and finishes with vtable `0x7C41D4`; RTTI TypeDescriptor `0x81D058` identifies **PMatchInfo**.
- Constructor arg1 is the fixture-derived object from virtual +0x18 and is stored at PMatchInfo `+0x70`; arg2 is the resolved linked context stored at `+0x74`. The higher-level class/name of that secondary context remains neutral.
- Generic geometry helper `0x653320` proves the dialog width/height supplied by `0x488C80` are 760x500; x/y are dynamically clamped from source UI globals rather than fixed by this checkpoint.
- Added a fail-closed `LeagueFixturesMatchInfoAction` clean-room contract and regressions. Exact next work after CI is PMatchInfo internal presentation/resources or remaining League Fixtures non-selector controls; no modern match-info route is synthesized.


## 2 October 2026 - Recovery 156 PMatchInfo original resource ownership

- PR #85 merged as `a5c0de8aff324aa6ea8481da24da725d8921ebd4`; focused Gate-13 run `36924435622` passed 333 tests with 21 expected source-gated skips and asset-policy run `36924435665` passed.
- Freshly recovered the canonical private Library ZIP and independently rechecked its 511,121,336-byte physical size and SHA-256 `677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`. Direct Joliet extraction of both shipped `footballmanager.exe` copies reproduced canonical SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
- RTTI/source tracing binds `PMatchInfoSubPanelBase` (TD `0x81D078`, COL `0x7E4C08`, vtable `0x7C42B8`) and `PMatchInfoSubPanel` (TD `0x81D0A0`, COL `0x7E4BD0`, vtable `0x7C426C`) under the already-proven PMatchInfo dialog.
- Recovered the complete contiguous 20-entry `FM2001_Art/Generic/Match_report/*.444` static loader family from `info_player.444` through `match_incid_grid.444`. Raw handles descend exactly `0x943570 -> 0x9430B0` in 0x40 steps; each wrapper is raw-0x20.
- Every one of the 20 authorized source files was reread from the raw disc and matched its recorded SHA-256, byte size and EA444 geometry. `info_popup.444` is exactly 760x500, independently matching the recovered PMatchInfo dialog size.
- Bounded executable consumers are now persisted for 13 resources: the player row pair, popup background, seven 14x14 incident/status icons, match-name grid, pitch image and incident grid. The four name-block and three possession-strip resources remain source-owned/hash-verified but without a claimed final per-control consumer until further data-flow tracing.
- Added `original_pmatchinfo_resources.py`, strict validator/regressions and Gate-13 CI coverage. No original Match Report binary bytes entered Git.
- Exact next task after CI is PMatchInfo internal control geometry/text/font/event binding, starting from the already-proven subpanel owner graph and direct resource consumers.


## 2 October 2026 - Recovery 157 PMatchInfo local geometry and Zurich text controls

- PR #86 merged as `c304e77d81b21d1c6fde1a63b90934347926d7f1`; focused Gate-13 run `36927729023` passed 343 tests with 21 expected source-gated skips and asset-policy run `36927729082` passed.
- Traced shared control rectangle helper `0x64F380`: arg1/2 store x/y, arg3/4 form right/bottom via width/height, arg5 is retained at control `+0x28` and receives an optional virtual callback, arg6 stores at `+0x1C`.
- Fresh RTTI proves the common PMatchInfo arg5 global `0x87BF00` is `eCDBitmap` (vtable `0x7BFE14`, COL `0x7E1248`, TD `0x819C48`), not a font. The model therefore keeps it as a neutral callback target.
- Source-bound nine exact owner-local resource rectangles: two copies each of match-name `(0,0,185,36)` and incident `(189,0,142,36)` grids; yellow-card `(191,11,14,14)`; active player `(0,0,274,16)`; disabled player `(0,0,252,16)`; pitch `(233,-2,294,78)`; popup `(0,0,760,500)`.
- The disabled player control intentionally clips the 274x16 source to 252x16, and pitch keeps its negative y=-2. These are original fidelity details, not errors to normalize.
- Traced text helper `0x6503F0` into `0x64F380`. Six bounded PMatchInfo calls pass the source-proven Zurich 16px global `0x87BEA0`: `(210,2,185,12)`, `(210,18,185,12)`, `(33,0,29,16)`, `(172,50,416,16)`, `(380,68,208,16)`, `(172,68,208,16)`. The two 12px-high controls remain 12px despite the font's 18px native line height.
- Added fail-closed placement helpers/regressions and explicit separation between bitmap callback ownership and true font binding. Exact next task after CI: resolve string/data producers for these six text controls and shared incident-icon control geometry, then continue PMatchInfo events/remaining resource consumers.


## 2 October 2026 - Recovery 158 PMatchInfo shared incident control

- PR #87 merged as `1fb35fbc8e0b36f3fefc7aad00e5cea388383a39`; focused Gate-13 run `36929308062` passed **351 tests with 21 expected source-gated skips and zero failures** and asset-policy run `36929308094` passed.
- Reconciled the final persisted Recovery-157 branch trace instead of repeating private-source work: `PScriptRow1` (TD `0x81CEE8`, vtable `0x7C3F34`) and `PScriptRow2` (TD `0x81CF08`, vtable `0x7C3F88`) share setup `0x483500` and update at `0x4858E0` / `0x485F50`.
- Source-bound shared dynamic incident control offset `+0x1C8`, switched resource slot `+0x1F4`, and owner-local rectangle `(191,11,14,14)`. The setup path seeds the same rectangle with `yellow_card.444`.
- Both update methods directly consume the same seven exact 14x14 wrappers: score, injury, yellow card, red card, single red card, substitution on and substitution off. Regression coverage now joins those consumers to the row methods without inventing the still-unresolved selection predicates.
- Exact next task after CI: resolve string/data producers and meanings for the six bounded Zurich text controls; then continue PMatchInfo incident predicates/events and the seven remaining name-block/possession final consumers.


## 2 October 2026 - Recovery 158 PMatchInfo text producer source continuation

- PR #88 merged as `6ae2f39caba70e8f31ec651cf98ccaff1be832a6`; Gate-13 run `36933211315` passed **352 tests with 21 expected source-gated skips and zero failures**, and asset-policy run `36933211343` passed.
- Freshly reread the authorized 511,121,336-byte source archive and independently re-extracted both original `footballmanager.exe` copies. Both match canonical SHA-256 `833bf95e6aae1b4c5e28d07e1bef272c03b9720cdf96572fdd4a7113f5104cc3`.
- Recovered the original `English.idx` / `English.str` pair and source-joined the complete 2,714-entry loader at `0x635F30..0x64C7D4` to the PMatchInfo globals used by the bounded text paths.
- Both `PScriptRow1` / `PScriptRow2` populate the first 185x12 control from row buffer `+0xA0` and the second from `+0x80`. The first is the incident/event description line. The second formats `event_record+0x00` via `%d`; its higher-level gameplay meaning remains deliberately neutral.
- Closed the exact row incident selection predicates without renaming source flags: types 0..4 select Goal/O.G./Shoot Out + score; type 5 checks event `+0x20` Injury first, then `+0x18` Booking, then `+0x1C` Sent off with the two red-card wrappers split by row `+0x74`; types 6..9 do not take a bounded incident branch; type 10 selects Sub On/Off by row `+0x74`.
- Source-bound the 29x16 player-strip text to the selected `DBTPositions` record's string field `+0x0C` (TD `0x8182F8`, vtable `0x7BD394`, 20-byte records), using low five bits returned by helper `0x4EA3C0`.
- Source-bound popup producer `0x4885A0`: `Attendance` (English.idx 1774) with original grouped decimal formatting and optional first/second-leg suffix, `Ref.` (2555) with dynamic source string producer `0x60BEB0` and optional `(%d-%d pen)`, and `Mom` (2128) through source format `%s: %s %s`.
- Added a clean-room text-producer contract and regressions that preserve exact globals, loader indices, object offsets, assignment VAs and source precedence. Exact next task after CI is PMatchInfo event/tab interaction behavior and/or the seven still-unmapped name-block/possession consumers.


## 2 October 2026 - PMatchInfo tab and exit interaction

- PR #89 merged as `5603f96fddee9de4b02d40c0a199fe66eea415ca`; Gate-13 run `36934794672` passed **357 tests with 21 expected source-gated skips and zero failures** and asset-policy run `36934794463` passed.
- Traced the exact three-element `fmRadioButton6` array (vtable `0x7C4474`, TD `0x81D108`) at PMatchInfo `+0x14A4/+0x14F8/+0x154C`; base binder `0x64F3C0` stores event IDs 1/2/3 at control `+0x20`.
- Source-bound captions through the complete English loader: `MATCH INFO` (entry 1776), `TEAM INFO` (1775), and `FINANCIAL` (2556).
- RTTI/source-bound tab targets: `PMatchInfoSubPanel` `+0x1C0`, `PTeamInfoSubPanel` `+0x8F0` (TD `0x81D038`, vtable `0x7C4220`), and `PFinanceSubPanel` `+0xB10` (TD `0x81D1E8`, vtable `0x7C4530`). Constructor `0x4879C6` stores the `+0x1C0` pointer as the setup default.
- Event handler `0x488B70` rewires the RTTI-proven `eCSubPanel` at `+0x17A8`, sets selected panel `+0x04=2`, panel `+0x08=host`, reapplies the host rectangle through `0x653320`, and refreshes through `0x64F600`.
- RTTI proves the `+0x17D8` exit control is `fmCrossButton`. Its event ID 7 and key-handler value `0x1B` both call `0x6539F0(7)`; that path reaches imported `PostMessageA` with exact tuple `(WM_USER=0x400, wParam=7, lParam=0)`. Receiver-side higher-level naming is intentionally left open.
- Exact next task after CI: recover final direct consumers for the four name-block and three possession-strip resources, then continue Match Report asset import and integrated Windows validation.


## 2 October 2026 - Recovery 159 final PMatchInfo resource-consumer audit

- Resumed from merged PR #90 at `ab39fd753e94c6ccfcea13ebbcd1d9576133efdb`; its Gate-13 run `36935848636` passed **360 tests with 21 expected source-gated skips and zero failures**, and asset-policy run `36935848660` passed.
- Freshly reread canonical `footballmanager.exe` and exhaustively scanned the seven still-unmapped Match Report resources: `name_block_1..4`, `poss_back`, `poss_blue`, and `poss_yellow`.
- Scanned each exact raw handle, every aligned field address in each 0x20-byte wrapper, and the surrounding `0x9430xx..0x9433xx` resource-family range. Also checked the concrete Match Info / Team Info / Finance subpanel and dialog methods.
- All seven files are loaded and receive valid static wrapper setup, but every executable literal xref is confined to static construction/teardown plus family-wide lifetime sweeps at `0x6017xx` / `0x6029xx`. No runtime PMatchInfo/TeamInfo/Finance presentation consumer exists in the canonical executable.
- Recorded exact xref sets in `PMATCHINFO_UNCONSUMED_RESOURCE_AUDIT` and added a fail-closed regression boundary so these resources cannot be assigned to widgets without new source evidence.
- This closes the seven-resource mapping question as **loaded-but-unconsumed**, not as a guessed UI binding. Exact next task after CI is intentional staging/import of only source-proven Match Report assets, integration into the reconstructed presentation, then corrected Windows validation and Gate-13 audit.


## 2 October 2026 - Recovery 159 PMatchInfo runtime asset staging

- PR #91 merged as `ae324cb3ba585dff1f96ff19053e35bc62917540`; Gate-13 run `36938526562` passed 361 tests with 21 expected source-gated skips and asset-policy run `36938526517` passed.
- Created `feature/gate13-pmatchinfo-asset-import` and imported twelve byte-identical Match Report files that have source-proven runtime presentation consumers: info_player, info_player_disabled, red/yellow card variants, substitution on/off, injured, score, match-name grid, pitch and incident grid.
- Preserved original source path casing for `Sub_on.444`, recorded every source SHA-256 in `original_assets/MANIFEST.md`, and added a repository-side validator that rechecks SHA-256, byte size and EA444 geometry in CI.
- Deliberately did not import the seven Recovery-159 loaded-but-unconsumed name-block/possession files into the runtime set.
- `info_popup.444` remains the only source-proven runtime asset not yet staged. The current GitHub connector cannot safely transmit its 179,988 raw binary bytes in a single blob handoff without truncation. No substitute, conversion or guessed background is allowed. The branch explicitly tests that this missing file remains absent rather than silently replaced.
- Exact next task: run the partial import checkpoint through Gate-13/asset-policy CI, then build the reconstructed PMatchInfo presenter so the source-proven subcomponents can integrate while the full-dialog background fails closed until its exact bytes can be transferred.


## 2 October 2026 - Recovery 160 PMatchInfo presenter integration

- PR #92 merged as `b13e271e9a9014a340f6c6399256108c42f61325` after Gate-13 run `36941189265` passed **363 tests with 21 expected source-gated skips and zero failures** and asset-policy run `36941189310` passed.
- Recovered the canonical 511,121,336-byte Library source ZIP again, reverified SHA-256 `677dcbc...a8a4`, extracted the raw Mode-1 disc image, and used its Joliet filesystem to source exact Match Report bytes.
- The first PR #92 run correctly caught a byte-size mismatch in `info_player_disabled.444`; a full Git-blob comparison then found `pitch_normal.444` was also truncated. Both were replaced from the canonical disc. All twelve staged runtime Match Report files now have exact Git blob identities matching local canonical source objects.
- Added `original_pmatchinfo_presenter.py`, a read-only, simulation-independent presentation seam over the recovered PMatchInfo contract. It preserves the exact 760x500 dialog size, tabs/default panel, six text rectangles, eight static placements currently available, the pitch's -2 local y origin, the 252x16 source clipping of the disabled 274x16 strip, and the source-proven incident-art selector.
- The presenter refuses a complete-dialog snapshot unless the exact `info_popup.444` is present. It does not translate modern `MatchEvent` objects into original PScriptRow event types because that semantic bridge is not source-proven.
- Exact next step after CI: merge this presenter checkpoint, then continue the strongest source-backed Gate-13 integration/audit path while preserving the popup transport blocker and real-Windows validation requirement.


## 2 October 2026 - Recovery 161 League Tables selector/header shell

- PR #93 merged as `5f76cd8d1187601034424fd6519c29c521b912bc`; focused Gate-13 run `36943619177` passed **364 tests with 21 expected source-gated skips and zero failures**, and asset-policy run `36943619314` passed.
- Continued source recovery on the RTTI-proven `PLeagueTables` panel (TD `0x81B458`, vtable `0x7C00C8`, constructor `0x448640`) through main setup `0x446F00` and event dispatch `0x448C40`.
- Source-bound eight `fmRadioTextSm` country controls beginning at object `+0x23C` and the constructor's exact country identity array at `+0x1D4`: England 26, Germany 33, Italy 40, Spain 73, Scotland 66, France 31, Holland 24, Belgium 9. Events 1..8 map directly to active-country index 0..7 at `+0x64`.
- Source-bound the country caption control at `+0x1F4` to English loader global `0x982670` / index 2146 / exact text `Country`.
- Recovered the table-header band through shared text setup `0x6503F0`: a neutral 214x19 slot at (316,152), then exact 27x19 columns P/W/D/L/F/A/Pts at x=532/561/590/619/648/677/706, y=152. Loader globals `0x9830F4..0x9830DC` resolve to indices 1473..1479.
- Bounded but did not semantically name two further `fmRadioTextSm` families: five controls at `+0x4E4` and two controls at `+0x6A8`. Exact next task after CI is events 9..15 plus their data/text producers, then League Tables row identity/geometry/resource ownership.

- Recovery 161 continuation closed events 9..15: source global `0x982678` / English index 2144 is **DIVISION**; five controls at `+0x4E4` use events 9..13 and are rebuilt by `0x448E60` from the active country's non-`DummyLeague` `LeagueBase` entries, exposing source caption `+0x14` and identity word `+0x20`. The selected index/identity live at `+0x68/+0x8C`.
- Source global `0x983A94` / index 857 is **Sort By**. Event 14 is **League Position** (global `0x983C04`, index 765, sort state 0); event 15 is **Current Form** (global `0x983A90`, index 858, state 1). Object `+0x98` is explicitly initialized to 0, making League Position the source default; `0x449090` applies the mode to the seven downstream table/display controls.


## 2 October 2026 - Recovery 162 League Tables body and original graphics

- Continued from merged League Tables selector/header shell at main `3c19c4fff22cc397fe3728e8f6e21fc7896075e0`.
- RTTI/source tracing identifies panel `+0x9BC` as `CLeagueTableList` (TD `0x81B478`, COL `0x7E1520`, vtable `0x7C011C`) and its row factory `0x447820` as constructing `PLeagueTableRow` (TD `0x81B378`, COL `0x7E1398`, vtable `0x7BFEC0`) in 0x4A8-byte objects.
- Source setup `0x4477E0 -> 0x6510F0` binds the table body at exact local rectangle `(270,184,477,384)` with native 24-row capacity and 16px row step.
- Each row source-binds rank `(23,1,21,12)`, name `(46,1,214,12)`, and seven 27x12 stat controls at x `262,291,320,349,378,407,436`. Added to list x=270, the seven stat positions align exactly under the recovered P/W/D/L/F/A/Pts headers.
- The source row record projects P/W/D/L/F/A from exact offsets `+0x10/+0x14/+0x18/+0x1C/+0x20/+0x24`; points are explicitly computed as `3*(+0x14) + (+0x18)`, i.e. **3*W + D**.
- Fresh raw-disc extraction source-binds all 15 `FM2001_Art/Generic/league_tables/*.444` files with exact SHA-256, byte size, geometry and raw/wrapper handles: six 477x14 grid strips, eight 20x12 normal/your status icons, and `league_bar.444` 475x19.
- Row source branches select champion/promotion/relegation/playoff/standard/your-team strips and paired icon wrappers. The helper byte returned through `0x4037B0` remains semantically neutral; only its exact art-selection consequence is recorded.
- Exact next task after CI: integrate the source-bound League Tables body in the reconstruction, stage/import exact original resources where safe transport permits, then continue the next Gate-13 presentation gap and corrected Windows validation.

- PR #95 merged as `7578e465fbc952a74ee1268b698dde7d26ee2a8b`; Gate-13 run `36949336841` passed **379 tests with 21 expected source-gated skips and zero failures**, and asset-policy run `36949336761` passed.
- Recovery 162's authorized source ZIP was successfully resolved/materialized, but all available execution sandboxes then failed before even trivial byte processing with `caas.internal.errors.ClientError`. The seven downstream display controls at `+0x7FC..+0x97C` therefore remain an explicit deferred private-source trace, not a guessed presentation binding.
- Canonical next task: integrate the already source-bound League Tables selector/header/body/row contract through a simulation-independent presentation seam, failing closed where exact row-art selection or unstaged original bytes are not source-proven.

## 2 October 2026 - Recovery 164 League Tables presenter integration

- Recovered the interrupted presenter stack from `feature/gate13-league-tables-presenter`, audited it against canonical Recovery 162, and rebuilt it cleanly on current main without carrying stale state-file edits.
- PR #96 merged as `95b566a50d749d17bcf0324b46582c9bc215b65b`. Gate-13 run `36953094233` passed **388 tests with 21 expected source-gated skips and zero failures**; full reconstruction run `36953094137` passed **1,285 tests with 22 expected source-gated skips and zero failures**; asset-policy run `36953094185` passed.
- The development League Tables view now consumes the simulation-independent source presenter, restores the source-visible F/A columns, removes the unsupported GD substitution, enforces the native 24-row capacity and `Pts=3*W+D`, and fails closed for Current Form ordering and unstaged exact art.
- Private blockers remain unchanged: local execution still fails before process start with `caas.internal.errors.ClientError`; Current Form `0x4F4A10`, downstream controls `+0x7FC..+0x97C`, byte-identical League Tables art staging, and corrected Windows/Tk validation therefore remain deferred rather than guessed.
- Next cloud-safe task: extend the already source-proven Squad presentation seam with the recovered six-match performance average and current assigned-role rating, then bind only the exact row-column geometry that is already evidenced.


## 2 October 2026 - Recovery 170 management routing checkpoint

PR #98 adds a source-bounded ordinary-management routing layer over the
recovered PMenu. A started TeamSelect session can now project the exact fresh
PSquadScreen route (0xCE), League Fixtures (0x25C), and League Tables (0x25A)
through the existing read-only presentation bridge. The League Fixtures route
preserves recovered fixture source order; League Tables reuses its strict
source presenter; and PMatchInfo is exposed only through the already-proven
fixture-present + linked-context action gates. Unsupported PMenu children fail
closed transactionally instead of dropping into the generic ttk prototype.

GitHub Actions Gate-13 run `36968140361` passed **403 tests, 21 expected
source-gated skips, zero failures** on
`30cfc7fdc999d5bc0e005a5a5bc0bc78525aaecd`. Repository asset-policy run
`36968140362` also passed.

The authorized 511,121,336-byte original Library ZIP was successfully
rematerialized during this recovery. Fresh private native tracing could not
continue because both available execution backends failed before process start
with `caas.internal.errors.ClientError`. Consequently no new claim is made
about the unresolved PMenu text origin/clipping or surrounding management
background. Work continues cloud-safely until execution recovers.


## 2 October 2026 - Recovery 171 fixed PMenu management host

PR #100 merged the first live post-TeamSelect management host. Successful
single-user Start now enters an explicit `FrontEndScreen.MANAGEMENT` state and
the Tk source viewer switches to a fixed **800x600** management host backed by
`OriginalManagementPresenter`. The host preserves the executable-recovered
PMenu **(599,96,201,504)** and fresh PSquadScreen **(0,79,800,520)** parent
geometry, including their native overlap.

The host intentionally renders no invented surrounding management pixels.
Exact PMenu label origin/clipping and any additional application-owned
background layer are still unresolved and exposed as fail-closed flags.

Verification on exact PR head
`4551e0a5e178a850a8cdf6930beff75cc84bbbc8`:
Gate-13 run `36971906350` passed **415 tests, 21 expected skips, zero
failures**; asset-policy run `36971906383` passed. PR #100 merged as
`163071883b932067a5cf33cf12ff3d05a2940cb5`.

A fresh process-sandbox probe still fails before process start with
`caas.internal.errors.ClientError`, so private executable tracing remains a
deferred infrastructure blocker while cloud-safe integration continues.


## 2 October 2026 - Recovery 171 source-backed default application host

PR #101 replaced the generic ttk notebook as the normal application launch with
a clean fixed **800x600** source-backed FM2001 host. The host loads the
provenance-tracked PStartMenu and TeamSelect resource set from
`original_assets/source`, uses the canonical installed `FOOTBAL.EXE` for
the verified original EA444 decode tables, and routes the first-screen flow
through `FrontEndSession` into the explicit MANAGEMENT/PMenu state. The old
ttk notebook remains an explicit `--prototype-ui` development fallback only.

The management state still draws no guessed background/text. The previous
TeamSelect frame is cleared and the recovered management presenter remains
attached while exact management background ownership and PMenu label
origin/clipping stay fail-closed.

Verification on exact PR head
`f1653cef39182c744e88c03c8e8f83b30418a95d`:
Gate-13 run `36972538322` passed **419 tests / 21 expected skips**; full
reconstruction run `36972538328` passed **1,321 tests / 22 expected skips**;
asset-policy run `36972538362` passed. PR #101 merged as
`62a1bbcd24bf1dc26e57294e40fef176a4f87036`.

The next cloud-safe checkpoint, PR #102, intentionally adds only candidate
PMenu row hit-testing from proven geometry and does not infer row activation.


## 2 October 2026 - Recovery 172 Windows management audit harness

PR #104 merged as `c0b2fd2465952d2f5134837054622c2706abda71`.
The fail-closed real Windows/Tk audit now extends the verified TeamSelect path
through a positive native-club selection and Start into the recovered
MANAGEMENT/PMenu host. The schema-4 contract requires the fixed 800x600 canvas,
PMenu rectangle (599,96,201,504), fresh PSquadScreen parent
(0,79,800,520), panel code 0xCE and PSquadScreen identity. It also requires no
management PhotoImages while the surrounding management background and exact
PMenu label placement remain unresolved.

Gate-13 CI run `36974932379` passed **427 tests with 21 expected skips and
zero failures** on the exact PR head. Repository asset-policy run
`36974932407` passed. The upgraded audit contract is therefore verified in
the repository; an actual new schema-4 Windows 11 receipt remains a separate
local graphical validation step.


## 2 October 2026 - Recovery 172 clean-host and PMenu input checkpoints

Three verified Gate-13 checkpoints landed after the fixed MANAGEMENT host:

- PR #105 -> `8b36c566ababdf52a8574d5c8753f92aad641fc4`: the
  diagnostic viewer now routes management clicks through the recovered PMenu
  candidate-row geometry while dispatching no navigation.
- PR #106 -> `45844074b4ad7128903fd3ed7b9a840dc82dbc74`: the same
  non-activating candidate feedback is integrated into the default
  `OriginalGameTkHost`.
- PR #107 -> `a79edc86e0333fb856539274e12113d85de868c8`: the real
  Windows/Tk audit contract is schema 5 and now exercises the default clean host
  through New Game -> native club -> Start -> MANAGEMENT, verifies exact
  management geometry and zero guessed pixels, and confirms PMenu candidate
  clicks do not mutate selection.

The final PR #107 Gate-13 run `36975636316` passed **427 tests with 21
expected skips** and asset-policy run `36975636285` passed. A new schema-5
real Windows 11 receipt remains pending.

A fresh trivial container process probe still fails before start with
`caas.internal.errors.ClientError`. A repository-only evidence sweep found no
persisted native PMenu row-event ownership trace sufficient to implement
activation safely, so activation/text/background work remains blocked on fresh
private execution rather than being guessed.


## 2 October 2026 - Recovery 173 sandbox recovery and PMenu action ownership

- Recovery 173 resumed from main `82a89e9c18c4a96951f00321b4e0932af6eb216d`.
- Independent Gate-14 PR #109 completed Gate-13 presentation CI, the full
  reconstruction suite, and asset-policy CI successfully, then squash-merged to
  main as `94d9702c0e4fce3fd215ec4741755cf8630751b3`. The clean host now has
  explicit receipt-driven verified startup-media playback through a caller-
  configured synchronous player command; no skip/fade/scaling semantics were
  invented.
- The process sandbox recovered. The authorized 511,121,336-byte Library source
  ZIP rehashed exactly to
  `677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`.
  Both executable copies extracted directly from the raw MODE1/2352 Joliet
  image rehashed to canonical
  `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
- Fresh private disassembly closes PMenu row action ownership. The common
  `PBaseMenuRow` action slot at vtable `+0x10` is pure; title and child rows
  override it at `0x47AC60` and `0x47AD60`. The generic accepted-control
  path dispatches through the parent row's `+0x10` slot at the call ending
  `0x64FF21`.
- Title action resolves the node through `0x60CA70`, clears bit 0 on other
  expandable roots, sets target node `+0x14 bit 0`, then refreshes the owner.
  Child action gates on target bits 0/1, reads exact node `+0x0C`, and calls
  management panel factory `0x47AEC0(menu_id, 0)` before committing the child
  selection and owner refresh.
- `reconstruction/original_pmenu_activation.py` and focused regressions now
  preserve this source contract. The seam deliberately begins after the
  original child control accepts an event, so the existing Tk rectangle hit is
  not yet promoted to a native click-equivalence claim.
- Exact next task: complete the PMenu label origin/clipping trace and the source
  control-acceptance boundary, then wire only source-proven activation into the
  clean host. The real Windows 11 schema-5 graphical receipt remains pending.

## 2 October Recovery 175 - source-accepted PMenu action integration

PR #111 squash-merged as `9e8f7a18368b8ce7076126a55b2e99563197659a`.
The management presenter now models the expanded PMenu root independently
from the selected panel, so an accepted title-row action can expose Calendar
or TABLES children without silently changing the current Squad/Fixtures panel.
The explicit source-accepted seam requires the target row to be visible,
preserves rejected actions without mutation, and transactionally routes the
already-source-proven child IDs into the existing Squad, League Fixtures and
League Tables presenters. `OriginalGameTkHost` exposes this seam separately
from `on_click`; ordinary Tk pointer hits remain candidate-only and dispatch
no navigation until source control acceptance/event equivalence is recovered.

Verification on PR head `776b1040ea90397c1f467fe990f1048781f9da1a`:

- Gate-13 run `36986776362`: **440 tests passed, 21 expected skips**;
- full reconstruction run `36986776403`: **1,350 tests passed, 22 expected skips**;
- asset-policy run `36986776562`: passed.

A fresh process probe in Recovery 175 still fails before process start with
`caas.internal.errors.ClientError`. Private executable tracing therefore
remains blocked for exact PMenu text origin/clipping, any still-missing
application-owned management pixels, and the source control-acceptance ->
modern Tk-event equivalence. This is an infrastructure blocker, not a user
action requirement.

Next: extend the Windows audit contract to exercise the explicit
source-accepted action seam separately from ordinary non-activating Tk hits,
then resume the private PMenu text/control-acceptance trace when execution
recovers. A fresh real Windows 11 audit receipt is still required.
