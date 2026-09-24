# Match Engine and FastView Reverse Engineering

## Purpose

This document tracks the uncertain match-calculation, FastView and 3D-presentation side of FM2001 separately from the management-system reverse engineering.

All findings below refer to the exact analyzed release identified in `research/FINDINGS.md`.

## High-level architecture

Executable source-path strings and RTTI establish several distinct layers rather than one monolithic match engine:

1. **Football Manager match orchestration**
   - `Applications\\FootballManager\\MatchFrontEnd.cpp`
   - high-level routine around `0x513010`

2. **MatchCalculator / match record and commands**
   - `Libraries\\MatchCalculator\\MatchRecord.cpp`
   - command classes include `TacticsCommand`, `PlayerCommand`, `AggressionCommand`, `DefensiveStyleCommand`, `FormationCommand`, `OrdersCommand`, `PositionCommand`, `StrategyCommand`, `StyleCommand`, and `SubstitutionCommand`.

3. **Semantic event stream / FastView**
   - `Applications\\FootballManager\\FastView\\MatchController.cpp`
   - `FastViewPanel.cpp`
   - `PossessionFigures.cpp`
   - `ScoreComposite.cpp`
   - event sender/receiver classes exist for goals, own goals, possession, score, substitutions, half/full time, extra time, penalties, penalty-shootout shots, player form and player energy.

4. **3D MatchEngine / animation and scenario assets**
   - `Libraries\\MatchEngine\\MatchEngine.cpp`
   - backend renderer/game source paths
   - external scenario, sequence, animation and formation/tactical tables under `DataInGame`.

This separation is a major feasibility advantage: backend match behavior can be studied and reconstructed independently from exact 3D choreography.

## High-level match-calculation dispatch

Routine `0x513010` is a high-level match-processing path.

Verified behavior:

- it constructs a large temporary match-record/state object through `0x62ABD0`;
- if a virtual precondition at match object vtable +0x34 fails, it falls back to compact result routine `0x512D80`;
- developer switch `/skipmatchcalc777` is read through `0x516080`; when set, the routine calls `0x512D80` instead of the normal calculation path;
- the normal path calls `0x632B20` or wrapper `0x632B50` depending runtime mode/state;
- `0x632B50` only clears byte `match_record +0x1145` and then calls `0x632B20`;
- `0x632B20` stores the match-record pointer globally at `0x981C78`, then calls:
  - `0x62AC90` — initialization/reset of match-record scores/player-side state;
  - `0x62FBC0` — drives the actual simulation;
  - `0x667E20` — **a no-op (`ret`) in this build**, not a third calculation stage.
- `0x62FBC0` repeatedly calls `0x62AE90` while it reports more work, then finalizes linked match-event state through `0x62F7C0`;
- after calculation, the high-level routine writes/propagates the calculated state through match-object virtual methods.

This gives a compact, identifiable entry point for deeper backend reconstruction.

## MatchEngine data assets loaded by the executable

The executable contains explicit paths for:

- `DataInGame\\sctable.sti`
- `DataInGame\\aiseqs.tbi`
- `DataInGame\\moai.viv`
- `DataInGame\\gen4tbls.t`
- `DataInGame\\FC.bin`
- `DataInGame\\FCDBP.dbi`
- `DataInGame\\FCDBT.dbi`
- `DataInGame\\FCDB.dbi`

Initialization around `0x6CB050` loads `GEN4TBLS.T`, `MOAI.VIV` and `AISEQS.TBI` through the same generic data loader, then passes the resulting objects into the MatchEngine initialization path around `0x6D8850`.

A separate initialization route loads the FC/FCDB files.

The small file `AIDATA.VER` identifies its AI-data version as `AIDATAV1-2-12`.

## BIGF archives

`AISCRIPT.VIV`, `MOAI.VIV`, and `GEN4TBLS.T` all use EA's structured `BIGF` archive format.

Confirmed header/directory structure:

- +0x00: ASCII `BIGF`
- +0x04: big-endian archive-size field
- +0x08: big-endian file count
- +0x0C: big-endian directory/header end
- each directory entry:
  - big-endian uint32 data offset
  - big-endian uint32 data size
  - NUL-terminated filename

Counts in this release:

- `AISCRIPT.VIV`: **140 entries**
  - one embedded `sctable.sti`
  - **139 archived .SCI files**
- `MOAI.VIV`: **584 entries**
- `GEN4TBLS.T`: **7 entries**

`GEN4TBLS.T` contains:

- `g99hd`
- `g99ko.fmt`
- `g99pl.fmt`
- `g99pk.fmt`
- `g99fk.fmt`
- `g99at.fmt`
- `g99df.fmt`

The filenames look formation/tactical in nature, but exact field semantics are not yet assigned.

## Loose SCI files and SCTABLE.STI

The extracted disc contains exactly **235 loose .SCI files** under `DATAING`.

This supersedes the earlier rough estimate of approximately 252.

The loose `SCTABLE.STI` is **6,580 bytes** and begins with little-endian uint32 count **137**.

The file is exactly:

`4 + 137 * 48 = 6580 bytes`.

Runtime loader `0x70F000` independently proves that each entry is **0x30 / 48 bytes** by copying `count * 12 dwords` into the engine's scenario table.

Confirmed 48-byte record layout:

- +0x00: `char sci_name[16]`
- +0x10: uint32 condition/mask field 1
- +0x14: uint32 condition/mask field 2
- +0x18: uint32 condition/mask field 3
- +0x1C: uint32 condition/mask field 4
- +0x20: `char viv_name[16]`

All 137 loose SCTABLE SCI references exist among the loose SCI files.

There are **98 additional loose SCI files** that are not directly listed by the loose SCTABLE.

### Selector behavior

Runtime selector `0x70F050` loops the table and filters candidate records using the third and fourth mask fields.

Routine `0x70F0C0` evaluates all four condition fields and contains a special comparison against VIV name `CORE`.

Exact semantic names for the four mask fields remain unresolved, but they are active scenario-selection conditions rather than unused metadata.

## Embedded AISCRIPT scenario table

The `AISCRIPT.VIV` archive contains an embedded `sctable.sti`:

- count: **139**
- record size: **48 bytes**
- archived SCI entries: **139**
- all 139 embedded table references correspond one-for-one to archived SCI entries.

Compared with the loose runtime table:

Embedded-table-only names:
- `bintro.sci`
- `refnoc0.sci`
- `refyclo0.sci`

Loose-table-only name:
- `emwncup1.sci`

The executable has an explicit literal path and direct loader for the loose `DataInGame\\sctable.sti`. No equivalent explicit `AISCRIPT.VIV` literal path has yet been found, so the loose table is the stronger confirmed runtime scenario-table source for this release. Do not yet claim the archive is completely unused because generic VIV/archive loaders exist.

## SCI structure: current evidence

SCI files are small structured binaries, roughly **1.2–9.7 KB** in this release, and contain repeated readable animation/action identifiers.

They are not encrypted or high-entropy opaque blobs.

Examples contain fixed-width-looking names that overlap heavily with `MOAI.VIV` animation identifiers.

Across all 235 loose SCI files, hundreds of distinct short identifiers can be extracted, and a large majority of the animation-like identifiers have exact name matches in `MOAI.VIV`.

The exact SCI instruction/record layout remains unresolved. A recurring 16-bit value 0x16 appears in headers, but its meaning is not yet proven and should not be labeled as a player/actor count without further evidence.

## AISEQS.TBI and AITMPS.TBI

Both files are exactly **23,088 bytes** and share the same high-level geometry.

Header:

- +0x00: little-endian uint32 primary record count = **452**
- +0x04: little-endian uint32 secondary-table offset = **0x2358 / 9048**

Primary table:

- starts at +0x08
- **452 records**
- **20 bytes per record**

Secondary table:

- starts at 0x2358
- **585 entries**
- **24 bytes per entry**

For `AISEQS.TBI`, the dword at primary-record +0x08 acts as an absolute file offset into the 24-byte secondary-entry table in the inspected records.

Of the 585 secondary AISEQS entries:

- one is blank;
- the other **584 names match all 584 MOAI.VIV entry names**.

This is a strong direct bridge between AI sequence selection and the motion/animation archive.

`AITMPS.TBI` has the same 452/20-byte + 585/24-byte structure, but secondary entries contain additional metadata beyond the short name in many records. Exact field semantics remain to be mapped.

## CAMERA.SCR

`CAMERA.SCR` is readable text rather than a binary format.

It defines camera configurations for:

- multiple in-play camera modes;
- throw-ins;
- corners;
- free kicks;
- goal kicks;
- penalties;
- replay modes;
- manual replay;
- out-of-play;
- half time.

This is another indication that presentation behavior is partly externalized into data rather than hard-coded.

## Feasibility assessment

### Backend match reconstruction

**Current assessment: feasible.**

Reasons:

- there is a clean high-level calculation entry point;
- a developer switch can bypass the normal calculator, making the normal route structurally visible;
- MatchCalculator exposes named command classes for tactics and substitutions;
- result calculation is followed by a semantic event/presentation layer rather than being inseparably embedded in 3D rendering;
- substantial engine behavior is table/data driven.

The actual probability/decision mathematics are still largely unmapped, so this is a feasibility judgment, not a claim that the backend is nearly complete.

### FastView / semantic presentation

**Current assessment: feasible and probably easier than exact 3D parity.**

FastView consumes explicit semantic events. A reconstructed calculator can therefore produce the same classes of events even before original 3D scenario playback is fully decoded.

### Exact original-style 3D choreography

**Current assessment: feasible in principle, but higher effort.**

Positive evidence:

- SCI files are structured and readable enough to correlate with animation identifiers;
- SCTABLE is completely structurally decoded;
- AISEQS/AITMPS have fixed record geometry;
- AISEQS maps directly to all MOAI animation names;
- BIGF archives are straightforward to parse;
- camera behavior is plaintext.

Remaining hard work:

- decode SCI instruction/record semantics;
- decode MOAI payload semantics sufficiently to play or convert motions;
- map the four SCTABLE mask meanings;
- understand how scenario selection is synchronized with semantic match events.

### Recommended reconstruction order

1. Map `MatchRecord` and the `0x62AC90 -> 0x62FBC0 -> 0x667E20` backend calculation stages.
2. Recover semantic match-event generation and match statistics.
3. Implement a non-3D clean-room calculator and event timeline first.
4. Implement FastView/event-driven match presentation.
5. Decode SCI/MOAI choreography and original-style 3D as a separate later layer.

This order reduces project risk: exact 3D reconstruction is no longer a prerequisite for recreating the core match simulation.


## Core calculator timeline and strength model

Deeper disassembly of the normal calculator substantially reduces the remaining uncertainty.

### 0x62AC90 initializes the match record

`0x62AC90`:

- clears home/away score-like fields at `+0xD4C/+0xD50`;
- clears several additional aggregate fields;
- initializes per-player match state for both sides;
- processes the first 11 players differently from substitutes/reserves;
- carries player runtime state into 0x4C-byte per-player match records.

This is initialization, not the main simulation loop.

### 0x62FBC0 drives 0x62AE90

`0x62FBC0` calls `0x62AE90` and repeats it while the return value is nonzero. It then finalizes/reorders linked event state and updates a list rooted around match record `+0xB60`.

The main match simulation therefore lives primarily in the `0x62AE90` family and its callees.

### Five-minute simulation cadence

The normal-time path in `0x62AE90` is explicit.

It begins with minute value 5 and invokes segment routine `0x62B1A0` in five-minute increments:

- 5, 10, 15, 20, 25, 30, 35, 40;
- boundary record at 45;
- 50, 55, 60, 65, 70, 75, 80, 85.

If extra time is required, the same routine later processes:

- 95, 100;
- boundary at 105;
- 110, 115.

If a penalty shootout is required, `0x631730` creates the penalty-phase record at minute **90** when extra time is not used, or **120** when extra time has been played.

Thus the backend is a discrete five-minute probabilistic simulation, not a continuous 3D-physics simulation.

### Boundary/event record type codes

Plain match-record constructors around `0x6325E0` assign numeric type codes.

Observed usage:

- constructor `0x632640` sets type **6** and is emitted at minute 45;
- constructor `0x632660` sets type **7** and is used in the final match-completion path;
- constructor `0x632690` sets type **8** and is used at extra-time transition/boundary points;
- constructor `0x6326C0` sets type **9** and is called by the penalty-shootout path at minute 90 or 120.

These structurally correspond to the known HalfTime / FullTime / ExtraTime / Penalties semantic-event family. Exact class/type names should still be tied to their serializers/consumers before treating the numeric enum names as final.

### Team-strength aggregate routines

Segment routine `0x62B1A0` calls symmetric floating-point routines `0x62F140` and `0x62F3E0`.

Both:

- iterate the participating player list;
- skip ineligible/unavailable records through player/status checks;
- loop **17 times** per player, matching the complete 17-skill model;
- read current player skill bytes from runtime `player +0x1E + skill_slot`;
- incorporate additional player runtime/status values and positional/context state;
- multiply contributions by large role/context weight tables at approximately `0x83B838` and `0x83E2B8`;
- apply team/manager/tactical/context multipliers before returning a floating aggregate.

The two functions use different weight tables/context bytes, strongly indicating complementary team-strength dimensions rather than duplicate calculations. Exact names such as attack/defence should not yet be assigned.

### Segment event generation

`0x62B1A0`:

1. obtains the two sets of team-strength aggregates;
2. derives relative integer thresholds/counts from their ratios;
3. uses the game's RNG at `0x64D5B0`;
4. repeatedly selects a side/outcome within the five-minute segment;
5. dispatches into event-generation routines including `0x62C740`, `0x62E130`, `0x62E2F0`, and `0x62E6F0`;
6. stores three per-segment aggregate/stat values into arrays beginning around `match_record +0x100C/+0x106C/+0x10CC`.

`0x62C740` itself performs further player selection/status/skill calculations and increments the segment aggregate counters before descending into event-specific logic.

This is strong evidence that the core backend is a weighted probabilistic event simulator driven by player attributes/tactics, rather than being dependent on 3D animation physics.

## Revised match feasibility

The biggest technical risk has shifted.

Earlier uncertainty was whether the match system might be an opaque, inseparable 3D engine. The current evidence disproves that concern.

The remaining difficult task is now **semantic recovery**:

- name the complementary strength dimensions and their weight tables;
- map event-generation branches to shots, goals, fouls, cards, injuries, possession and other statistics;
- recover substitution/tactical-command effects during the timeline;
- validate random distributions against the original.

Those are substantial but conventional reverse-engineering tasks with clear entry points.


## Calculator event types mapped to FastView senders

The Football Manager match-controller processing routine around `0x519862..0x519DA1` switches directly on each MatchCalculator linked record's type field at **record +0x28**.

The controller constructor `0x518C80` independently maps its sender members by RTTI:

- controller +0x10 = `Sender<EventGoal>`
- controller +0x20 = `Sender<EventPossession>`
- controller +0x30 = `Sender<EventPenaltyShootoutShot>`
- controller +0x40 = `Sender<EventHalfTime>`
- controller +0x50 = `Sender<EventFullTime>`
- controller +0x60 = `Sender<EventExtraTime>`
- controller +0x70 = `Sender<EventPenalties>`
- controller +0x80 = `Sender<EventSub>`

The MatchCalculator type switch can therefore be mapped directly:

- **types 0..4** -> common goal-family processing through `Sender<EventGoal>`
- **type 5** -> separate player-state/incident handling; exact semantic label remains unresolved
- **type 6** -> `EventHalfTime`
- **type 7** -> `EventFullTime`
- **type 8** -> `EventExtraTime`
- **type 9** -> `EventPenalties`
- **type 10** -> `EventSub`

The type-7 path is handled immediately before the jump table: when record +0x28 == 7, the controller iterates the sender at +0x50, proving FullTime directly.

### Penalty-shootout reuse of type-1 goal records

When the controller is in its penalty-shootout state, a **type-1** goal-family record is diverted into the sender at controller +0x30 instead of the normal EventGoal sender.

RTTI proves +0x30 is `Sender<EventPenaltyShootoutShot>`.

Thus penalty-shootout kicks reuse part of the ordinary goal-family MatchCalculator record model, with the controller's current match phase selecting the semantic presentation event.

### Types 0..4 are a goal-event family

The common handler for types 0..4 constructs the event payload and iterates `Sender<EventGoal>`.

Lower calculator code independently shows score increments immediately before several creators in this family:

- score fields are the side-indexed pair at match record `+0xD4C/+0xD50`;
- branches around `0x62CAD3`, `0x62CC9A`, `0x62D0D0`, `0x62D40D`, `0x62D50E`, `0x62D914`, `0x62DC62`, and `0x62DD62` increment one of those score fields and then append one of the type-0..4 record variants.

Known record creators include:

- `0x62ECF0` -> goal-family record with type supplied through its arguments; observed callers commonly create type 1;
- `0x62EE20` -> type 2;
- `0x62EEA0` -> type 4;
- `0x62EFD0` -> manually appends the same 0x38-byte linked-record shape with caller-supplied subtype fields.

Exact labels for types 0/1/2/3/4 (for example ordinary goal vs own goal vs set-piece source) remain to be recovered from their payload fields and player-goal/own-goal consumers. They should not yet be named more specifically than **goal-family records**.

### Significance

The bridge from MatchCalculator records into semantic FastView events is now directly visible. Reconstructing the backend does not require guessing how its timeline is interpreted: the executable exposes a compact typed record stream whose major timeline/substitution/goal families are mapped to named event senders.


## Type-5 player-incident records and per-segment player-state updates

Further tracing separates three previously unresolved branches in the five-minute simulator.

### Type 5 is a three-subtype per-player incident/status record

MatchController type-5 handling is at `0x519B89`. Unlike types 0..4, it does not emit through `Sender<EventGoal>`.

Its payload selects one of three small setters:

- `0x6C28F0`
- `0x6C2910`
- `0x6C2930`

These write one of three adjacent bytes in a global per-side/per-player matrix beginning at approximately `0xA14828`.

The indexing is structurally:

`3 * (player_index + 18 * side) + subtype_byte`

so each player has three independent incident/status flags.

The exact football labels of the three bytes are not yet proven and must not yet be called yellow/red/injury by name.

Record creator `0x62EF20` constructs type-5 records. Two confirmed creation forms from `0x62E130` are:

- subtype path A: record `+0x18 = 1`, causing FastView/controller code to call `0x6C28F0`;
- subtype path B: record `+0x18 = 0`, record `+0x1C = 1`, causing `0x6C2910`.

Subtype B also marks per-player match-state byte `+0x49`, increments a side counter, and calls player routine `0x4181B0`, so it has a stronger/removal-like effect than subtype A.

A third encoding uses record `+0x20 != 0` and routes to `0x6C2930`.

### 0x62E2F0 is AI substitution logic

Routine `0x62E2F0` is now structurally resolved as computer-manager substitution logic.

Confirmed behavior:

- returns/avoids the decision path for a human-controlled club through `0x4037B0`;
- checks match minute and score context;
- evaluates current players and substitute candidates;
- compares player metrics/availability;
- selects a replacement;
- calls `0x62EF90`, the confirmed **type-10 substitution-record creator**;
- updates per-player match-state bytes after the substitution.

Thus this routine is not a generic match-event generator; it is the automatic substitution decision path.

### 0x62E6F0 is recurring player Condition decay

Routine `0x62E6F0` runs repeatedly during the match and iterates players on both sides.

Helper `0x62E6C0` derives a player-specific probability threshold from player/runtime state. When the RNG condition succeeds:

- player byte `+0x77` is checked to be greater than 1;
- it is decremented by one;
- `0x62EAE0(player, time/segment)` is called to propagate the update.

This is conclusively a recurring decrement of player **Condition**. The identification is now exact: tuning loader `0x5039A6..0x5039DC` maps literal key `ConditionInjuryInducingLevel` to global `0x821814`, and the injury path compares player `+0x77` directly against that value. The following tuning key `ConditionInjuryRandomiser` maps to `0x821818`. `0x62EAE0` is therefore an injury check run after Condition changes, not an energy-event notifier.

### Significance

The five-minute simulation now separates into clearer responsibilities:

- weighted team/event probability generation;
- per-player incident/status generation (type 5);
- AI substitution decisions (type 10);
- recurring player condition/energy-like decay.

This further reduces the backend reconstruction problem to finite, independently traceable systems.


## Type-5 incident subtypes resolved: booked / sent off / injured

The three type-5 per-player status bytes are now semantically resolved.

### Status-byte order

The global per-side/per-player matrix beginning at approximately `0xA14828` stores three bytes per player:

1. byte 0 -> **Booked**
2. byte 1 -> **Sent Off**
3. byte 2 -> **Injured**

The executable contains the corresponding FastView/tactics art assets:

- `reused_Art\FastView\Tactics_Booked.444`
- `reused_Art\FastView\Tactics_SentOff.444`
- `reused_Art\FastView\Tactics_Injured.444`

The semantics are independently proven by the MatchCalculator creation paths rather than assigned from the filenames alone.

### Booking / yellow-card path

Disciplinary routine `0x62E130` uses player runtime `+0x1B7` as a 0..9 user-adjustable aggression value.

For a selected player whose per-match byte `+0x48` is still clear, one branch creates a type-5 record through `0x62EF20` with:

- record `+0x20 = 0`
- record `+0x18 = 1`

The MatchController then calls `0x6C28F0`, setting status-matrix byte 0.

The generator sets player-match byte `+0x48 = 1`, so a later disciplinary event knows that the player has already been booked.

Thus type-5 subtype/flag 0 is **Booked / yellow card**.

### Sending-off / red-card path

A later branch in the same aggression-sensitive routine can create:

- record `+0x20 = 0`
- record `+0x18 = 0`
- record `+0x1C = 1`

The MatchController routes this to `0x6C2910`, setting status-matrix byte 1.

The calculator additionally:

- sets per-player match byte `+0x49 = 1`;
- increments a per-side count at match record `+0xD74 + side*4`;
- restricts the branch so the side count remains below four before another dismissal is generated;
- calls player routine `0x4181B0`, removing/resetting the player from active selection state.

Lineup/AI routines that copy the three-byte status matrix specifically test the **second byte** to exclude the affected player from active on-field selection.

Thus subtype/flag 1 is **Sent Off / red card**.

The logic also supports a direct-red-style branch: an unbooked high-aggression player can bypass the booking branch and proceed to the dismissal probability test.

### Injury path

The third type-5 encoding is created by `0x62EAE0`, a separate condition-driven injury routine.

It is reached after recurring Condition decay and computes injury probability from:

- match/context state;
- player status;
- player **Condition at +0x77**;
- tuning global `0x821814 = ConditionInjuryInducingLevel`.

When an injury is generated, `0x62EF20` is called with the form that produces:

- record `+0x20 = 1`

The MatchController routes this to `0x6C2930`, setting status-matrix byte 2.

The same injury path then attempts replacement/substitution where permitted, including creation of a type-10 substitution record.

Thus subtype/flag 2 is **Injured**.

### Player +0x1B7 = Aggression

Player runtime byte `+0x1B7` is initialized to 5 and exposed through UI increment/decrement controls clamped to 0..9.

The MatchCalculator RTTI contains a named `AggressionCommand` class, and disciplinary routine `0x62E130` uses `+0x1B7` repeatedly to control both the overall disciplinary-event probability and escalation from booking to dismissal.

This establishes `player +0x1B7` as the player's **Aggression instruction/setting**.

### Reconstruction consequence

Type-5 can now be reconstructed with explicit semantics:

- booked/yellow card;
- sent off/red card;
- injury.

The match engine therefore has a compact, recoverable discipline/injury state model rather than an opaque incident system.
