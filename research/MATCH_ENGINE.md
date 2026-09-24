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


## Own-goal encoding resolved: goal-family +0x20 is the side-inversion flag

The scoring record model can now distinguish an ordinary credited goal from an own goal without assigning own-goal semantics to any one record type 0..4.

### Calculator player mapping

Helper `0x62F0C0` maps a player pointer into:

- side index (0 or 1);
- player index within that side.

Goal-family record builders use it to populate the player-side/index fields.

### MatchController derives the credited scoring side

For goal-family records at `0x51994A..0x519962`, MatchController reads:

- record `+0x04` = the recorded player's actual side;
- record `+0x08` = that player's index;
- record `+0x20` = side-inversion flag.

The credited scoring side is calculated as:

```
credited_side = record+0x20 ? !record+0x04 : record+0x04
```

That side and player index are resolved into the semantic EventGoal payload.

### FastViewPanel distinguishes ordinary goals from own goals

`FastViewPanel` derives from/contains the semantic EventGoal receiver at subobject +0x7C. Its EventGoal callback is **`0x522690`**.

The callback dispatches the event to per-player state via `0x524880`.

Inside `0x524880`:

- EventGoal's credited scoring side is compared with the player's actual side;
- when they are equal, the function iterates **`Sender<EventPlayerGoal>`** at PlayerProxy +0x20;
- when they differ, it iterates **`Sender<EventPlayerOwnGoal>`** at PlayerProxy +0x30.

RTTI independently identifies those two sender bases:

- vtable `0x7CA84C` = `Sender<EventPlayerGoal>`
- vtable `0x7CA844` = `Sender<EventPlayerOwnGoal>`

### Conclusion

**record +0x20 is the own-goal/scoring-side inversion flag.**

- `+0x20 = 0` -> credited side equals player's actual side -> ordinary player goal;
- `+0x20 != 0` -> credited side is flipped -> player is credited with an own goal for the opponent.

Therefore MatchCalculator types **0..4 are not simply "normal goal / own goal" categories**. Own-goal attribution is orthogonal to the type code and can accompany the goal-family record model through +0x20.

This substantially narrows the remaining type-0..4 problem to the *kind/source/context of scoring event* rather than scorer-vs-own-goal identity.


## Goal-family outcome code resolved at record +0x24

The apparent contradiction where types 1..4 were sometimes created without a score increment is now resolved.

These records describe **goal-scoring chances/outcomes**, while field `record +0x24` stores the chance result.

### Base outcome values

Across the type-1, type-2, type-3 and type-4 creation branches:

- **+0x24 = 0** -> **goal**
  - every verified branch with this base value increments side score at match record `+0xD4C/+0xD50` immediately before record creation;
- **+0x24 = 1** -> **miss / failed shot before goalkeeper save resolution**
  - these branches create the chance record without incrementing the score;
  - in the clearest type-4 shooting path this outcome is selected before the goalkeeper-vs-shot contest is entered;
- **+0x24 = 2** -> **saved/stopped by goalkeeper**
  - no score increment occurs;
  - in the type-4 path this result is generated after the goalkeeper `Goalkeeping` (+0x2B) contest defeats the shooter's chance.

### +3 presentation variant

The common record creators draw RNG(0..99) and compare against float constant `0x83B4FC = 10.0`.

On the selected branch they add **3** to the base outcome:

- 0 -> 3
- 1 -> 4
- 2 -> 5

Thus the semantic result is preserved by `outcome % 3`; the +3 bank is a secondary presentation/variant encoding rather than a different football result.

Exact purpose of the +3 variant (for example alternate FastView/animation treatment) remains unresolved.

### MatchController confirms goal-only forwarding

For MatchCalculator types 0..4, MatchController at `0x51993A` reads record +0x24.

It continues to construct/send semantic `EventGoal` only when:

- +0x24 == 0, or
- +0x24 == 3.

Values 1/2/4/5 are skipped by the semantic goal sender.

Therefore the class name `EventGoal` is literal: only scored outcomes from the broader calculator chance records reach FastView as EventGoal.

### Consequence

MatchCalculator types 0..4 identify **chance/source families**, not success/failure.

Success is orthogonally encoded by `+0x24`, while own-goal attribution is separately encoded by `+0x20`.

The scoring record model is therefore:

- `+0x28` = chance/source family type;
- `+0x24 mod 3` = outcome (goal / miss / saved);
- `+0x20` = scoring-side inversion / own-goal flag;
- `+0x2C` = additional context flag, still being resolved.


## MatchCalculator type 0 is unused/reserved in this release

The active goal/chance-family source types in the analyzed FM2001 executable are **1, 2, 3, and 4**.

Evidence:

- exhaustive direct creator/call-site tracing finds normal MatchCalculator production paths for types 1, 2, 3, and 4;
- no normal calculator producer for type 0 has been found;
- the MatchRecord serialization/reconstruction code explicitly rebuilds only source types 1..4 from its compact source/type encoding and never reconstructs type 0;
- FastView still accepts type 0 in the shared 0..4 switch, indicating compatibility/reserved handling rather than active normal generation.

Conclusion:

- type 0 should currently be treated as **unused/reserved/legacy-compatible** in this release;
- active chance/source-family reverse engineering should focus on types 1, 2, 3, and 4.

Do not assign a football semantic to type 0 unless a producer is later found.


## Team Orders priority lists: captain and penalty takers

RTTI/source analysis identifies the squad/team-orders screen as **`PTeamOrders2K`** (vtable around `0x7C6FE0`, TypeDescriptor around `0x81DE68`, source path `Applications\\FootballManager\\SquadPan.cpp`).

The MatchCalculator accesses four ordered player-priority categories through club/user helpers `0x40D620` / `0x40D650`.

### Category 0 = captaincy order

Helper `0x408560` reads priority category **0** and returns the first eligible listed player.

Both major team-strength aggregators `0x62F140` and `0x62F3E0` call this helper. The selected player's runtime:

- `+0x2C` = Confidence
- `+0x2D` = Leadership

are combined into a team-wide strength multiplier.

EA's English resources independently contain the matching Team Orders labels `Captains`, `Click for captaincy order`, and `CAPTAIN`.

Therefore priority category **0 is the captaincy order**.

### Category 1 = penalty-taker order

Helper `0x631F10` explicitly reads priority category **1**.

The penalty-shootout routine around `0x631730` also reads category 1 for both sides and reorders/chooses penalty candidates through that priority list before the shootout sequence.

EA's English resources independently contain `Penalty Takers`, `Click for penalties order`, and `PENALTIES`.

Therefore priority category **1 is the penalty-taker order**.

## MatchCalculator chance type 4 = penalty kick

Chance resolver `0x62D660` is now semantically resolved as a **penalty-kick attempt**.

Evidence:

1. It selects the attacking player through `0x631F10`, the confirmed category-1 penalty-taker selector.
2. The attempt is a direct one-player shot:
   - the taker's **Shooting** byte at runtime `+0x24` drives the initial miss/failure test;
   - the defending goalkeeper is selected separately;
   - goalkeeper **Goalkeeping** at runtime `+0x2B` drives the save/stop contest.
3. The three outcomes match the already-decoded chance result at record `+0x24 mod 3`:
   - 0 = goal
   - 1 = miss
   - 2 = goalkeeper save
4. Successful branches increment the appropriate score field before appending the chance record.
5. The resolver emits the fixed **type-4** chance record through `0x62EEA0`.

Thus active MatchCalculator source type **4 = penalty kick**.

This is distinct from penalty-shootout presentation: shootouts reuse type-1 records while the MatchController's current phase reroutes them to `EventPenaltyShootoutShot`. Type 4 is the normal-match penalty-kick chance family.


## Active chance-source taxonomy resolved: open play / free kick / corner / penalty

The four active MatchCalculator chance source types are now semantically resolved for this release.

### Team Orders category 2 = corner-kick order

Selector `0x632280` reads Team Orders priority category **2** through `0x40D620/0x40D650`.

It is called by chance resolver `0x62D950`, which emits **source type 3**.

The resolver has a delivery/finishing structure rather than a direct one-player shot:

- the designated category-2 player is selected first as the set-piece taker;
- a separate attacking target/receiver is selected;
- the receiver's **Heading** skill at player `+0x26` participates in the chance-resolution path;
- Shooting also participates in later finishing branches;
- the opposing goalkeeper is resolved separately;
- outcomes are recorded through the shared goal/miss/save encoding.

This is the characteristic corner-delivery model.

EA's Team Orders strings independently list the order family after Captains and Penalty Takers as:

- `Corner Kicks (Left)`
- `Corner Kicks (Right)`

The MatchCalculator collapses the designated corner-priority selection into category 2.

Therefore:

- **Team Orders category 2 = corner-kick priority**
- **MatchCalculator source type 3 = corner chance**

### Team Orders category 3 = free-kick order

Selector `0x631FB0` reads Team Orders priority category **3**.

It is called by chance resolver `0x62CE10`, which emits fixed **source type 2** records.

Unlike the corner path, the selected category-3 player is itself the primary chance player. The resolver evaluates the taker's set-piece-selected role and direct attacking qualities including **Shooting** and **Passing**, then resolves the chance/goalkeeper outcome through the shared result model.

EA's Team Orders resources independently contain:

- `Free Kicks (Left)`
- `Free Kicks (Right)`

following the corner entries.

Therefore:

- **Team Orders category 3 = free-kick priority**
- **MatchCalculator source type 2 = free-kick chance**

### Source type 1 = ordinary/open-play chance

All normal-play uses of common record creator `0x62ECF0` in the main chance generator pass **source type 1**.

The dedicated set-piece resolvers instead emit:

- type 2 from the free-kick path;
- type 3 from the corner path;
- type 4 from the penalty-kick path.

No additional normal source family remains once those dedicated set pieces are removed.

Penalty shootouts also reuse type-1 records, but this is explicitly phase-dependent compatibility behavior: MatchController reroutes type-1 records through `EventPenaltyShootoutShot` while in shootout state.

Therefore source type **1 is the ordinary/open-play chance family** during normal match play.

### Final active source mapping

- **type 0** = unused/reserved in this release
- **type 1** = ordinary/open-play chance
- **type 2** = free kick
- **type 3** = corner
- **type 4** = penalty kick

Chance success/failure remains orthogonal in `record +0x24 mod 3`:

- 0 goal
- 1 miss
- 2 goalkeeper save

and own-goal attribution remains orthogonal at `record +0x20`.


## Possession / territorial segment statistics resolved

The five-minute MatchCalculator segment statistics at `+0x1000..+0x10CC` are now tied directly to FastView's named possession UI.

### Three raw possession-state counters

During segment simulation, MatchCalculator accumulates:

- match record `+0x1000` — side-0 possession/control count;
- `+0x1004` — neutral/contested possession-state count;
- `+0x1008` — side-1 possession/control count.

Routine `0x62C740` proves the side mapping:

- when side argument is 0, it increments `+0x1000`;
- when side argument is 1, it increments `+0x1008`;
- common contested/progression phases increment `+0x1004`.

### Normalization into per-segment percentages

At `0x62B50D..`, the three counters are summed.

The game computes:

- `100 * (+0x1000) / total` -> stored in segment array `+0x106C[index]`;
- `100 * (+0x1004) / total` -> stored in `+0x10CC[index]`;
- the third displayed percentage is later reconstructed as `100 - first - second`, corresponding to side 1 / `+0x1008`.

Small +/-5 random variation is applied within bounded ranges before storage, and the first two percentages are constrained so their sum does not exceed 100.

The raw counters are reset after each five-minute segment.

### FastView EventPossession bridge

MatchController at `0x5196A3..0x5197B8` calls `0x631240` to retrieve three segment values:

- `+0x100C[index]`;
- `+0x106C[index]`;
- `+0x10CC[index]`.

It smooths them and constructs `EventPossession` through `0x51A6B0`, then dispatches that event through the RTTI-identified `Sender<EventPossession>`.

The EventPossession constructor stores:

- byte `+0x0C` = the separate `+0x100C` metric;
- byte `+0x0D` = side-0 possession percentage;
- byte `+0x0E` = neutral/contested percentage;
- byte `+0x0F` = `100 - +0x0D - +0x0E` = side-1 percentage.

### PossessionFigures confirms the three percentages

The executable contains source path:

`Applications\FootballManager\FastView\PossessionFigures.cpp`

and art assets:

- `team_bar_2.444`
- `blank_bar.444`
- `team_bar_1.444`

PossessionFigures receiver `0x51EA80` reads EventPossession bytes `+0x0D/+0x0E/+0x0F` and formats all three as `%u%%`.

This confirms a three-part possession display: the two teams plus a neutral/contested component.

### +0x100C is territorial/pitch-position state, not another possession percentage

EventPossession byte `+0x0C`, sourced from segment array `+0x100C`, is not printed by PossessionFigures.

Instead it is consumed by the RTTI-identified `PossessionDiagram` path around `0x522BB0`, which changes among a three-state display.

The executable ships the matching assets:

- `pitch_left.444`
- `pitch_middle.444`
- `pitch_right.444`
- `pitch_normal.444`

Thus `+0x100C` is a **territorial / pitch-position bias metric** used to move the FastView possession diagram among left/middle/right states, while `+0x106C/+0x10CC` and the remainder represent the possession percentages.

Exact orientation of side 0 as screen-left/right depends on current team presentation and should not be hard-coded as home/away until that display mapping is traced.


## Chance record +0x2C resolved: headed vs shooting finish mode

The final one-bit chance field at `record +0x2C` is now semantically resolved.

Across the active chance families, the MatchCalculator computes effective **Heading** and **Shooting** strengths for the selected finisher using the same Condition × skill × position-compatibility × Form pipeline. It draws:

`RNG(effective_heading + effective_shooting)`

and compares the result with `effective_heading`.

- if the roll is below Heading strength, the chance follows the **Heading** branch and the record creator receives `+0x2C = 0`;
- otherwise it follows the **Shooting/kicked-finish** branch and receives `+0x2C = 1`.

This is directly visible in type-1 open play:

- headed branch around `0x62CA66` emits source type 1 with context/finish bit 0;
- shooting branch around `0x62CC2D` emits source type 1 with bit 1.

It independently repeats in the set-piece resolvers:

- type-2 free kick has headed-finish and shooting-finish branches using 0 and 1;
- type-3 corner has the same Heading-vs-Shooting weighted selection and emits 0/1 accordingly;
- normal-match type-4 penalties always emit 1, consistent with a kicked/shooting finish.

The serializer had already proven the field is exactly one bit. MatchController does not need it for scorer/own-goal attribution, because it describes **how the chance was finished**, not whether it scored.

Therefore:

- **record +0x2C = 0 -> headed finish**
- **record +0x2C = 1 -> shooting/kicked finish**

The clean-room event model now exposes this as `FinishMode.HEADED` / `FinishMode.SHOOTING`.

## Position compatibility routine 0x4EA440 fully mapped

The final numeric input to the type-4 penalty strength calculation is now reconstructed.

The runtime position object at player +0x248 contains three compatible/preferred zero-based position codes in its first three bytes and the current assigned role in byte +0x03 low 5 bits, read by 0x4EA3C0. Routine 0x4EA410 tests those three preferred codes.

Routine 0x4EA440 first returns **1.00** for an exact role match, then applies the original fallback table using literal doubles **1.00 / 0.90 / 0.85 / 0.80 / 0.75 / 0.70 / 0.50 / 0.10**.

The role codes are the same zero-based values used by the original data:

0 None, 1 GK, 2 RB, 3 LB, 4 CB, 5 SW, 6 RWB, 7 LWB, 8 ANC, 9 DM, 10 RM, 11 LM, 12 CM, 13 RW, 14 LW, 15 AM, 16 RF, 17 LF, 18 CF, 19 ST.

Representative fallbacks include RB from RWB/CB = 0.90, CM from DM/RM/LM/AM = 0.90, RM from RW = 0.85, AM from CF/ST = 0.75, and an out-of-position GK = 0.10. RF/LF have no special non-exact fallback and fall to 0.50.

Real records independently confirm the coding: David Seaman=1 GK, Tony Adams=4 CB, Patrick Vieira=12 CM, Dennis Bergkamp=18 CF, Thierry Henry=19 ST.

## First exact clean-room MatchCalculator resolver

The normal-match type-4 penalty routine is now implemented in reconstruction/match_calculator.py.

The implementation preserves the full 0x4EA440 position table, Condition factor, Shooting/Goalkeeping, Form, integer truncation points, minimum-strength override, RNG(3)/RNG(256)/RNG(800)/RNG(10) branch order, the record creator's RNG(100)<10 presentation variant, type-4 context flag, and the original no-record branch when high-score suppression rejects the otherwise-unsaved attempt.

This is the first complete evidence-backed scoring/chance resolver implemented as clean-room replacement code.


## Verified match-clock / phase scaffold

Routine `0x62AE90` gives an exact finite schedule for backend segment calculation.

Normal time invokes `0x62B1A0` at:

- first half: 5,10,15,20,25,30,35,40
- second half: 50,55,60,65,70,75,80,85

At minute 45 it creates type-6 HalfTime through `0x632640`.

If extra time is required, `0x632690` creates type-8 ExtraTime at minute 90, then the calculator runs:

- 95,100
- another type-8 ExtraTime boundary at 105
- 110,115

If a shootout is required, `0x631730` creates type-9 Penalties at:

- minute 90 when no extra time was played;
- minute 120 after extra time.

The final type-7 FullTime record from `0x632660` is created at:

- 90 for ordinary normal-time completion;
- 120 after extra time without a shootout;
- 130 after a penalty shootout.

The clean-room `match_clock.py` implements this timeline but deliberately leaves the upstream competition/tie decision (whether ET/penalties are required) outside the clock layer.


## Open-play helper routines resolved

The helper chain used by the type-1 open-play Heading/Shooting branches is now mapped numerically.

### 0x62BD80 — aerial Heading duel

Inputs include the selected attacking finisher and an opposing defender.

- if no defender is supplied, returns success;
- computes effective **Heading** for attacker and defender with the common Condition × skill × position × Form pipeline;
- draws `RNG(attacker_heading + defender_heading)`;
- attacker wins when `roll < attacker_heading`.

### 0x62C0D0 — Control vs Tackling duel

Same weighted-duel structure, but:

- attacker uses **Control** (+0x27);
- defender uses **Tackling** (+0x25).

No defender -> automatic attacker success.

### 0x62BFC0 / 0x62C310 / 0x62C420 — accuracy/execution gates

These three routines share one structure:

- `0x62BFC0` uses **Heading**;
- `0x62C310` uses **Shooting**;
- `0x62C420` uses **Set Piece** (+0x2E).

Each:

1. draws `RNG(320)`;
2. compares against `floor(effective_skill / 100)`;
3. if the skill threshold succeeds -> returns success;
4. otherwise draws `RNG(2)` and succeeds only when that roll is 0.

### 0x62C530 — goalkeeper / score-stop gate

The routine uses the active opposing goalkeeper at match state +0xE24.

1. draw `RNG(256)`;
2. calculate effective **Goalkeeping**;
3. if `roll < floor(effective_goalkeeping/100)` -> returns stopped/save;
4. otherwise draw `RNG(10)`;
5. if `roll >= 10-current_attacking_score` -> also returns stopped;
6. otherwise performs goal/stat bookkeeping and returns the goal-success path.

The type-1 caller encodes any nonzero return as SAVE outcome 2; therefore the high-score suppression path is represented as a stopped/saved chance to the event stream.

### Type-1 common record creator miss suppression

Common source-type-1 creator `0x62ECF0` has a behavior not shared by the dedicated type-2/3/4 creators.

It always draws `RNG(100)`.

Before minute 130:

- if roll < 10, adds +3 to the base outcome;
- after that, if the resulting outcome is still exactly 1 (plain MISS), it returns 0 without appending a record.

Consequently ordinary type-1 misses are normally omitted from the event list; only the 10% presentation-variant miss (raw outcome 4) is retained.

At minute >=130, used by penalty-shootout compatibility routing:

- no +3 presentation variant is added;
- plain miss outcome 1 is retained.

This behavior explains how the same type-1 record creator can serve sparse normal-play highlights and complete penalty-shootout attempts.


## Type-1 outer open-play flow and positional player pools

The outer normal-play flow around `0x62C740` is now structurally mapped.

### Positional pools built by 0x62DE90

Before a side's chance is resolved, `0x62DE90` rebuilds role-grouped active-player pools.

Attacking pools:

- `+0xDF8`, count `+0xF44` — RM / LM / CM (roles 10,11,12);
- `+0xDCC`, count `+0xF40` — RW / LW / AM (13,14,15);
- `+0xDA0`, count `+0xF3C` — CF / ST (18,19).

RF/LF (16,17) are not placed into these three attacking-selection pools.

Defending pools:

- `+0xE24` — goalkeeper;
- `+0xE28`, count `+0xF4C` — RB / RWB;
- `+0xE54`, count `+0xF48` — LB / LWB;
- `+0xE80`, count `+0xF50` — CB / SW;
- `+0xF04`, count `+0xF5C` — ANC / DM / CM;
- `+0xED8`, count `+0xF58` — RM;
- `+0xEAC`, count `+0xF54` — LM.

Inactive/unavailable players are filtered before entering these pools.

### Initial ball carrier / passer: 0x62B780

The initial open-play player is selected from:

1. RM/LM/CM pool `+0xDF8` if non-empty;
2. otherwise RW/LW/AM pool `+0xDCC`;
3. otherwise no open-play carrier is returned.

Selection within the chosen pool is uniform via bounded RNG.

### Role-matched first defender: 0x62B7D0

The initial defender is selected based on the carrier's current role:

- RM -> defending RM;
- LM -> defending LM;
- CM -> central ANC/DM/CM pool;
- RW -> defending RM, falling back to RB/RWB;
- LW -> defending LM, falling back to LB/LWB;
- AM -> central ANC/DM/CM, falling back to CB/SW;
- CF/ST -> central ANC/DM/CM;
- RF/LF -> no mapped defender in this helper.

### First duel and pass

`0x62B9D0` resolves the carrier's **Control** against the selected defender's **Tackling** with the shared effective-skill formula and weighted RNG.

The helper returns true when the defender wins the tackle. The type-1 generator aborts that open-play sequence on this result.

If the carrier survives, `0x62BBF0` performs a Passing gate:

- draws `RNG(320)`;
- computes effective **Passing**;
- succeeds only when `roll < floor(effective_passing/100)`;
- unlike the later finishing accuracy helpers, there is no RNG(2) fallback.

Failure aborts the sequence.

### Possession/control accounting

At the start of this resolution step the neutral/contested counter `+0x1004` is incremented.

The attacking side's possession/control bucket `+0x1000` or `+0x1008` is also incremented according to side.

This links the open-play flow directly to the already-mapped three-part EventPossession model.

### Finisher selection: 0x62BCE0

After a successful carrier duel/pass, the actual finisher is selected with one `RNG(100)`:

- roll < 50: choose a random CF/ST if that pool is non-empty;
- else roll < 75: choose a random RW/LW/AM if available;
- otherwise choose a random RM/LM/CM.

If the preferred bucket for that random range is empty, the routine falls through to available alternatives.

Thus the intended role weighting is approximately:

- 50% CF/ST;
- 25% RW/LW/AM;
- 25% RM/LM/CM,

subject to pool availability.

### Close defender: 0x62B900

A second, closer defender is selected for the finisher:

- RM/RW -> RB/RWB;
- LM/LW -> LB/LWB;
- CM/AM/CF/ST -> CB/SW;
- RF/LF -> no defender.

If the original carrier and finisher are the same player, the generator bypasses the Heading-vs-Shooting selection and enters the shooting-finish branch directly.

Otherwise effective Heading and Shooting are calculated and the already-mapped FinishMode weighted roll chooses the headed or kicked finish.

### Failed final duel can create a set piece

If the final **Heading-vs-Heading** duel or **Control-vs-Tackling** duel is lost, both finish branches enter the same set-piece transition logic.

1. draw `RNG(4)`;
2. only when that roll is 0 and a close defender exists:
   - draw `RNG(100)`;
   - if roll < **20** -> invoke type-4 **penalty** resolver `0x62D660`;
   - otherwise -> invoke type-2 **free-kick** resolver `0x62CE10`.
3. otherwise draw `RNG(2)`;
   - roll 0 -> invoke type-3 **corner** resolver `0x62D950`;
   - roll 1 -> no chance event from this branch.

This gives an exact transition structure from a lost final duel into the dedicated set-piece resolvers.

### Direct corner branch before open play

Immediately after rebuilding the positional pools, `0x62C740` draws `RNG(100)` and compares it against literal float **5.0**.

- roll < 5 -> bypass ordinary open-play setup and invoke the type-3 corner resolver directly;
- otherwise -> continue into carrier selection.

Thus this stage has an explicit **5% direct-corner branch** before the ordinary type-1 sequence.

### Rare own-goal attribution on a scored open-play chance

After `0x62C530` has accepted a goal and incremented the attacking score, the Heading and Shooting goal branches draw `RNG(20)`.

When the roll is 0 and a close defender exists, the type-1 goal record is emitted with the already-proven side-inversion flag set. Otherwise a normal scorer record is emitted.

Therefore successful open-play goals with an involved close defender have a **5% record-attribution branch to own goal** at this stage.

The score increment itself remains on the attacking side; the inversion changes player attribution in the semantic event stream.


## Clean-room positional pools and selectors

The mapped 0x62DE90/0x62B780/0x62B7D0/0x62B900/0x62BCE0 role pools and selectors are now implemented in reconstruction/match_calculator.py. The 0x62BCE0 finisher helper preserves the original single RNG(100) roll while falling through empty buckets. The early 0x62B9D0 duel remains distinct from later 0x62C0D0 because its true return means the defender won; 0x62BBF0 remains a separate Passing gate without coin-flip recovery.


## Clean-room outer type-1 resolver

The mapped 0x62C740 shell is now implemented as resolve_open_play_attempt(). It returns both semantic chance records and explicit set-piece handoffs while preserving the original RNG order and possession counter increments. Free-kick/corner transitions remain explicit boundaries rather than placeholder simulations, keeping the clean-room implementation evidence-backed.


## Type-2 free-kick and type-3 corner flows completed

Type-2 free kicks now have a complete post-taker-selection model. The normal branch computes effective Shooting and Passing, forms floor((Shooting + Passing) * 1.2), and draws RNG(bound). A roll below effective Shooting selects the direct shot; otherwise the free kick is delivered. Cached match context overrides this choice: a cached taker with no cached receiver forces direct execution, while a cached receiver forces delivery.

Direct free kicks use the Shooting accuracy helper, then the shared goalkeeper/high-score gate, and emit type-2 records with shooting FinishMode. Delivered free kicks require Set Piece execution first, increment the attacking possession/control bucket a second time, select a receiver, and reuse the shared Heading/Shooting finish machinery. A cached distinct receiver forces the headed branch; taker==receiver forces shooting. Failed final duels retain the already-mapped penalty/free-kick/corner transitions.

Type-3 corners increment attacking possession/control at entry, require Set Piece execution, increment possession again after successful delivery, then choose a distinct receiver. receiver==taker returns without a chance. A cached receiver forces Heading; otherwise the ordinary weighted Heading-vs-Shooting selector is used. Final duel, accuracy, goalkeeper and failed-duel transitions are shared with the other chance families.

Type-2 creator 0x62EE20 and type-3 creator 0x62EFD0 both apply the 10% +3 presentation-variant bank and keep side inversion clear. For delivered records the semantic scorer is the receiver/finisher; the set-piece taker is retained in the secondary raw MatchRecord player slot.

The clean-room reconstruction now implements resolve_free_kick() and resolve_corner() for these post-taker-selection flows.


## Five-minute attacking-sequence driver at 0x62B1A0

The top-level per-segment chance-frequency logic is now mapped.

For the two sides, 0x62B1A0 evaluates the paired team-strength routines in opposite directions:

- side-0 attacking-side strength from 0x62F140 divided by side-1 opposing strength from 0x62F3E0, then multiplied by **1.10**;
- side-1 attacking-side strength from 0x62F140 divided by side-0 opposing strength from 0x62F3E0, then multiplied by **0.90**.

The shipped constants are exact doubles 1.1 and 0.9.

Each ratio is then multiplied by 100 and converted toward zero to an integer attack weight. Let these be W0 and W1.

The total number of attacking-sequence iterations for the five-minute segment is:

`sequence_count = floor((W0 + W1) / 30)`

The division-by-30 is implemented through the signed magic constant 0x88888889.

For every sequence iteration the game draws:

`RNG(W0 + W1)`

- roll < W0 -> side 0 attacks;
- otherwise -> side 1 attacks.

The event minute is distributed across the five-minute segment from the overall iteration index i and total N:

`event_minute = segment_start + floor(5 * i / N) + 1`

This gives event minutes inside the interval immediately after the segment start, e.g. the segment invoked at minute 5 produces events in minutes 6..10.

The selected side is then passed into 0x62C740, the already-mapped open-play/set-piece shell. After each sequence the calculator also runs that side's Condition/injury update and disciplinary update, and with probability 1/7 invokes the AI substitution path for the opposite side.

This means chance frequency is not a free-running per-minute process: each five-minute block has a finite strength-derived number of attacking sequences, each assigned to one side by a weighted draw.

The remaining major prerequisite for a complete segment simulator is the exact numeric content of team-strength routines 0x62F140 and 0x62F3E0.
