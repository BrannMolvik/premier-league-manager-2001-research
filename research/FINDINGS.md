# Confirmed Findings

This document contains technical findings that have been directly verified against the user's FM2001 disc image and derived analysis files.

## Binary identities

SHA-256 values for the analyzed files:

- `footballmanager.exe`: `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`
- `Editor.exe`: `0dd121f1e27906b7c839374288cfb497e38c87595b4736ee2c9febbe956408c5`
- `Master.dat`: `183dd457d09ce616f99a664636727668ec15eab3f65b9057ef0953e76548b6b8`
- `Static.dat`: `e0ff7c10a5f5f973a87cf6cd2d3770e623071899a0b30378debd0e7d13edb9d8`
- `English.str`: `aa594a55ad95c672b69184e5f3ff8349e41fe95b48c5dcb3c8fcfe2bcdf5b601`
- `Core.str`: `b0800475769fa087e69de989388569e5b29f495e5abe5d62687c2acb1d339e06`

These hashes define the exact analyzed dataset and should be checked before assuming offsets apply to another release.

## String tables

`English.str` and `Core.str` are indexed string tables.

Observed structure:

- file offset +0: uint32 string-data/table boundary
- file offset +4: uint32 string count
- index begins at `table_offset + 8`
- index contains `count` uint32 relative offsets
- each string is NUL-terminated and decoded correctly as Windows-1252
- string byte position is `8 + indexed_offset`

Decoded counts in this release:

- `Core.str`: about 29,033 strings
- `English.str`: about 21,856 strings

`Core.str` contains large numbers of person-name components; early entries resolve the Arsenal-era player sequence beginning David Seaman, Lee Dixon, Nigel Winterburn, etc.

## Master.dat

`Master.dat` is structured and directly parseable, not encrypted.

### Top-level layout

- uint32 club count at file +0
- 1,246 club records
- club record size: 181 bytes
- after club records: uint32 player count (=30,064)
- 30,064 player records
- player record size: 103 bytes
- after player records: uint32 manager count (=1,612)
- 1,612 manager records
- manager record size: 43 bytes
- manager array ends exactly at EOF

### Club records

Confirmed fields:

- +4 uint16: club full-name string ID in `English.str`
- +6 uint16: club short-name string ID in `English.str`
- +16 uint16: map-file string ID
- +30 uint16: stadium-name string ID
- +44 uint16: badge-file string ID
- +46 uint16: sponsor string ID
- +48 uint32: manager record ID

Record 0 resolves to Arsenal and includes strings/assets for Arsenal/Highbury.

### Player records

EA's actual compact importer at `0x418B90` proves the 103-byte layout and expands each record into a 592-byte runtime `DBRPlayer`.

Confirmed:

- player section header is exactly 4 bytes: uint32 count = 30,064
- compact record size: 103 bytes
- +0 uint16: player record ID
- +2 uint16: first-name ID in `Core.str`
- +4 uint16: surname ID in `Core.str`
- +6 uint16: current club record index
- +8 uint8: nationality ID
- +9 uint8: primary/default zero-based position code
- +14 uint32: date of birth, OLE-style serial date using epoch 1899-12-30
- +18 uint8: shirt/squad number
- +19 uint8: height in centimeters
- +20 uint8: weight in kilograms
- +21..+23: three zero-based position codes
- +24..+40: 17 current-skill bytes
- +41..+57: 17 corresponding peak/development-target bytes

The complete skill order is:

`Speed, Strength, Stamina, Determination, Injury Proneness, Passing, Shooting, Tackling, Heading, Control, Technique, Awareness, Agility, Goalkeeping, Confidence, Leadership, Set Piece`.

Exact raw-byte to displayed 0..30 conversion:

`floor((30*raw + 128) / 255)`

Examples under the corrected alignment:
- record 0: David Seaman, club ID 0 (Arsenal)
- record 1: Lee Dixon, club ID 0 (Arsenal)
- record 2: Nigel Winterburn, club ID 18 (West Ham United)
- record 3: Steve Bould, club ID 105 (Sunderland)
- record 4: Tony Adams, club ID 0 (Arsenal)

The second 17-byte array is a peak/development target, not an invariant hard ceiling; target values lower than current are valid and are handled by the recovered aging/development formulas.

### Manager records

The manager section begins with a uint32 count (=1,612), followed by 1,612 packed 43-byte records ending exactly at EOF.

Confirmed fields:

- +0 uint32: manager record ID
- +4 uint16: first-name string ID in `Core.str`
- +6 uint16: surname string ID in `Core.str`
- +8 uint32: date of birth, OLE-style serial date
- +20 uint32: date joined club
- +27 uint32: club ID; `0xffffffff` indicates no current club

Examples:

- manager 10 -> Alex Ferguson, DOB 1941-12-31, joined 1986-11-06, club ID 10
- manager 204 -> Arsène Wenger, DOB 1958-01-01, joined 1996-09-30, club ID 0 (Arsenal)
- Arsenal club record points to manager record 204

## Static.dat

`Static.dat` is a concatenation of typed tables that correspond closely to database classes visible through MSVC RTTI in `footballmanager.exe`.

Confirmed tables:

### Position table

- table offset: `0x25E0`
- count: 20
- record size: 7 bytes
- +0 uint8: position ID
- +1 uint16: long position-name string ID in `English.str`
- +3 uint16: abbreviation string ID in `English.str`

Records decode to positions including Goalkeeper/GK and Right Back/RB.

### Competition table

- table offset: `0x2726`
- count: 193
- record size: 53 bytes
- +0 uint32: competition ID
- +12 uint16: competition-name string ID in `English.str`

Decoded competition names include the F.A. Premier League, FA Cup, English Divisions 1/2/3, League Cup, Charity Shield, Conference, Champions League, UEFA Cup, playoffs and competitions from other countries.

## Executable architecture

The executable contains original source-path strings and MSVC RTTI revealing a modular C++ architecture.

Verified source-path/module strings include:

- `Applications\\FootballManager\\Season.cpp`
- `Training.cpp`
- `Scouting.cpp`
- `TransPan.cpp`
- `Youth.cpp`
- `MatchFrontEnd.cpp`
- `FastView\\MatchController.cpp`
- `FastView\\PossessionFigures.cpp`
- `Libraries\\Database\\Club.cpp`
- `Libraries\\Database\\Player.cpp`
- `Libraries\\Database\\Competitions.cpp`
- `Libraries\\Database\\Match.cpp`
- `Libraries\\Database\\Game.cpp`
- `Libraries\\Database\\PlayerMovements.cpp`
- `Libraries\\Database\\ManagerMovements.cpp`
- `Libraries\\MatchCalculator\\MatchRecord.cpp`
- `Libraries\\MatchEngine\\MatchEngine.cpp`

RTTI also exposes record/table classes for clubs, players, managers, countries, nationalities, positions, statuses, rounds, competitions, league allocation, cup allocation, fixtures, manager ratings/sacking, formations and additional systems.

## Player development and training

Confirmed:

- runtime player size is 592 bytes;
- current skills are runtime +0x1E..+0x2E;
- development targets are runtime +0x2F..+0x3F;
- baseline skill snapshot is +0x111..+0x121;
- individualized age peaks are stored at +0x123/+0x124/+0x125;
- shipped peak ranges are physical 25-26, outfield skill 27-29, goalkeeper/late group 30-32, with AGEPeakPeriod = 5;
- the main development recalculation is monthly and uses the recovered piecewise age interpolation/decline formulas;
- each club owns 40 × 200-byte per-player training records;
- training methods are 0 rest/recovery, 1 attacking, 2 midfield, 3 defensive, 4 goalkeeper, 5 fitness, 6 technique;
- active training success uses `random(0..99) < profileWeight * Q * 0.5`;
- Youth Team Coach quality sets Q to 1.25/1.30/1.35/1.40/1.45, Assistant Manager fallback gives 1.25, and a Training Centre adds 0.25;
- a successful active-training skill step adds +8 raw skill while below the development target.

## Contracts, transfers and finance

Confirmed:

- player weekly wage is runtime +0xC4;
- player contract expiry is runtime +0x154;
- negotiated contract terms include wage, signing-on fee, promotion bonus, contract length, appearance fee, relegation transfer-request clause, big-club clause, big-money clause, house and car;
- live transfer proposal is 0x50 bytes and supports up to three exchange players;
- `CDealInProgress` is 0x68 bytes;
- `CPlayerMovement` is a 0x18-byte completed-transfer history record;
- movement fee sentinel 1 means free transfer and 2 means Bosman;
- state 2/5 in the deal-state family is the player-rejected/declined-contract outcome; +3 denotes swap/exchange variants;
- completed transfers use MPM transfer-execution objects, log history, switch the player's club, stamp join date and clear transient transfer state;
- buyer cash is debited and seller cash credited by the same transfer amount through Balance.cpp;
- live cash/balance and chairman-assigned transfer budget are separate concepts;
- chairman/start-season/monthly budget message layouts and all global budget-default addresses are mapped;
- the authoritative live transfer-budget store is still unresolved.

## Match subsystem

Static RTTI/string evidence shows an event-driven separation between calculation and presentation.

Identified event concepts/classes include:

- goal
- own goal
- possession
- score
- substitution
- half time
- full time
- extra time
- penalties
- player form/energy updates

The executable distinguishes backend match calculation from FastView/3D presentation.

The exact disc contains **235 loose .SCI files**. The 3D scenario layer is now known to be structured and data-driven: loose SCTABLE.STI has 137 fixed 48-byte scenario-selection records; AISCRIPT.VIV, MOAI.VIV and GEN4TBLS.T are BIGF archives; MOAI.VIV contains 584 motion/animation-named entries; and all 584 nonblank AISEQS secondary names map exactly to those MOAI entries. CAMERA.SCR is plaintext. The internal SCI instruction/choreography semantics are still not decoded.

## Simulation tuning

The executable contains hundreds of named tuning keys covering areas such as:

- transfer budgets and wage budgets
- transfer limits and negotiations
- injuries
- player aging/development
- stadium costs
- attendance
- merchandising and ticketing
- loans/APR
- training
- youth generation
- tactical biases
- pitch/weather
- manager sacking
- role-specific match-performance rating weights

Static disassembly shows a named-key loader that parses values into global simulation variables. The value source and full variable mapping remain active research targets.

## Runtime compatibility

On the user's Windows 11 system, Code Integrity/Smart App Control blocks the legacy unsigned `footballmanager.exe` before meaningful execution.

Verified:

- launching produces only a brief shell spinner
- Command Prompt launch returned `-1` during earlier tests
- admin launch does not solve it
- Code Integrity Operational log Event ID 3077 explicitly names `C:\Games\FM2001\footballmanager.exe`

Compatibility mode, command-line launch and administrator elevation do not bypass that policy.


## Contracts, transfers and finance — manager funding request

Confirmed additionally:

- `EAMFundRequest` = event ID 0x185;
- `EAMFundRequestReject` = 0x186;
- `EAMFundRequestAccept` = 0x187;
- accepted request +0x3C is the granted amount and +0x40 is the repayment term in months;
- `FUNDMaxReqPerYear` and `FUNDMaxTimeToRepay` are live tuning inputs to this system;
- accepted manager funding requests credit the club's current cash through Balance credit routine `0x5DC510`;
- this repayable cash-funding system is distinct from the automatic chairman transfer-budget-increase event family.


## Runtime ownership correction

Older notes often call the large object returned/used throughout manager gameplay the "game/session" object. RTTI now identifies it as **DBRUser**. Existing offsets such as +0x670 Balance, +0x690 concessions, +0x698 bank loans, +0x6B0 stadium, etc. remain valid; only the ownership terminology changes.


## Runtime user / finance architecture

Confirmed:

- the large runtime object previously described in older notes as the game/session object is RTTI-identified as **DBRUser** (vtable `0x7BDF4C`);
- DBRUser owns six Balance pointers at `+0x670..+0x684`;
- current cash is the qword at active Balance `+0x10`;
- completed transfer purchases debit this cash and sales credit it;
- accounting category 1000 is used for transfer postings and has a dedicated Finance Overview aggregate path;
- accounting category 1100 is used by stadium/grounds/facility expenditure paths;
- manager `FundRequest` / `FundRequestAccept` is a separate repayable cash-funding system and accepted requests credit current cash;
- the Balance `+0x30..+0x80` block is manager financial-objective/forecast state, not chairman spending budgets;
- DBRUser `+0x698` is bank-loan state, `+0x690` concession offers, `+0x69C` sponsor offers, and `+0x6B0` stadium/building/ticketing state;
- persistent monthly finance snapshots are RTTI-identified as `CMonthHistory` and are stored through the DBRUser history container around `+0x6DC`;
- the five qwords beginning at DBRUser `+0x588,+0x590,+0x598,+0x5A0,+0x5A8` are media-rights state sourced from radio/TV/European tuning values, not the five chairman operating budgets;
- DBRUser list triplets beginning at `+0x5B8,+0x5C4,+0x5D0` are support-staff containers (RTTI `CSupportStaff`), not budget state;
- `EAMchairbudgetsettings +0x58` is the displayed transfer-budget value;
- the authoritative persisted or derived source of that transfer-budget value remains unresolved.


## Contracts, transfers and finance — monthly maintenance categories

Confirmed additionally:

- monthly DBRUser routine `0x42AEB0` performs maintenance cash debits rather than chairman rebudgeting;
- accounting category 601 = stadium-size maintenance;
- accounting category 602 = major club-facility maintenance;
- accounting category 603 = pitch-system maintenance;
- DBRUser +0x65C owns/query-controls facility/building state used for School, Hotel, Hospital, Club, Training, Parking and Merchandising maintenance;
- DBRUser +0x6A8 stores pitch-system state used for sprinklers, drainage, pitch cover and heating maintenance.


## Match-engine feasibility

Confirmed additionally:

- high-level match processing at `0x513010` exposes a normal calculation route distinct from the `/skipmatchcalc777` result bypass;
- normal calculation reaches `0x632B20`, which runs `0x62AC90`, `0x62FBC0`, then `0x667E20`;
- MatchCalculator command classes, semantic FastView event classes, and MatchEngine 3D data loaders are separate architectural layers;
- the exact disc's match assets use deterministic, parseable formats rather than encryption/obfuscation;
- this supports a reconstruction strategy in which backend match simulation and semantic event generation are rebuilt before exact original-style 3D choreography.


## Match calculator core structure

Confirmed:

- `0x667E20` is a no-op in the analyzed build; normal calculation is initialized by `0x62AC90` and driven through `0x62FBC0 -> 0x62AE90`;
- the backend simulates normal play in discrete **five-minute segments** with explicit half-time, extra-time and penalty boundaries;
- the five-minute segment routine computes complementary team-strength aggregates through two routines that iterate participating players and **all 17 current skill slots**;
- those weighted aggregates feed the game's RNG and lower semantic event-generation routines;
- therefore the backend is a weighted probabilistic football-event calculator and is not dependent on continuous 3D physics for its outcomes.


## MatchCalculator event stream

Confirmed:

- MatchCalculator linked-event records carry a type code at +0x28;
- record types 6/7/8/9/10 map directly to FastView HalfTime/FullTime/ExtraTime/Penalties/Substitution senders;
- record types 0..4 are routed through FastView's EventGoal sender;
- during penalty-shootout state, type-1 goal-family records are presented as EventPenaltyShootoutShot;
- multiple type-0..4 producer paths directly increment the side-indexed score fields at +0xD4C/+0xD50 before appending the record;
- record type 5 remains an unresolved player incident/state family.

This confirms the calculator emits a structured semantic timeline that can be reconstructed independently of original 3D choreography.


## Match calculator — additional semantic structure

Confirmed:

- MatchCalculator type 5 is a three-subtype per-player incident/status record family; its exact card/injury labels remain unresolved;
- routine `0x62E2F0` performs AI substitution decisions and creates type-10 substitution records;
- routine `0x62E6F0` performs recurring player **Condition** decay; player `+0x77` is proven as Condition by its direct comparison with tuning key `ConditionInjuryInducingLevel`;
- these systems are separate from the goal-family record generation and five-minute team-strength calculation.


## Match discipline and injury semantics

Confirmed:

- MatchCalculator type-5 subtype 0 = **Booked / yellow card**;
- type-5 subtype 1 = **Sent Off / red card**;
- type-5 subtype 2 = **Injured**;
- player runtime `+0x77` = **Condition**;
- player runtime `+0x1B7` = 0..9 **Aggression** instruction/setting;
- disciplinary probability and escalation are aggression-sensitive;
- injury generation is condition-sensitive and is separate from the booking/dismissal generator;
- sent-off players are excluded by downstream lineup/AI state and the calculator limits further dismissal generation through a per-side counter.


## Match own-goal representation

Confirmed:

- goal-family record `+0x20` is the scoring-side inversion / own-goal flag;
- the credited scoring side equals the player's actual side when +0x20 is clear and is flipped when +0x20 is set;
- FastViewPanel routes same-side attribution to `EventPlayerGoal` and opposite-side attribution to `EventPlayerOwnGoal`;
- own-goal identity is therefore independent of MatchCalculator goal-family type 0..4.


## Match chance outcome encoding

Confirmed:

- MatchCalculator goal/chance record `+0x24 mod 3` encodes outcome:
  - 0 = goal
  - 1 = miss/failed chance
  - 2 = goalkeeper save/stop;
- record creators may add +3 as an alternate presentation variant without changing the base result;
- MatchController emits semantic `EventGoal` only for outcome values 0 or 3;
- chance/source type at +0x28 is independent of success/failure and independent of the own-goal flag at +0x20.


## Match source-type range

Confirmed:

- active MatchCalculator chance/source types in this release are 1, 2, 3, and 4;
- type 0 is accepted by FastView's compatibility switch but has no identified normal producer and is not reconstructed by MatchRecord serialization;
- type 0 is therefore treated as unused/reserved unless future evidence finds an active producer.


## Match Team Orders and penalty source type

Confirmed:

- Team Orders runtime priority category 0 = **captaincy order**;
- priority category 1 = **penalty-taker order**;
- MatchCalculator active chance source type 4 = **penalty kick**;
- the normal-match penalty resolver selects the designated penalty taker, resolves Shooting against the opposing goalkeeper/Goalkeeping, and records goal/miss/save through the common chance outcome field.


## Match chance-source taxonomy

Confirmed for the analyzed release:

- MatchCalculator source type 0 = unused/reserved;
- source type 1 = ordinary/open-play chance;
- source type 2 = free kick;
- source type 3 = corner;
- source type 4 = penalty kick.

Team Orders priority categories consumed by MatchCalculator:

- 0 captaincy;
- 1 penalty takers;
- 2 corner kicks;
- 3 free kicks.

The source type is independent of chance outcome at +0x24 and own-goal inversion at +0x20.


## Match possession / territory model

Confirmed:

- MatchCalculator raw segment counters at +0x1000/+0x1004/+0x1008 track side-0, neutral/contested, and side-1 possession/control states;
- those counters are normalized every five-minute segment;
- +0x106C stores side-0 possession percentage;
- +0x10CC stores neutral/contested percentage;
- side-1 percentage is reconstructed as the remainder to 100;
- +0x100C is a separate territorial/pitch-position metric;
- MatchController emits these through EventPossession;
- PossessionFigures displays the three possession percentages, while PossessionDiagram uses the territorial metric to select left/middle/right pitch presentation.


## Match chance context flag and possession payload

Confirmed:

- active chance-record `+0x2C` is serialized as exactly one bit and is now resolved as finish mode;
- `+0x2C = 0` means a headed finish and `+0x2C = 1` means a shooting/kicked finish;
- type-1/2/3 choose the bit from a weighted effective Heading-vs-Shooting roll, while penalties use shooting mode;
- `EventPossession` carries a separate territorial metric plus side-0 and neutral/contested possession percentages; side-1 percentage is reconstructed as the remainder to 100.


## Match penalty probability pipeline

Confirmed:

- MatchCalculator bounded RNG helper `0x64D5B0(N)` returns integer values in `0..N-1`;
- normal-match type-4 penalty attempts use player Condition, Shooting/Goalkeeping, positional-role compatibility and five-state Form modifiers;
- Form modifiers are exactly 0.90, 0.95, 1.00, 1.05 and 1.10 from Bad through Fantastic;
- the Shooting miss gate uses `RNG(256)` against `floor(effective_shooting/100)` on one branch selected by `RNG(3)`;
- the goalkeeper save gate uses `RNG(800)` against `floor(effective_goalkeeping/100)`;
- the goal branch includes `RNG(10) < 10-current_score` before incrementing the score.


## Match position compatibility and exact penalty resolver

Confirmed:

- the runtime role codes used by MatchCalculator are the original zero-based position codes;
- player +0x248 position state contains three compatible roles plus current assigned role;
- 0x4EA440 provides exact role-compatibility multipliers 1.00/0.90/0.85/0.80/0.75/0.70/0.50/0.10;
- the normal-match type-4 penalty resolver is now fully reconstructable including Condition, role compatibility, Form, miss/save thresholds, high-score suppression, and the chance creator's 10% presentation-variant roll.


## Match open-play resolution primitives

Confirmed:

- `0x62BD80` resolves attacker Heading vs defender Heading with weighted bounded RNG;
- `0x62C0D0` resolves attacker Control vs defender Tackling with the same weighted-duel model;
- `0x62BFC0`, `0x62C310`, and `0x62C420` are Heading, Shooting, and Set Piece execution gates using RNG(320), effective_skill/100, and a 50% fallback;
- `0x62C530` resolves goalkeeper Goalkeeping through RNG(256), followed by the same 10-current-score suppression gate used elsewhere;
- normal-time type-1 creator `0x62ECF0` suppresses plain MISS records 90% of the time and retains the +3 presentation-variant miss; at minute >=130 misses are retained without +3 variation.


## Match type-1 outer open-play flow

Confirmed:

- positional pools group attackers into RM/LM/CM, RW/LW/AM, and CF/ST; defenders into GK, right-back, left-back, centre-back, central-defensive-midfield, RM and LM groups;
- normal open play begins with a carrier from RM/LM/CM, falling back to RW/LW/AM;
- the first role-matched defender can end the move through a Control-vs-Tackling duel;
- the carrier must pass a Passing-only RNG(320) threshold;
- finishers are weighted roughly 50% CF/ST, 25% RW/LW/AM, 25% RM/LM/CM subject to availability;
- a closer defender is selected by finisher role before Heading/Shooting resolution;
- there is a direct 5% corner branch before ordinary open play;
- a failed final duel can branch into penalty/free kick/corner using RNG(4), RNG(100)<20, and RNG(2);
- scored open-play chances with a close defender have a RNG(20)==0 own-goal attribution branch.


## Match free-kick and corner resolvers

Confirmed:

- type-2 normal free kicks choose direct vs delivered from effective Shooting relative to floor(1.2 * (Shooting + Passing));
- cached set-piece state can force a direct free kick or force a delivered headed receiver;
- type-2 delivered free kicks and type-3 corners require Set Piece execution and reuse the common finishing primitives;
- type-3 corners require a receiver distinct from the corner taker;
- type-2/type-3 creators use the 10% +3 presentation variant and do not use own-goal inversion.


## Match five-minute attack-frequency driver

Confirmed:

- each five-minute segment derives one attack weight per side from opposing 0x62F140/0x62F3E0 team-strength ratios;
- side 0 is multiplied by 1.10 and side 1 by 0.90 before conversion;
- sequence_count = floor((W0 + W1) / 30);
- each sequence chooses side 0 when RNG(W0+W1) < W0, otherwise side 1;
- sequence event minute = segment_start + floor(5*i/N) + 1;
- each selected sequence calls the normal chance shell 0x62C740, followed by condition/injury and discipline updates.


## Match team-strength modifiers

Confirmed:

- match bias is reciprocal between attack and defence;
- human-controlled sides use the active captain's Confidence and Leadership;
- AI sides receive fixed strength boosts;
- aggression is a separate user-team multiplier;
- defence has a separate formation-coverage penalty.


## MatchCalculator team-strength and normal-time integration

**Confirmed**

The paired team-strength builders feeding the five-minute MatchCalculator scheduler are fully specified and now clean-room implemented:

- attack coefficients: executable VA `0x83B838`;
- defence coefficients: `0x83E2B8`;
- each table is exactly `4 x 20 x 17` doubles;
- one player/skill contribution is
  `(effective_skill / 255) * coefficient[tactic][role][skill] * (role_factor / 100)`;
- attack role factors for roles 0..12 are
  `105,108,110,120,112,115,97,95,102,92,90,117,100`;
- defence uses `200 - attack_factor` for those roles; roles 13..19 use 100 for both;
- live bias, captain/AI, aggression and defence formation-coverage multipliers are applied after the matrix sum.

The five-minute driver converts those strengths to side weights with the verified 1.10/0.90 asymmetry, runs `floor((W0+W1)/30)` sequences, selects the attacking side with `RNG(W0+W1)`, and places sequences within the five-minute window by `segment_start + floor(5*i/N) + 1`.

Exact-source validation against the canonical `footballmanager.exe` confirmed that the data-free PE coefficient loader returns two real `4 x 20 x 17` matrices from the analyzed executable.

The reconstruction now also has an evidence-backed normal-time orchestration layer that runs the 16 normal five-minute segments, routes open-play transitions into the recovered free-kick/corner/penalty resolvers, emits Half Time/Full Time boundaries, and can persist the final score of a due Premier League fixture into `PremierLeagueState`.

**Current implementation boundary (supersedes the earlier "not yet implemented" list)**

The clean-room normal-time orchestrator now also executes the recovered recurring match-state paths rather than only the scoring backbone:

- exact Condition workload decay and injury-incidence gates;
- immediate injury type-5 records and original type-10 replacement path when replacement is allowed;
- exact aggression-driven booking and dismissal generation;
- sending-off mutation/removal from later active pools;
- exact per-segment possession/territory normalization;
- exact `RNG(7)==0` automatic AI substitution trigger after discipline;
- original AI substitution timing, outgoing/incoming selection, Form-adjusted role comparison and type-10 event creation;
- active/substitute player-state mutation, including inheritance of assigned role `+0x03` and auxiliary `+0x04` while preserving the separate balance-position code `+0x05`.

The principal remaining backend match blocker is now **authoritative match-day initialization**: selecting the original starting XI and bench, assigning runtime roles and auxiliary position state, initializing Form/Condition and Team Orders, and reproducing the AI match setup that supplies those inputs. The simulator still accepts explicit prepared state rather than inventing those values.


## Team-strength balance-position field correction

**Confirmed; supersedes the earlier shorthand that the 105/108/... role-factor table is indexed by the current runtime role.**

The current assigned role and the small strength-balance code are separate fields in the player's position-state object:

- +0x03 through `0x4EA3C0`: current assigned role; selects positional compatibility and the 4 x 20 x 17 matrix role.
- +0x05 through `0x4EA3E0`: separate low-five-bit balance-position code; selects the small `0x840D38` factor table for codes 0..12, otherwise neutral 100%.

Attack uses `[105,108,110,120,112,115,97,95,102,92,90,117,100]` for +0x05 codes 0..12. Defence uses 200 minus the corresponding value. The semantic label of +0x05 remains unresolved, so reconstruction exposes it neutrally as `balance_position_code`.
## AI substitution and injury replacement

**Confirmed**

Normal five-minute sequence processing continues beyond chance/Condition/discipline with a separate `RNG(7)` draw. On zero, `0x62E2F0` is called for the side opposite the scheduler-selected attacker.

For AI-controlled teams the automatic substitution path:

- begins at minute 60 when the original starting XI is intact;
- moves to minute 70 after one original starter is no longer active, then minute 80 after two;
- is suppressed while that AI side is leading;
- scans original XI slots in reverse order;
- considers outgoing current roles 8..19;
- obtains the best substitute for the outgoing role through `0x409950`;
- rejects the pair if that selected substitute's pre-substitution current role is below 8;
- compares outgoing and incoming role ratings after the five-state Form multiplier and chooses the strictly smallest truncated outgoing-minus-incoming difference.

The exact player role-rating helper `0x41C7E0` is implemented in `reconstruction/match_role_rating.py`. It converts selected raw skills to the 0..30 display scale, applies the role-specific seven-skill weight vector, applies `0x4EA440` position compatibility, caps at 99, adds 0.49 and truncates toward zero. Runtime roles 16 and 17 use the executable's zero branch.

Successful substitutions use `0x409AC0`: the incoming player inherits the outgoing assigned role (`+0x03`) and auxiliary low-nibble field (`+0x04`), but **not** the distinct strength/discipline balance-position field (`+0x05`). The outgoing player is removed from active/substitute state and its position state is reset. Type-10 records carry side, outgoing side-local index and incoming side-local index.

A successful injury uses the same `0x409950 -> 0x409AC0 -> 0x62EF90` replacement path immediately after the type-5 Injury record. AI-controlled teams permit this automatic injury replacement. User-controlled teams permit it only when the still-generically-named MatchCalculator `+0xD3C` mode code is 1 or 3. If no replacement occurs, the injury routine itself does **not** automatically remove the injured player from the field.

The Condition loop checks active state dynamically for each match participant as it reaches that roster slot. Consequently a bench player activated by an injury substitution can be processed later in the same Condition pass if its participant slot occurs later in iteration order.
## Match participant construction and runtime selection flags

**Confirmed**

The MatchCalculator participant arrays are populated from each team's ordered runtime roster after lineup selection has already marked player state.

- team roster IDs begin at team object `+0x244`, with count at `+0x294`;
- collector `0x510CD0` resolves each ID to its 592-byte runtime `DBRPlayer`;
- a player is included when either the active predicate `0x417F50` or substitute predicate `0x417F60` succeeds;
- included players retain team-roster iteration order.

For the player's current club, those predicates map to `DBRPlayer+0x14`:

- bit 4 / `0x10` = starting/on-field active;
- bit 5 / `0x20` = match substitute available.

Setter `0x4182F0` sets active and clears substitute state. Setter `0x4182C0` sets substitute state and clears active. Removal helper `0x4181B0` clears both and resets position state.

The AI lineup routine `0x409C90` runs before participant collection for non-user-controlled teams. Therefore automatic match preparation can be reconstructed as lineup-state assignment followed by the exact ordered participant filter, rather than inventing a separate match-only roster.
## Exact DBRPlayer match-state initialization defaults

**Confirmed**

Runtime player initialization now supplies three formerly caller-supplied match inputs exactly:

- Condition byte `DBRPlayer+0x77` initializes to **80**;
- Form byte `DBRPlayer+0x192` initializes to neutral state **2**;
- the position-state constructor copies preferred role 0 into assigned role `+0x03`, clears the low nibble of `+0x04`, and forces the low five bits of `+0x05` to **10**.

The last value is the same separate `balance_position_code` already proven to index the small team-strength balance table and participate in discipline candidate selection. Its higher-level semantic label remains unresolved, but its initialization no longer is.
## AI lineup base availability flags

**Confirmed**

The first three low bits of `DBRPlayer+0x14` are all exclusion inputs to the competitive lineup availability helper `0x418050`.

- bit 0 = **injured**;
- bit 1 = **banned/suspended**;
- bit 2 = **separate selection-exclusion state**, exact semantic label unresolved.

The simpler helper `0x418130` tests only bits 0 and 1, confirming injury/suspension as the common global unavailability pair. Bit 2 is managed by a separate club roster-selection path and should not be mislabeled as cup-tied; a distinct `CCupTiedPlayer` persistence class and competition lookup path exist in the executable.
## Cup-tied player persistence

**Confirmed**

FM2001 stores cup-tie state separately from the transient DBRPlayer exclusion bits.

A `CCupTiedPlayer` record stores:

- player ID;
- the club/team ID for which that player is tied.

Lookup `0x4E9710(collection, player_id, team_id)` returns cup-tied only when a record exists for that player and the stored club differs from the team attempting to field him. Competition helper `0x4F8E40` invokes this lookup through the competition/context cup-tied collection.

Therefore `DBRPlayer+0x14 bit 2` is not a cup-tied bit and must remain a separately named selection-exclusion state.
## Non-EU player restriction in AI team selection

**Confirmed**

`DBRPlayer+0x14 bit 11` is the game's **Non-EU** state. The persistent collection consulted by `0x41B4D0` creates records whose vtable RTTI is `CNonEUPlayer`, matching the embedded `NonEUPlayer.cpp` source identity.

The corresponding competition limit is `DBRCompetition+0x2B`, packed Static.dat competition byte **+34**. `0x407DF0` returns that value for the current competition or defaults to 11 without competition context. The shipped Premier League value is **3**.

Competitive selector `0x409C90` rejects a Non-EU candidate after the running restricted count reaches that maximum. If an AI-controlled team cannot complete the XI while restriction counting is enabled, the routine retries the whole XI selection exactly once with the restriction-enforcement flag cleared. User-controlled teams do not receive that automatic relaxation.


## 25 September current implementation boundary

**Supersedes older FINDINGS sections that call match-day initialization the principal MatchCalculator blocker.**

The autonomous Premier League path now includes AI strategy/formation choice, exact AI lineup core, substitutes, runtime position/selection state, ordered participant collection, match environment generation, normal-time MatchCalculator simulation, incident persistence, post-match Form/Condition, Pitch Wear, persistent injuries and league-result storage.

The main match/season fidelity boundary is now global state ordering rather than missing basic AI preparation: the reconstruction has an exact MSVC CRT RNG primitive and exact schedule shuffle mechanics, but new-game RuntimePlayer peak-age initialization still consumes Python random.Random rather than the shared FM2001 CRT stream. Exact same-day fixture order also remains an explicit deterministic fallback until the original RNG state entering the Premier League bucket shuffle is reproduced.

Premier League fixed-fixture scheduling is additionally constrained as follows:

- real fixtures preserve Static.dat source order within each round;
- the fixed League builder consumes no RNG before schedule insertion;
- schedule insertion is head insertion;
- per-bucket shuffle is descending Fisher-Yates;
- competition 0 uses schedule container 0x947AD8 (mode 0);
- the RNG-heavy 0x4FA790 branch belongs to the other mode-1 container and cannot run before the Premier League container is finalized.

League-table equal-points ordering after points / goal difference / goals scored remains unresolved; reconstruction intentionally uses club ID only as a deterministic fallback.

## DBRPlayer startup RNG ordering

Confirmed:

- every runtime player constructor consumes RNG(15) and initializes +0x18E from maximummorale minus that roll; shipped maximummorale is 100;
- DBTPlayers constructs the complete player array before loading records, so all constructor RNG(15) draws happen first;
- each loaded player then consumes peak RNG(1), RNG(2), RNG(2), followed by RNG(5);
- the RNG(5) result becomes a 12/24/36/48/60 month byte at +0xC0 and is used to derive +0x154;
- the Non-EU startup branch adds no random draw;
- GameState.from_database now uses MsvcCrtRng for this recovered startup block and retains the same RNG object for subsequent autonomous match simulation unless a caller explicitly supplies a different scripted RNG.

This resolves the Python-Random mismatch identified by the 25 September audit for the currently mapped player-startup block. Exact RNG state at the first Premier League schedule shuffle still depends on other startup RNG consumers not yet audited.

## Mode-0 procedural competition RNG before PL shuffle

Confirmed:

- 0x411020 dispatches competition initializers for a requested schedule-container mode and walks its competition pointer array in reverse index order;
- generic procedural League builder 0x6170F0 has a bounded-RNG shuffle, but only when the League has a parent and the parent virtual +0x18 predicate is true;
- League/ScotPremierLeague parents return false for +0x18; Cup/DummyLeague parents return true;
- root leagues therefore skip this specific random shuffle;
- mode-0 child League IDs 14, 167 and 192 have Cup parents and are currently proven candidates for this pre-bucket RNG consumer;
- 0x6178B0 copies the relevant parent Cup vector at +0x54/+0x58 before the shuffle;
- exact vector counts/order for those child phases remain unresolved;
- 0x40B380 itself is RNG-clean; the rand() seen at adjacent 0x40B390 belongs to another function.

## Mode-0 Cup and team-setup RNG corrections

Confirmed:

- Cup's eight-dword +0x54 allocation branch is selector-true/mode-1 only; Champions League/WCC mode-0 initialization skips it;
- a root mode-0 Cup with an empty +0x54 vector later initializes one slot at +0x54/+0x58;
- Cup+0x34 derives from packed competition dword +27: 123 -> 1, 116 -> 2, otherwise 0;
- Champions League ID 9 (+27=123) uses the 0x40C6C0 selection route, which consumes at most one RNG(count-1) draw via 0x5EE6C0 when its candidate vector has >1 entries;
- WCC ID 101 (+27=116) has a special branch whose RNG use depends on Cup+0x40 and remains unresolved;
- 0x4F6360 is RNG-clean; the earlier apparent RNG call belonged to the next function;
- new-game 0x616620 passes argument 1 to 0x404110, so 0x404110 skips its 0x41ACA0 RNG-using morale path before 0x615BE0.

## Competition registration / initialization order

Confirmed:

- packed competition dword +27 is the country/region index used by 0x4F8FF0;
- country+0x40/+0x44 stores root (parentless) competition pointers only;
- roots are appended in global competition source/ID order, then qsorted by runtime competition +0x18;
- runtime +0x18 is the negated signed packed word +15;
- 0x411020 walks the sorted root array in reverse, yielding effective ascending packed +15 initialization order;
- countries are processed in global country-table order;
- child competitions are recursively attached to parent object+0x08/+0x0C in global competition-table ID order and do not appear independently in country+0x40;
- equal packed +15 keys compare equal and retain unresolved qsort relative order.

## Competition runtime metadata and class-specific RNG eliminations

Confirmed clean-room parser fields now include runtime class code, parent
competition, root initialization-order value, country/region ID, and schedule
container code.

For pre-Premier-League-shuffle RNG accounting:

- shipped primary DummyLeague roots: 118;
- primary DummyLeague roots have no children in the shipped competition tree;
- DummyLeague virtual initializer 0x4F5130 and recursive base initializer
  0x4F3DE0 contain no RNG call, eliminating those 118 roots as direct RNG
  consumers;
- Scottish Premiership ID 27 is a root with no children;
- ScotPremierLeague::Initialize 0x4FAC60 has no direct bounded RNG call;
- its generic procedural-League RNG block at 0x617277 is skipped for this root
  because the block requires a non-null parent.

Nested generic League helpers are still being audited before declaring the
entire Scottish/root-League path transitively RNG-clean.
