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
