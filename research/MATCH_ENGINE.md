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


## Five-minute team-strength builders: structural mapping checkpoint

The two paired routines feeding the five-minute attack scheduler are now structurally separated.

### 0x62F140 — attacking/build-up strength

This routine iterates the active players for one side and accumulates weighted contributions from all **17 player skills**. The coefficient lookup is indexed by the player's current role/position and current team-tactic state. The resulting floating aggregate is then modified by team-level context before being returned to the segment scheduler.

### 0x62F3E0 — defensive/resistance strength

This companion routine performs the same broad pattern for the opposing/defensive dimension: it iterates active players, applies role/tactic-specific coefficients across all 17 skills, and then applies formation/team-level modifiers before returning the second strength aggregate used by the five-minute segment driver.

### Shared structure now confirmed

Both routines depend on:

- all 17 player attributes;
- current player role/position;
- large EA coefficient tables rather than a small hand-written formula;
- current team tactical settings;
- formation/shape state;
- mentality/aggression-style team modifiers;
- separate human/AI contextual modifiers.

The five-minute scheduler therefore does **not** invent attacks from raw overall ratings. It consumes two higher-level, role-aware team-strength aggregates built from the original player/tactic matrices.

### Important position-code consistency issue under review

A formation-coverage helper used by this path groups several role codes in a way that may conflict with the current clean-room `PositionRole` naming for the advanced midfield/wing codes. In particular, one helper groups code 14 with the right-sided defensive/midfield roles and code 15 with the left-sided equivalents, while code 13 behaves centrally.

This could mean the existing enum labels for roles 13/14/15 need correction even though the numeric codes themselves are right. No reconstruction code should be changed until the original Static.dat position table and executable consumers are reconciled.

This issue is now explicitly checkpointed so future sessions do not silently rely on possibly shifted semantic labels.


## Team-strength coefficient matrices and tactic selectors

The coefficient tables used by the two five-minute strength builders are now structurally proven.

Attack routine `0x62F140` reads doubles from **0x83B838**.

Defence routine `0x62F3E0` reads doubles from **0x83E2B8**.

The difference is exactly:

`0x2A80 = 10880 bytes = 1360 doubles = 4 × 20 × 17`.

The executable's index arithmetic is therefore:

`coefficient[tactic_style][runtime_role][skill]`

with:

- 4 tactic-style values;
- 20 runtime role codes;
- 17 player skills.

Attack and defence each have their own complete 4×20×17 matrix.

### Tactic bytes

Attack indexes its matrix using team byte **+0x1B6**, matching the four **With Ball** styles:

- 0 Normal
- 1 Short Pass
- 2 Long Ball
- 3 Counter

Defence indexes its matrix using team byte **+0x1B5**, matching the four **Without Ball** styles:

- 0 Normal
- 1 Contain
- 2 Press
- 3 Offside Trap

The separate three-state team byte **+0x1B4** is the Play style:

- 0 Play Attack
- 1 Play Normal
- 2 Play Defend

Routine `0x40DA30` converts those initial values into match-bias states:

- Play Attack -> 3
- Play Normal -> 2
- Play Defend -> 1

The live match bias itself can occupy 0..4.

### Position-code clarification

Runtime role codes remain the already-proven zero-based values (13 RW, 14 LW, 15 AM). Static.dat position IDs are one-based, which explains the apparent one-step discrepancy seen in one formation helper. No clean-room enum correction is required.


## Team-strength post-matrix modifiers

After summing role/skill contributions, the builders apply a set of exact team-level multipliers.

### Five-level match bias

Attack `0x62F140`:

- bias 0 -> ×0.80
- 1 -> ×0.90
- 2 -> ×1.00
- 3 -> ×1.10
- 4 -> ×1.20

Defence `0x62F3E0` uses the inverse ordering:

- bias 0 -> ×1.20
- 1 -> ×1.10
- 2 -> ×1.00
- 3 -> ×0.90
- 4 -> ×0.80

### User-controlled club predicate

Routine `0x4037B0(team)` is the user-controlled-club test. It forwards the club ID into the DBRUser list and checks whether a user's current club matches.

### Active captain modifier

Routine `0x408560(team)` walks Team Orders category 0 and returns the first valid captain.

The builders read that player's:

- runtime +0x2C = Confidence
- runtime +0x2D = Leadership

Attack captain multiplier:

`0.95 + (Confidence + Leadership) / 5120`

Defence captain multiplier:

`0.90 + (Confidence + Leadership) / 2560`

If no captain is available, this stage leaves the base strength unchanged.

For AI-controlled clubs, the captain/user branch is replaced by fixed multipliers:

- attack ×1.05
- defence ×1.10

### Aggression multiplier

For user-controlled teams, team byte +0x1B7 applies:

`1.0 + (aggression - 5) × 0.02`

Thus aggression 5 is neutral, 0 -> 0.90, and 9 -> 1.08.

### Defence-only formation coverage

Defence additionally calls `0x62F6A0`.

That helper begins with:

- central requirement counter = 2;
- five coverage flags = set.

Active current roles satisfy/clear those requirements.

It returns:

`formation_multiplier = 1.0 - 0.05 × (central_count² × 4 + remaining_flags)`

This is a shape/coverage penalty applied only to defence.

Some branch groupings inside `0x62F6A0` are non-intuitive; they should be reproduced literally rather than “corrected” to football expectations.


## Per-player strength contribution formula

The inner contribution loop of both `0x62F140` and `0x62F3E0` is now exact.

For each active player and each of the 17 skills:

1. build the already-recovered effective skill integer:
   `(floor(Condition/3)+66) * raw_skill`, then position compatibility, then Form, with truncation after each floating multiplier;
2. if the per-match player-state disable flag is set, use effective strength **1** instead;
3. multiply by **1/255** (`0x7D7F10 = 0.00392156862745098`);
4. multiply by the appropriate tactic/role/skill matrix coefficient;
5. multiply by the role balance factor / 100;
6. add to the team sum.

Thus one contribution is:

`(effective_skill / 255) * matrix[tactic][role][skill] * (role_factor / 100)`

### Role balance factors

For runtime roles 0..12, attack uses the integer table at **0x840D38**:

`[105,108,110,120,112,115,97,95,102,92,90,117,100]`

For roles 13..19 attack uses 100.

Defence uses:

- `200 - attack_role_factor` for roles 0..12;
- 100 for roles 13..19.

Therefore defence role factors for 0..12 are:

`[95,92,90,80,88,85,103,105,98,108,110,83,100]`.

The final `/100` is literal constant **0.01** at `0x7BD600`.

This role split is independent of the much larger 4×20×17 coefficient matrices.


## Clean-room team-strength builders and scheduler implemented

The verified `0x62F140` / `0x62F3E0` team-strength formulas are now executable in `reconstruction/match_strength.py`.

Implemented exactly from the current reverse-engineering evidence:

- all 17 raw player skills;
- shared effective-skill pipeline (Condition, positional compatibility, Form, disable/minimum override);
- 4 x 20 x 17 tactic/role/skill coefficient matrices;
- attack role-balance table at `0x840D38`;
- defence role factors as `200 - attack_factor` for roles 0..12;
- five-level live match-bias multipliers;
- user captain Confidence/Leadership multipliers;
- fixed AI attack/defence multipliers;
- user aggression multiplier;
- defence-only literal `0x62F6A0` formation-coverage multiplier.

The same module now contains the verified head of `0x62B1A0`:

- side-0 ratio x1.10 and side-1 ratio x0.90;
- integer attack weights after x100 conversion;
- `floor((W0+W1)/30)` sequence count;
- side selection through `RNG(W0+W1)`;
- event-minute distribution `segment_start + floor(5*i/N) + 1`.

Deterministic regression coverage is in `reconstruction/test_match_strength.py`.

### Exact-source validation

The original Library disc image was re-materialized and converted from raw MODE1/2352 sectors to ISO9660 locally. The root `FOOTBAL.EXE` hashes to the expected analyzed executable SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

The existing data-free coefficient loader successfully reads both real matrices from that executable as exact `4 x 20 x 17` double arrays. Observed values are plausible sparse football weights (attack range 0.0..1.2, defence range 0.0..1.3), providing an additional direct validation that the mapped table geometry and PE loader are correct.

This closes the former main numeric prerequisite for the five-minute attack-frequency scheduler. The next backend step is orchestration: use these strengths to run each normal-time segment through the already-implemented chance resolvers and accumulate a complete score/event timeline.


## Exact recurring Condition / injury / discipline formulas recovered

Fresh direct disassembly of the canonical executable resolves much more of the per-sequence tail of `0x62B1A0`.

### Per-sequence call order

After each scheduler-selected attacking sequence, `0x62B1A0` calls, in order:

1. `0x62C740` chance resolution;
2. `0x62E6F0(attacking_side, event_minute)` Condition/injury update;
3. `0x62E130(attacking_side, event_minute)` discipline update;
4. with probability `1/7`, `0x62E2F0` AI substitution logic.

Thus both Condition and discipline run once per generated attacking sequence, not merely once per five-minute segment.

### Condition probability helper `0x62E6C0`

The helper consumes:

- team tactical Aggression byte `+0x1B7`;
- player Stamina raw byte `+0x20`.

It returns exactly:

```
floor((256 - Stamina) / 32) + 2 * Aggression
```

The caller compares `RNG(100)` against this threshold.

Workload is role- and side-asymmetric:

- **attacking side**
  - runtime roles >=16: full threshold;
  - roles 8..15: threshold / 2, integer-truncated;
  - roles <=7: no Condition roll.
- **defending side**
  - roles <=7: full threshold;
  - roles 8..15: threshold / 2, integer-truncated;
  - roles >=16: no Condition roll.

The attacking side is iterated first, then the defending side. On a successful roll, Condition `+0x77` is decremented by one only when it is greater than 1. The injury routine `0x62EAE0` is then called immediately with the changed player and current event minute.

This means Condition changes inside the scheduler sequence loop can affect later skill checks in the same five-minute segment even though team attack/defence weights were built once at the beginning of that segment.

### Injury incidence `0x62EAE0`

Confirmed incidence score:

```
environment_component
+ floor(InjuryProneness / 8)
+ max(0, ConditionInjuryInducingLevel - Condition)
```

where:

- `environment_component = match_environment_byte >> 6`, therefore 0..3;
- Injury Proneness is player raw skill byte `+0x22`;
- shipped executable default `ConditionInjuryInducingLevel` at `0x821814` is **75**.

The injury roll is:

```
RNG(1000) < incidence_score
```

with the following additional guards:

- goalkeeper role 1 is excluded;
- an already-injured player is excluded;
- the incidence score must be non-zero;
- a global match injury cooldown requires the previous injury minute to be **strictly earlier than current_minute - 10**.

The RNG(1000) draw occurs before the ten-minute cooldown check.

On success, the routine stores the current minute as the last-injury minute, marks the side/player injury state, creates the confirmed type-5 Injury record, and then attempts a replacement/substitution through the existing type-10 path when allowed.

The higher-level semantic name of the source byte copied into match `+0xD47` is **not yet proven**. Only its use as a 0..3 injury environment component is confirmed, so reconstruction should keep it generically named until the source object field `+0x1D7` is identified.

The adjacent shipped tuning global `ConditionInjuryRandomiser` at `0x821818` defaults to **3**, but it is not used in this incidence gate. Its separate use should be traced before assigning semantics.

### Discipline routine `0x62E130`

Discipline is applied to the **defending/opposing side** of the scheduler-selected attack.

Overall incident gate for that defending team's Aggression:

```
RNG(800) < floor(Aggression * Aggression / 2) + 12
```

If that succeeds, `RNG(100)` selects a role band for the candidate foul/card player:

- roll <=40: runtime roles 3..7;
- 41..85: roles 8..12;
- 86..99: roles 13..19.

The band bounds in `0x62E5D0` are strict (`role > lower && role < upper`). The helper counts eligible active players, selects a 1-based target through `RNG(count)+1`, and contains an additional bias involving position-state byte `+0x05`: while scanning before the target, a player whose `+0x05 & 0x1F == 8` can be selected early when `RNG(10) < 5`. The higher-level meaning of that secondary position-state byte is not yet named.

For an unbooked selected player:

- `RNG(100) >= Aggression` creates a **Booked** event and sets booked byte `+0x48 = 1`;
- `RNG(100) < Aggression` bypasses the booking and proceeds to the dismissal test, providing the direct-red path.

Dismissal escalation:

```
RNG(10) < Aggression
```

followed by:

```
RNG(5) < 4 - defending_side_red_count
```

On success the routine creates **Sent Off**, sets `+0x49 = 1`, increments the defending side's dismissal count, and removes/resets the player from active on-field selection. The second gate naturally prevents a fifth sending-off for one side.

### Exact segment statistics normalization

The tail of `0x62B1A0` / `0x62B3F0` is now instruction-mapped and implemented in `reconstruction/match_statistics.py`.

Territory starts at 50. When at least one attacking sequence exists:

```
territory = floor(side0_attack_sequences * 100 / total_attack_sequences)
```

If `5 < territory < 95`, add `RNG(10)-5`, then clamp to 0..100.

Raw possession counters are `side0 / neutral / side1`. If their sum is positive:

```
side0_percent  = floor(side0_raw  * 100 / raw_total)
neutral_percent = floor(neutral_raw * 100 / raw_total)
```

otherwise both stored percentages start at 33.

Each stored percentage independently receives `RNG(10)-5` only when strictly between 5 and 95 and is clamped to 0..100. If their sum exceeds 100, side0 is reduced to `100-neutral`. Side1 is the implicit remainder.

This exact normalization is now integrated into all 16 normal-time statistic slots in the clean-room orchestrator.


## Team-strength role-factor indexing correction

**Confirmed, superseding the earlier assumption that the small role-balance table is indexed by the current assigned role.**

Direct instruction-level recheck of both `0x62F140` and `0x62F3E0` proves that two distinct fields in the player position-state object are used:

- `0x4EA3C0` returns `position_state[+0x03] & 0x1F`.
  - This is the current/assigned runtime role.
  - It is passed into `0x4EA440` for positional compatibility.
  - It selects the role dimension of the 4 x 20 x 17 attack/defence coefficient matrix.
- `0x4EA3E0` returns `position_state[+0x05] & 0x1F`.
  - This separately indexes the small balance-factor table at `0x840D38` when the value is below 13.
  - Values >=13 use a neutral 100% balance factor.
  - Attack uses the table value directly.
  - Defence uses `200 - table[value]`.
  - The higher-level semantic name of this +0x05 field is still unresolved.

Therefore one player/skill contribution is more precisely:

```
(effective_skill / 255)
* matrix[tactic][current_role_from_+0x03][skill]
* balance_factor[position_state_+0x05] / 100
```

and the two position-state codes must **not** be conflated.

The clean-room reconstruction now carries the second field explicitly as `balance_position_code`. It is required from prepared match-day state instead of silently defaulting to the assigned role. Regression source includes a case where current role 12 and balance code 3 deliberately differ, proving that the matrix row and balance factor are independently selected.

This same +0x05 accessor is also used by the discipline candidate helper for its special `code == 8` selection bias, providing an additional independent use of the field.
## AI substitution routine `0x62E2F0`

**Confirmed from the canonical executable.**

The normal five-minute scheduler calls the AI substitution routine only after the chance, Condition/injury, and discipline paths. After each attacking sequence it performs `RNG(7)`; only a zero result invokes `0x62E2F0`, and the side passed to the substitution routine is the **opposite side from the scheduler-selected attacker**.

The routine exits unless all of the following hold:

- generic MatchCalculator guard byte `+0x1145` is nonzero;
- the selected side is AI controlled (`0x4037B0(team)` is false);
- the current minute meets the substitution timing threshold;
- the selected side is not currently leading.

The timing helper `0x409A70` starts at 3 and scans the original starting XI, decrementing once for every original starter whose active-player bit is no longer set. The threshold is then:

```
threshold_minute = (9 - remaining_value) * 10
```

For an untouched starting XI this gives the first possible automatic change at minute 60. After one original starter has left active state it becomes 70, then 80 after two. Because the helper literally counts inactive original starters rather than a separate abstract substitution counter, reconstruction should preserve that state-derived behavior.

Outgoing candidates are scanned over the original eleven lineup slots in reverse order and must still be active. The two role-band helpers together accept only current assigned roles **8..19**. Therefore this automatic AI path does not choose goalkeepers or roles 2..7 as the outgoing player.

For each eligible outgoing player, team helper `0x409950` scans the selected match-participant roster for players in the substitute-available state. It computes `0x41C7E0(candidate, outgoing_current_role)` and keeps the first candidate with the strictly greatest role rating. The helper separately starts with a value of 3 and decrements for every participant who is neither active nor substitute-available; if the resulting value is non-positive, no replacement is returned. After `0x409950` returns, `0x62E2F0` also requires the chosen replacement's pre-substitution current role to be in 8..19.

The outer routine evaluates each surviving outgoing/incoming pair as:

```
outgoing_value = current_role_rating(outgoing) * form_multiplier(outgoing)
incoming_value = role_rating(incoming, outgoing_current_role) * form_multiplier(incoming)
difference = trunc_toward_zero(outgoing_value - incoming_value)
```

The initial best difference is 200, and the pair with the **strictly smallest** difference is retained. Thus the routine prefers the largest role-and-form improvement, while preserving first encountered candidates on ties.

`current_role_rating(outgoing)` is helper `0x41E1B0`, which simply obtains the outgoing player's current assigned role and calls `0x41C7E0` for that role.

### Role rating helper `0x41C7E0`

The role-rating helper is now fully specified for the roles used by the substitution path.

Each selected raw current skill is first converted to the game's 0..30 display scale:

```
display_skill = floor((30 * raw_skill + 128) / 255)
```

Seven weighted display skills are then summed. Canonical skill indices use the 17-skill order already documented in `PLAYER_DEVELOPMENT.md`:

```text
role 1 :  Strength .3, Confidence .4, Speed .2, Passing .1, Awareness .7, Agility .7, Goalkeeping .9
role 2 :  Strength .3, Confidence .5, Speed .5, Heading .4, Shooting .1, Passing .6, Tackling .9
role 3 :  Strength .3, Confidence .5, Speed .5, Heading .4, Shooting .1, Passing .6, Tackling .9
role 4 :  Strength .3, Confidence .5, Speed .5, Heading .6, Shooting .1, Passing .4, Tackling .9
role 5 :  Strength .3, Confidence .4, Speed .5, Heading .3, Shooting .2, Passing .7, Tackling .9
role 6 :  Strength .3, Confidence .4, Speed .6, Heading .2, Shooting .3, Passing .7, Tackling .8
role 7 :  Strength .3, Confidence .4, Speed .6, Heading .2, Shooting .3, Passing .7, Tackling .8
role 8 :  Strength .3, Confidence .4, Speed .4, Heading .5, Shooting .2, Passing .6, Tackling .9
role 9 :  Strength .3, Confidence .3, Speed .3, Heading .5, Shooting .3, Passing .9, Tackling .7
role 10:  Strength .3, Confidence .3, Speed .4, Heading .5, Shooting .3, Passing .9, Tackling .6
role 11:  Strength .3, Confidence .3, Speed .4, Heading .5, Shooting .3, Passing .9, Tackling .6
role 12:  Strength .3, Confidence .3, Speed .4, Heading .5, Shooting .3, Passing .9, Tackling .6
role 13:  Strength .3, Confidence .4, Speed .7, Heading .2, Shooting .5, Passing .8, Tackling .4
role 14:  Strength .3, Confidence .4, Speed .7, Heading .2, Shooting .5, Passing .8, Tackling .4
role 15:  Strength .3, Confidence .4, Speed .4, Heading .4, Shooting .6, Passing .8, Tackling .4
role 16:  0
role 17:  0
role 18:  Strength .3, Confidence .4, Speed .5, Heading .5, Shooting .9, Passing .5, Tackling .2
role 19:  Strength .3, Confidence .5, Speed .6, Heading .6, Shooting .9, Passing .2, Tackling .2
```

Every nonzero role's seven weights sum to 3.3. The weighted sum is multiplied by the existing `0x4EA440` positional-compatibility multiplier for the queried role, capped at 99.0, then 0.49 is added and `0x668350` truncates toward zero:

```
role_rating = trunc_toward_zero(
    min(weighted_sum * positional_compatibility, 99.0) + 0.49
)
```

Roles 16 and 17 route to the zero branch in this release.

### Substitution mutation and type-10 event

Team mutation helper `0x409AC0` copies two position-state values from outgoing to incoming before switching their active/substitute state:

- current assigned role, low five bits of position-state `+0x03`;
- the low four-bit auxiliary value at position-state `+0x04`.

It does **not** copy the separate `+0x05` balance-position code used by team strength and discipline. The outgoing player's position state is subsequently reset through `0x4EA370`.

The type-10 creator `0x62EF90` creates a substitution record carrying:

- side;
- outgoing side-local player index at record `+0x08`;
- incoming side-local player index at record `+0x30`.

The event minute is supplied by the caller. This is sufficient to represent the semantic substitution record independently of FastView presentation.
## Injury replacement path after `0x62EAE0`

**Confirmed from the canonical executable and now integrated into the clean-room normal-match loop.**

A successful injury is not merely a type-5 status event. The original routine immediately attempts a replacement after recording the injury:

1. update injury state and the global last-injury minute;
2. append type-5 subtype-2 Injury;
3. test automatic-replacement permission through `0x62EAB0`;
4. if allowed, call `0x409950(team, injured_player, participant_count)`;
5. if a replacement exists, apply `0x409AC0`;
6. append type-10 Substitution through `0x62EF90` at the same event minute.

The control helper `0x62EAB0` behaves as follows:

- AI-controlled team -> replacement path allowed;
- user-controlled team -> allowed only when MatchCalculator raw mode field `+0xD3C` equals 1 or 3;
- otherwise -> no automatic injury replacement.

The higher-level UI/competition meaning of `+0xD3C` remains unresolved. Reconstruction therefore exposes it as a raw `match_mode_code` rather than assigning an unsupported semantic name.

Unlike the scheduled AI substitution routine `0x62E2F0`, injury replacement does **not** apply the role-8..19 outgoing/incoming filters. It uses `0x409950` directly for the injured player's current assigned role, so defenders can be replaced through this path.

If no replacement is permitted or available, `0x62EAE0` does not itself deactivate the injured player. Removal occurs only if the substitution mutation succeeds.

### Dynamic participant iteration in `0x62E6F0`

The Condition loop iterates the match-participant pointer array and checks `0x417F50` separately for each entry when that entry is reached. It does not work from a frozen active-player snapshot.

This has a subtle but reproducible consequence: if an injury substitution activates a bench player whose participant-array slot appears later in the current Condition pass, that newly active player can also be processed for workload/Condition in the **same attacking sequence**.

The clean-room Condition loop now preserves this by accepting the full participant sequence, checking each player's active state dynamically, and applying the immediate injury-substitution callback before iteration continues.

### Shared match-state guard

The injury-incidence routine checks the same generic MatchCalculator byte `+0x1145` that guards discipline processing. Condition decay itself occurs outside that injury guard. Therefore disabling this match-state update byte suppresses injury incidence but does not suppress the underlying Condition decrement.

The semantic name of `+0x1145` is still unresolved and should remain generic until its initialization/source is identified.
## Pre-match participant construction

**Confirmed from the canonical executable.**

The high-level normal-match path constructs a MatchCalculator, then invokes a virtual pre-match population method before `0x62AC90`. Therefore `0x62AC90` is not the lineup selector: it initializes per-match state from participant arrays that are already populated.

### Participant collector `0x510CD0`

The participant collector receives a team object and destination player-pointer array. The team stores an ordered array of 16-bit player IDs beginning at `team+0x244`, with its roster count at `team+0x294`.

For each roster ID, the collector resolves the corresponding runtime `DBRPlayer` from the global player array. The executable arithmetic independently confirms a **592-byte DBRPlayer stride**.

A player is copied into the MatchCalculator participant array when either:

- `0x417F50(player, team)` reports the player active/on field; or
- `0x417F60(player, team)` reports the player available as a match substitute.

Players that satisfy neither predicate are omitted. Included players preserve the team's roster-ID iteration order.

`0x510D60` invokes this collector for both sides:

- side 0 participant pointers begin at MatchCalculator `+0x04`, count at `+0x5A4`;
- side 1 participant pointers begin at `+0x5B4`, count at `+0xB54`.

### Runtime starter/substitute flags

The two collector predicates are now traced to exact `DBRPlayer` flag bits for the player's current club.

After confirming `DBRPlayer+0x10` matches `team+0x04`:

- `DBRPlayer+0x14 bit 4 (0x10)` = **starting/on-field active flag**.
  - getter path: `0x417EE0 -> 0x417F50`;
  - setter `0x4182F0` sets bit 4 and clears bit 5.
- `DBRPlayer+0x14 bit 5 (0x20)` = **match substitute-available flag**.
  - getter path: `0x417F00 -> 0x417F60`;
  - setter `0x4182C0` sets bit 5 and clears bit 4.

Removal helper `0x4181B0` clears both match-selection bits and resets the player's position state.

This proves that the clean-room `active` and `substitution_available` concepts correspond to original runtime state rather than reconstruction-only abstractions.

### Ordering relative to AI lineup selection

The population routine `0x510D60` invokes `0x5111A0` before collecting participants. For each non-user-controlled team, that path calls `0x409B50`, which enters the AI lineup routine `0x409C90`.

The original order is therefore:

1. AI/user lineup state is established on runtime DBRPlayers;
2. starters receive the on-field flag and substitutes receive the substitute-available flag;
3. `0x510CD0` filters the ordered team roster using those two flags;
4. `0x62AC90` initializes MatchCalculator per-player state from the resulting participant arrays.

This identifies `0x409C90` as the remaining major bridge between club runtime state and an autonomously prepared reconstructed match.

### `0x62AC90` participant-state initialization

The MatchCalculator layout visible from this path includes:

- side 0 team pointer at `+0x0000`;
- side 0 participant array at `+0x0004`, count at `+0x05A4`;
- side 1 team pointer at `+0x05B0`;
- side 1 participant array at `+0x05B4`, count at `+0x0B54`.

`0x62AC90` copies each participant's runtime Condition byte `DBRPlayer+0x77` into its per-match state and resets score/segment state. Calls to `0x417A40/0x417A50` in this initializer set `DBRPlayer+0x18F`; they are **not** the starter/substitute flags and should not be conflated with `+0x14 bit 4/5`.

## Team-selection status and AI selection routines

### First-team / reserve selection state

**Confirmed.**

Player selection state is represented by four mutually exclusive bits plus the unselected state:

- first-team XI / on-field: player `+0x14` bit 4, status code 4;
- first-team substitute: player `+0x14` bit 5, status code 3;
- reserve-team XI: player `+0x174` bit 0, status code 2;
- reserve-team substitute: player `+0x174` bit 1, status code 1;
- none selected: status code 0.

`0x4218E0` returns those status codes in the priority above and `0x421950` dispatches status setters. Reserve-XI transitions use `0x418220` to swap the current `+0x03/+0x04` position state with reserve-stored bytes `+0x152/+0x153`.

`0x408500(team)` returns the competition-dependent first-team substitute quota, with a fallback of 5 when no competition context is available.

### Position metadata used by selection

**Confirmed from Static.dat plus executable consumers.**

The Position table's final bytes are now decoded:

- disk record `+5`: position ordering key;
- disk record `+6`: broad position category.

Categories are:

- 0 defender: RB/LB/CB/SW/RWB/LWB;
- 1 midfielder: ANC/DM/RM/LM/CM/RW/LW/AM;
- 2 attacker: CF/ST;
- 3 goalkeeper: GK;
- 255: None/RF/LF in the shipped data.

The loaded runtime helper `0x4EA310` returns this broad category. The status sort uses the ordering key.

### Simple selector `0x40AF60`

**Confirmed core behavior.**

Argument 2 is the first-team formation index. Argument 3 enables substitute filling and argument 4 is the requested first-team substitute count. Argument 5 equal to 1 commits the chosen XI/status mutations. Argument 7 controls whether the chosen formation is written back to team `+0x1D8`. Arguments 1 and 6 are unused by the recovered body.

For each of the 11 formation slots, the selector first scans the roster in order and considers unused players whose current role or one of their three preferred roles matches the formation slot. The player with the strictly greatest `0x41C7E0(player, required_role)` rating is retained; zero ratings are treated as one. Ties preserve the first roster entry.

A second pass fills any still-empty formation slot from all unused players using the same role rating, allowing out-of-position choices.

When commit mode is 1 it clears prior selection state across the roster, assigns each chosen player's exact formation role and formation auxiliary byte, marks the player first-team active, and accumulates `0x41E1D0` into team `+0x34`.

If substitute filling is enabled, the routine then walks the roster from first to last and marks the first still-nonactive players as first-team substitutes until the requested quota is exhausted. This simple path does not separately optimize substitute ability.

### Competitive selector `0x409C90`

**Confirmed selection structure; several helper-field semantic names remain intentionally generic.**

The seven stack arguments are structurally:

1. availability/context parameter passed to the full player-availability helper;
2. roster count;
3. first-team formation index;
4. reserve-team formation index;
5. first-team substitute quota;
6. commit-selection flag;
7. a restriction-enforcement flag that the AI can relax and retry if no XI can be completed.

The first XI is built in two stages. Every selected-player comparison uses:

```
trunc_toward_zero(
    role_rating(player, formation_role) * form_multiplier(player)
)
```

with zero coerced to one and strict-greater comparison, so roster order wins ties.

Stage 1 processes the eleven formation slots in order and considers only unused, available players whose **preferred-position triplet** contains that slot's required role. Stage 2 revisits unfilled slots and chooses the best unused available player regardless of preferred-position match.

This path applies the original availability/status filters and a separate player-restriction counter/limit path before accepting a candidate. The restriction is stored in player `+0x14` bit 11 and bounded through `0x407DF0(team)`. The executable contains the database class/source identity `CNonEUPlayer` / `NonEUPlayer.cpp`, making a non-EU-player restriction the leading interpretation, but the bit's complete lifecycle should be traced before the reconstruction exposes that semantic name as final. If an AI-controlled team cannot complete the XI while argument 7 is 1, the routine retries with that restriction flag cleared.

In commit mode, chosen XI players receive the formation role and auxiliary byte and are marked first-team active. The team-strength/rating aggregate written to team `+0x34` uses `0x41E1D0 * Form` on this competitive path.

#### Competitive bench construction

The remaining first-team substitute quota is filled in this exact sequence, each ranked pass choosing the strictly greatest `0x41E1D0 * Form` value among unused, available players of the requested broad category:

1. category 1, midfielder;
2. category 2, attacker;
3. category 0, defender;
4. category 3, goalkeeper.

Each pass can add at most one player. Any remaining substitute slots are then filled by roster order from unused/available players whose category is **not 3**, preventing additional goalkeepers in the overflow phase.

After first-team selection, non-special team types call `0x40AB40` with the reserve formation and commit flag to construct the reserve XI and its fixed three-player reserve bench.
## AI lineup core `0x409C90` — formation slots and bench groups

**Confirmed from direct disassembly plus the canonical Static.dat.**

The AI lineup routine uses a built-in formation table at runtime address `0x876CB8`. Initializer `0x50C3B0` writes exactly **21 formations x 11 slots x 8 bytes**.

Each slot contains:

- dword `+0x00`: target runtime role code;
- low byte of dword `+0x04`: auxiliary position-state value later copied through `0x4EA350` into position-state `+0x04`.

The exact 21 role/aux templates are:

```text
0 : 19/1 19/0 11/0 10/0 12/1 12/0 4/1 4/0 3/0 2/0 1/0
1 : 19/1 19/0 14/0 13/0 9/1 9/0 4/1 4/0 3/0 2/0 1/0
2 : 18/1 18/0 11/0 10/0 9/1 9/0 4/1 4/0 3/0 2/0 1/0
3 : 19/1 19/0 15/0 12/1 12/0 7/0 6/0 4/2 4/1 4/0 1/0
4 : 19/1 19/0 18/0 12/1 12/0 7/0 6/0 4/2 4/1 4/0 1/0
5 : 18/1 18/0 12/1 12/0 9/0 7/0 6/0 4/2 4/1 4/0 1/0
6 : 19/1 19/0 18/0 11/0 10/0 9/1 9/0 4/2 4/1 4/0 1/0
7 : 19/1 19/0 18/0 14/0 13/0 12/1 12/0 4/2 4/1 4/0 1/0
8 : 19/0 18/1 18/0 11/0 10/0 9/1 9/0 4/2 4/1 4/0 1/0
9 : 19/1 19/0 14/0 13/0 12/1 12/0 9/0 4/2 4/1 4/0 1/0
10: 19/1 19/0 18/0 14/0 13/0 9/1 9/0 4/2 4/1 4/0 1/0
11: 19/1 19/0 15/0 11/0 10/0 9/1 9/0 4/2 4/1 4/0 1/0
12: 19/1 19/0 18/0 12/1 12/0 8/0 7/0 6/0 4/1 4/0 1/0
13: 19/1 19/0 18/0 15/1 15/0 12/0 7/0 6/0 4/1 4/0 1/0
14: 19/0 14/0 13/0 12/1 12/0 8/0 4/1 4/0 3/0 2/0 1/0
15: 18/0 15/1 15/0 11/0 10/0 8/0 4/1 4/0 3/0 2/0 1/0
16: 19/1 19/0 18/0 15/1 15/0 14/0 13/0 9/0 4/1 4/0 1/0
17: 18/0 15/1 15/0 11/0 10/0 5/0 4/1 4/0 3/0 2/0 1/0
18: 19/1 19/0 14/0 13/0 12/1 12/0 4/1 4/0 3/0 2/0 1/0
19: 19/1 19/0 15/0 12/1 12/0 7/0 6/0 5/0 4/1 4/0 1/0
20: 19/0 18/1 18/0 15/0 12/1 12/0 4/1 4/0 3/0 2/0 1/0
```

These are numeric original templates; formation display names have not yet been attached to IDs and should not be guessed.

### Starter selection is two-pass

For each of the eleven target slots, the first pass considers only unselected/eligible players whose one of three stored preferred positions exactly matches the target role. Among those candidates it chooses the strictly highest:

```
trunc_toward_zero(
    role_rating(player, target_role) * form_multiplier(player)
)
```

with zero scores forced to one.

After the first pass has attempted all eleven slots, a second pass revisits any still-unfilled slot. That fallback drops the exact-preferred-position requirement and chooses the best remaining eligible player by the same target-role rating x Form score.

When normal assignment mode is enabled, the chosen starter receives:

- target role -> position-state `+0x03` through `0x4EA330`;
- slot auxiliary value -> low nibble of position-state `+0x04` through `0x4EA350`;
- on-field flag through `0x4182F0`.

### Static position group bytes and substitute phases

Each 7-byte Static.dat position definition contains two bytes after the fields previously parsed by the clean-room loader. The final byte maps directly to the category returned by runtime helper `0x4EA310`.

For the normal runtime roles:

- category 0 = defender;
- category 1 = midfielder;
- category 2 = forward;
- category 3 = goalkeeper;
- category 255 = unclassified/not used by this grouping.

Static position IDs are one-based relative to the zero-based runtime roles. The canonical records show:

- goalkeeper role 1 -> category 3;
- roles 2..7 -> category 0;
- roles 8..15 -> category 1;
- roles 18..19 -> category 2;
- roles 16..17 -> category 255.

The last point independently agrees with roles 16/17 taking the zero branch in `0x41C7E0` and not appearing in the 21 built-in formation templates.

After starters, `0x409C90` attempts substitute selection in category order:

1. midfielder (1);
2. forward (2);
3. defender (0);
4. goalkeeper (3).

Each phase chooses the highest eligible remaining player using the current-role rating helper `0x41E1D0` multiplied by Form, marks the player substitute-available through `0x4182C0`, and decrements the remaining substitute count.

A final fill loop then consumes any still-open substitute places from remaining eligible players but excludes category 3, preventing additional goalkeepers through that fallback.
## Match-day runtime defaults: Form, Condition, and position state

**Confirmed from the canonical executable.**

Several values that were previously treated as caller-supplied unknowns have exact DBRPlayer initialization behavior.

### Form

DBRPlayer initialization writes:

```
DBRPlayer +0x192 = 2
```

at `0x41B330`.

This is the neutral member of the already-recovered five-state Form scale 0..4. Therefore a newly initialized runtime player begins at **Form state 2 / Normal**, not at an unknown value.

The later Form transition routine `0x41B870` mutates this byte within 0..4 using the named tuning globals `FormChangeProb`, `InFormChangeProb`, `OutOfFormChangeProb`, and `FormIncreaseProb`. Match and lineup code consume the current runtime value through `0x41B970`.

### Condition

DBRPlayer initialization at `0x417930` writes:

```
DBRPlayer +0x77 = 0x50
```

so initial runtime **Condition = 80**.

Subsequent training/rest/match paths mutate the same byte; MatchCalculator `0x62AC90` copies its current value into per-match state. Thus the authoritative match input is the live runtime Condition byte, with 80 as its proven initialization value.

### Position-state constructor

The six-byte position state referenced from DBRPlayer `+0x248` is initialized by `0x4EA2D0`.

The constructor:

1. copies the three stored preferred/runtime role bytes into position-state `+0x00..+0x02`;
2. calls `0x4EA370`, which copies preferred role 0 into current assigned role `+0x03` and clears the low nibble of auxiliary byte `+0x04`;
3. calls `0x4EA3B0`.

`0x4EA3B0` performs:

```
position_state[5] = (position_state[5] & 0xEA) | 0x0A
```

For the low five bits returned by `0x4EA3E0`, this forces:

```
balance_position_code = 10
```

regardless of the previous low-five-bit contents.

Therefore the clean-room startup state can now initialize:

- current assigned role = first preferred role;
- auxiliary position code low nibble = 0;
- separate balance-position code low five bits = **10**.

AI formation selection later overwrites assigned role `+0x03` and auxiliary `+0x04` for starters, but does not overwrite the distinct `+0x05` balance code. Substitution likewise copies `+0x03/+0x04` but not `+0x05`.
## AI lineup availability flags at DBRPlayer +0x14

**Confirmed / partially named from executable lifecycle.**

The full competitive availability helper `0x418050(player, team_id, context)` begins by marking a player unavailable when any of the low three bits of `DBRPlayer+0x14` are set, or when the player's normal club ID at `+0x10` differs from the requested team.

The low bits now separate as follows:

- **bit 0 / 0x01 = injured**.
  - getter `0x417FF0`;
  - injury creation paths `0x41A5B0` and `0x41A670` refuse to create a second injury when this bit is already set;
  - those paths allocate the player's injury-state object at `+0x24C` and dispatch through `0x605F90` into the named injury-probability system;
  - MatchCalculator injury processing reaches `0x41A5B0` directly.
- **bit 1 / 0x02 = banned/suspended**.
  - it is part of the simpler global-unavailability test `0x418130`, which checks `+0x14 & 3`;
  - post-match routine `0x419680` sets bit 1 when either of the two suspension countdown fields (`+0x13E` / `+0x13B`) is active under its competition/date conditions;
  - post-match maintenance `0x419490` clears bit 1 before decrementing the relevant suspension countdown for the match just processed, then subsequent selection-state refresh can set it again while suspension remains.
- **bit 2 / 0x04 = separate selection-exclusion flag; higher-level name unresolved**.
  - setter `0x418010`, clearer `0x418030`;
  - it participates in `0x418050` but not in the simpler `0x418130` injury/suspension check;
  - it is set and cleared by a separate Club.cpp roster-selection/reordering path around `0x50F4D0..0x50FA58`.
  - It must **not** yet be labeled cup-tied: the executable has a distinct persistent `CCupTiedPlayer` database class and separate competition-player lookup path.

After the low-bit/club checks, `0x418050` applies competition/context-specific registration checks through `0x4F8E40` / `0x419350` and a separate bit-11/date-backed player restriction. Those context checks remain outside the clean-room generic availability primitive until their persistent database semantics are fully named.

This means the core AI lineup eligibility bridge can safely internalize injury and suspension immediately while keeping bit 2 and competition registration as explicit neutral exclusion inputs.
## Cup-tied persistence record and competition lookup

**Confirmed from RTTI, constructor, serializer and lookup code in the canonical executable.**

The executable contains a distinct persistence class named `CCupTiedPlayer` (`CupTiedPlayer.cpp`). Its record constructor at `0x4E95D0` stores two 16-bit identifiers:

- record `+0x04`: player ID;
- record `+0x06`: club/team ID for which that player is tied/registered.

Collection helper `0x4E96E0(collection, player_id)` searches by the player ID field.

The actual cup-tied predicate is `0x4E9710(collection, player_id, team_id)`:

```
record = find_by_player_id(collection, player_id)
if record is None:
    return false
if record.club_id == team_id:
    return false
return true
```

Thus a player with no record is not cup-tied, and a player whose record belongs to the team trying to field him is not cup-tied. A record for the same player tied to a **different** club makes the lookup return true.

The competition/context helper `0x4F8E40` is a thin wrapper around this exact check. It passes team ID and player ID into the `CCupTiedPlayer` collection stored at context object `+0x48`.

This independently proves that `DBRPlayer+0x14 bit 2` is **not** the cup-tied state. Cup ties are represented by their own persistent competition collection and consulted through `0x4F8E40`.

### Placement inside full availability helper `0x418050`

After the base club/low-three-bit exclusions, `0x418050` may enter extra competition-registration checks when an additional DBRPlayer flag at `+0x174 bit 8` is set. That flag initializes clear and can be set by team-assignment/new-player paths, but its higher-level semantic name is not yet proven.

Within those context checks, `0x4F8E40` supplies the confirmed cup-tied test. Another competition-specific branch uses `0x419350`; that branch remains unresolved and should not be folded into the generic clean-room availability predicate yet.
## Manager-driven first-team formation source

**Confirmed from the canonical executable and Master.dat serializer.**

Wrapper `0x409B50` chooses the first-team formation passed into competitive selector `0x409C90`. The source is the club manager runtime record at the club's manager index (`team+0x40`) in the 64-byte runtime manager array.

The three one-byte manager formation fields are:

- runtime manager `+0x20`;
- runtime manager `+0x21`;
- runtime manager `+0x22`.

The Master.dat manager serializer `0x414910` proves that these bytes are persisted directly and sequentially. Because the preceding persisted fields consume 24 bytes, they correspond exactly to packed manager-record offsets:

- Master.dat manager `+24` -> runtime `+0x20`;
- Master.dat manager `+25` -> runtime `+0x21`;
- Master.dat manager `+26` -> runtime `+0x22`.

Across all 1,612 shipped manager records, +24 and +26 are always formation IDs in 0..20; +25 is likewise 0..20 except for one `0xFF` record. This independently matches the 21-entry formation table.

### Selection-class mapping in `0x409B50`

When the team is in the normal manager-driven path, `0x409500(team)` returns a selection class. `0x409B50` maps that class to the manager fields exactly as follows:

```text
class 0 -> manager +0x20
class 1 -> manager +0x22
class 2 -> manager +0x20
class 3 -> manager +0x21
```

So +0x20 is the default formation for classes 0 and 2, while classes 1 and 3 select the two alternates.

The higher-level football labels for classes 1/2/3 are not yet assigned. `0x409500` clearly derives them from match/opponent context, relative ratings and named game-state tuning such as `GSHomeValue`, `GSAwayValue`, `GSRatingDiv`, cup-stage biases and attack/defence thresholds, but that routine is still being mapped. Reconstruction should therefore expose the numeric class mapping without guessing labels such as attacking/defensive until the remaining branches are fully traced.

After selection, `0x409B50` writes the chosen first-team formation back to team `+0x1D8`.

### Competitive selector call arguments from normal match setup

The normal match population path `0x5111A0` now fixes the argument wiring into `0x409B50 -> 0x409C90`.

`0x409C90` receives, in order:

1. availability/context pointer returned by `0x511170`;
2. team roster count;
3. manager-derived first-team formation ID;
4. stored reserve formation ID from team `+0x1DC`;
5. the match/competition substitute quota;
6. commit flag = 1;
7. restriction-enforcement flag = 1.

The substitute quota is the same field returned by dedicated accessor `0x408500(team)`: it resolves the team's current match, dereferences the match competition/context pointer at `+0x4C`, and returns context `+0x1C`. When no current match/context exists, `0x408500` returns the fallback value **5**.

Thus the remaining autonomous team-preparation gap is no longer where formation/quota enter the selector, but how `0x409500` derives its numeric formation-selection class and how the competition object initializes its `+0x1C` substitute-count field.
## Non-EU lineup restriction and AI retry

**Confirmed from RTTI, player initialization, competition records and `0x409C90`.**

Player helper `0x41B490` returns `DBRPlayer+0x14 bit 11`. This bit is not merely a generic restriction marker.

The persistent record collection at global `0x876B30` creates records with vtable `0x7C89E8`. The vtable's MSVC RTTI Complete Object Locator points to type descriptor `0x81F548`, whose class name is exactly:

```text
.?AVCNonEUPlayer@@
```

The executable also embeds source identity `Database\\NonEUPlayer.cpp`.

When bit 11 is set, helper `0x41B4D0` looks the player ID up in this `CNonEUPlayer` collection and creates the record through `0x417A20` when missing. Therefore:

```
DBRPlayer +0x14 bit 11 = Non-EU player state
```

### Original startup derivation

Player startup routine `0x421CE0` calls `0x421760(player)`; when that predicate succeeds it calls `0x417A20`, setting the Non-EU bit and creating the persistent `CNonEUPlayer` record.

The exact `0x421760` country/nationality predicate is now localized but its two country metadata words and player `+0x6C` condition still require semantic naming before clean-room initialization should derive Non-EU automatically. Until that final mapping is completed, reconstruction may carry the proven Boolean state explicitly but must not invent nationality rules.

### Competition maximum

Global `0x876C50` is the runtime `DBRCompetition` array owned by `DBTCompetitions`:

- table vtable `0x7C9984` RTTI = `DBTCompetitions`;
- 64-byte record vtable `0x7C9998` RTTI = `DBRCompetition`.

Helper `0x407DF0(team)` resolves the team's current match competition and returns:

```
DBRCompetition +0x2B
```

or **11** when no competition context can be resolved.

The exact DBRCompetition binary reader `0x40F760` maps runtime `+0x2B` to packed Static.dat competition byte **+34**. The 193 shipped competition records contain only values:

```text
0, 3, 4, 5, 99
```

Premier League competition ID 0 has value **3**. This is therefore the exact competition maximum consulted for Non-EU lineup selection; 99 is effectively unrestricted under the original integer comparison.

### Selection and retry behavior

Throughout both XI and bench construction, a Non-EU candidate is rejected when:

```
selected_non_eu_count >= competition_non_eu_limit
```

The running count is incremented for a selected Non-EU player only while the restriction-enforcement flag is 1 and the team's country/context record enables that restriction path.

If the first XI cannot be completed, `0x409C90` reaches its failure path. It then performs exactly one retry when:

- the team is **not user controlled** (`0x4037B0(team)` is false); and
- the local restriction-enforcement flag is still 1.

The routine sets that flag to 0, resets its selection state, and jumps back to the start of XI construction. A second failure returns zero instead of retrying again.

This is the original AI escape hatch for a squad that cannot field eleven players under the Non-EU counting restriction. It is not a generic reconstruction fallback and should be reproduced only under those conditions.
## Exact startup derivation of player Non-EU state

**Confirmed from DBRClub/DBRCountry readers, Editor resources, Master.dat/Static.dat values and `0x421760`.**

The Non-EU Boolean is not arbitrary runtime state. Player startup `0x421CE0` calls `0x421760(player)`; when it returns true, `0x417A20` sets `DBRPlayer+0x14 bit 11` and ensures the persistent `CNonEUPlayer` record exists.

### Source fields

The player's current club/team country is runtime team `+0x14`. The DBRClub reader `0x4022D0` maps packed Master.dat club bytes `+12..+15` directly into this dword. The clean-room club record can therefore expose packed **club +12 uint32** as country ID.

Player runtime byte `DBRPlayer+0x6C` comes from packed Master.dat player **+96**. The shipped database uses only values 1 and 2. EA's bundled Editor player dialog labels this exact concept **EU Status**, with choices **EU** and **Non EU**. Executable behavior and shipped examples establish:

```text
+96 / runtime +0x6C == 1 -> Non-EU classification path is enabled
+96 / runtime +0x6C == 2 -> EU/exempt status; normal path does not mark Non-EU
```

For example, shipped Arsenal records for Christopher Wreh, Nwankwo Kanu, Oleg Luzhny, Lauren and Nelson Vivas carry value 1, while the English/French/German/Dutch/etc. players and several non-European players with EU/exempt status carry value 2.

Global `0x874BD8/0x874BE0` is the country table. Runtime records are 108-byte **DBRCountry** objects (RTTI `.?AVDBRCountry@@`). Country lookup helper `0x410E00` scans runtime `DBRCountry+0x0C`, which is packed Static.dat country **+6 uint32**, for the player's nationality ID.

The DBRCountry reader `0x410640` maps:
- packed country +14 uint16 -> runtime `+0x16`;
- packed country +16 uint16 -> runtime `+0x18`.

The shipped +14 values form the European/UEFA association set: zero outside Europe and a nonzero 1..50-style association index for European countries. Packed +16 is the narrower EU-status eligibility flag used by the normal Non-EU path: England, France, Germany, Italy, Spain, Norway, etc. have 1; Brazil, Argentina, USA, South Korea, etc. have 0.

### Exact predicate `0x421760`

Let:
- `club_country` = player's current team country ID;
- `eu_status_code` = player runtime +0x6C / Master.dat player +96;
- `country` = DBRCountry resolved by player nationality ID.

The executable is equivalent to:

```text
if club_country == 33:  # Germany in this database
    return country.european_index == 0

if eu_status_code == 1:
    if country lookup fails:
        return true
    return country.eu_status_flag == 0

return false
```

Country ID 33 is Germany in the shipped Static.dat. The Germany-specific branch therefore classifies non-European nationalities through the broader European/UEFA index and does not consult the player's +0x6C EU-status code.

For all other club countries, only players whose stored EU Status code is 1 enter classification; they are marked Non-EU when their nationality cannot be resolved or when the nationality country's packed +16 EU-status flag is zero.

This completes the startup derivation needed to initialize the clean-room `RuntimePlayer.non_eu` flag from original database data rather than defaulting every player to false.
## AI manager tactical packet sources

**Confirmed from DBRManager loading and pre-match packet builder `0x40D860`.**

For an AI-controlled team, the pre-match tactics packet does not read the live user-team tactical bytes directly. It resolves the club manager and reads runtime DBRManager bytes `+0x30..+0x33`, which map to packed Master.dat manager record bytes `+39..+42`.

The packet transforms them exactly as follows:

```text
strategy_code      = 0x4035E0(manager+0x30)
aggression_code    = floor((manager+0x31) / 6) & 0x0F
with_ball_code     = (manager+0x32) & 0x03
without_ball_code  = (manager+0x33) & 0x03
```

`0x4035E0` maps source values:

```text
0 -> 3
1 -> 2
2 -> 1
other -> 2
```

For a user-controlled team the same packet fields instead come from live team state:

- Play style `team+0x1B4` through `0x4035E0`;
- Aggression `team+0x1B7` directly;
- With Ball style `team+0x1B6` low two bits;
- Without Ball style `team+0x1B5` low two bits.

The team constructor initializes these live fields to:

```text
Play style        +0x1B4 = 1
Without Ball      +0x1B5 = 0
With Ball         +0x1B6 = 0
Aggression        +0x1B7 = 5
```

Canonical manager raw examples include Ferguson `3,80,2,3` and Wenger `2,90,4,3`. Because source value 4 is masked to zero in the packet, the persisted bytes must remain distinguished from final MatchCalculator tactic indices until the concrete TacticsCommand visitor is fully mapped.

The clean-room reconstruction now exposes these as neutral AI tactical source values and reproduces the exact packet transforms without prematurely assigning downstream semantics.
## Exact human Team Orders priority storage

**Confirmed from accessors `0x40D620/0x40D650` and MatchCalculator consumers.**

The four human Team Orders categories are stored on the user-team companion/profile returned by `0x403850(team)`. This helper returns null for AI-controlled teams, so these explicit lists are user-team state rather than generic AI tactical state.

For category index `c`:

```text
count(c)      = byte  [profile + 0x206 + c]
list_ptr(c)   = dword [profile + 0x660 + 4*c]
player_id(i)  = uint16[list_ptr(c) + 2*i]
```

The categories are exactly:

- 0 = captain priority;
- 1 = penalty-taker priority;
- 2 = corner-taker priority;
- 3 = free-kick-taker priority.

### Category 0 — captain

Team helper `0x408560`, already consumed by the human team-strength path, scans category 0 in stored order. Each listed player ID is resolved to the global DBRPlayer array and checked with active/on-field predicate `0x417F50(player, team)`. The first active listed player is returned. If no listed active player exists, the helper returns null; there is no carrier fallback for captaincy.

### Category 1 — penalties

Selector `0x631F10` resolves the relevant team, confirms it has a user companion/profile, then scans category 1 in stored order with the same `0x417F50` active-player test. The first active listed player is returned. If the list is empty or all listed players are inactive, it falls back to `0x62B780`.

The same category is also used by the pre-match participant-ordering path around `0x631A8C..0x631B40`, independently confirming category 1 as the penalty priority list.

### Category 2 — corners

Selector `0x632280` scans category 2 in stored order, requires `0x417F50`, returns the first active listed player, and falls back to `0x62B780` when none is usable.

### Category 3 — free kicks

Selector `0x631FB0` scans category 3 in stored order, requires `0x417F50`, returns the first active listed player, and falls back to `0x62B780` when none is usable.

For AI-controlled teams `0x403850` returns null, so the category-list branch is skipped. Existing reconstructed AI behavior remains separate: penalties use the calculator carrier fallback, while corners/free kicks use the recovered best-effective-Set-Piece selector.

The nearby 10-dword team region beginning at `team+0x178`, manipulated by `0x408530`, is therefore **not** the Team Orders priority storage and should not be labeled as such.

The clean-room `TeamOrderPriorities` model now mirrors these four categories while remaining data-free.
## AI formation strategy classifier `0x409500`

**Confirmed from direct disassembly and the original tuning-key loader.**

The numerical selection classes previously left unnamed are now resolved by the executable's own tuning vocabulary and by their manager-formation consumers.

The final thresholds are stored in globals initialized from:

```text
GSDefPerc = -3
GSAttPerc =  3
```

and `0x409500` returns:

```text
score <= GSDefPerc       -> class 3 -> manager +0x21 -> defensive formation
GSDefPerc < score < GSAttPerc
                         -> class 2 -> manager +0x20 -> normal/default formation
score >= GSAttPerc       -> class 1 -> manager +0x22 -> attacking formation
no usable match context  -> class 0 -> manager +0x20 -> normal/default formation
```

This is independently consistent with the dominant shipped manager triple `(0,2,1)`: formation 2 is the more cautious variant of formation 0, while formation 1 is the more attacking variant. Other common manager triples follow the same pattern.

### Exact tuning names and defaults used by the score

The contiguous loader around `0x4FD9FD..0x4FDDA8` names the relevant globals explicitly:

```text
GSDefPerc                         -3
GSAttPerc                          3
GSHomeValue                        1
GSAwayValue                       -1
GSRatingDiv                    10000
GSCupFinalBias                     3
GSCupSemiFinalBias                 2
GSCupQuarterFinalBias              1
GSPrecedenceDiv                    3
GSGoForWinLeagueBias               2
GSGoForPromotionBias               1
GSGoForPromotionPlayoffBias        runtime/tuning value
GSGoForAvoidRelegationBias         1
GSGoForAvoidRelegationPlayoffBias  3
GSStartWorryingAboutLeaguePos      8
GSReallyWorryingAboutLeaguePos     4
```

The promotion-playoff bias lives at global `0x877448` and is populated from its named tuning key; its pre-loader binary default is not stored in the initialized .data block, so reconstruction should not invent a default value when no tuning source is available.

### Home/away and relative squad-rating pressure

The match object identifies one side as the home side. `0x409500` begins the strategy score with:

- home -> `GSHomeValue`;
- away -> `GSAwayValue`.

Team rating helper `0x409900` walks at most the first eleven IDs in the team's ordered roster and sums `0x41E1D0(player)`, the already-recovered best-preferred-position role rating.

It computes:

```text
rating_delta = trunc_toward_zero(
    (current_rating - opponent_rating) / GSRatingDiv
)
```

and converts its absolute magnitude to a pressure step:

```text
abs(delta) <   5 -> 0
>= 5            -> 1
>= 10           -> 2
>= 20           -> 3
>= 50           -> 4
>= 100          -> 5
```

A positive delta (current team stronger) **subtracts** the step, pushing toward the defensive/protective formation bucket. A zero/negative delta adds the step, so a sufficiently weaker team is pushed toward the attacking bucket.

With the analyzed release's default `GSRatingDiv=10000`, ordinary 0..99 role-rating sums make this component effectively dormant unless tuning overrides the divisor. The arithmetic is nevertheless reconstructed exactly.

### Aggregate/score deficit boost

For competition/context type 2, `0x409500` computes the relevant current-team aggregate deficit through `0x513ED0/0x513F00`. Only a positive deficit adds attacking pressure:

```text
1 goal behind -> +2
2 goals behind -> +5
3 goals behind -> +6
4+ behind      -> +7
level/ahead    -> +0
```

This provides direct behavioral confirmation that increasing strategy score means increasing pressure toward the attacking manager formation.

### Cup-round context `0x409680`

For cup-style context, `0x409680` adds:

```text
final         -> GSCupFinalBias
semi-final    -> GSCupSemiFinalBias
quarter-final -> GSCupQuarterFinalBias
other round   -> 0
```

plus:

```text
trunc_toward_zero((competition_precedence + 12) / GSPrecedenceDiv)
```

using the default precedence divisor 3.

### Late-season league objective pressure

The non-cup branch asks the competition helpers for the team's remaining matches and five possible objective gaps:

1. win league;
2. promotion;
3. promotion playoff;
4. avoid relegation;
5. avoid relegation playoff.

No league-position pressure is applied while more than `GSStartWorryingAboutLeaguePos` matches remain (default 8).

For the first applicable objective whose positive points gap is mathematically reachable at **less than 3.0 points per remaining match**, the executable computes approximately:

```text
pressure = trunc(points_gap / matches_remaining + 0.499) + objective_base_bias
```

If more than `GSReallyWorryingAboutLeaguePos` matches remain (default 4), that pressure is halved with signed truncation toward zero. In the final four matches it is used at full value.

The clean-room helpers in `match_team_setup.py` now reproduce the final class bucket, relative-rating step, aggregate-deficit step, cup-round bias and common late-season objective arithmetic. The remaining higher-level task is to reproduce the exact competition helper that decides which objective gap is active for a given club/table state.
## Exact competition substitute quota source

**Confirmed from RTTI, DBRCompetition deserialization and runtime Competition construction.**

The object stored at the current match's `+0x4C` pointer is a runtime `Competition` object (MSVC RTTI `.?AVCompetition@@`), not a Round object. Team helper `0x408500(team)` returns:

```text
current_match->competition_context->+0x1C
```

and falls back to **5** when no current match/context can be resolved.

The value's source is now exact:

1. `DBRCompetition` binary reader `0x40F760` reads packed Static.dat competition byte **+17** into runtime `DBRCompetition+0x18`;
2. `Competition` constructor `0x4F3BE0` sign-extends `DBRCompetition+0x18` and stores it at `Competition+0x1C`;
3. `0x408500` returns that dword unchanged as the first-team substitute quota passed to `0x409C90`.

Across all 193 shipped competition records, packed byte +17 contains only:

```text
0, 3, 5, 7
```

The shipped Premier League, competition ID 0, stores **5**.

This removes the last unknown source for the bench-size argument in the normal AI lineup path. The clean-room `CompetitionDefinition` now exposes `substitute_quota` directly from Static.dat +17.

## Tactics command conversion into MatchCalculator type-11 records

**Confirmed from command RTTI/vtables, ConversionVisitor dispatch, compact-record constructors and serializer `0x6336E0`.**

The front-end tactical command hierarchy is converted into MatchCalculator linked records through `ConversionVisitor` (vtable `0x7D7FC4`). The exact typed-command dispatch is:

| Typed command | Visitor slot | ConversionVisitor handler | Type-11 subcommand |
|---|---:|---:|---:|
| StrategyCommand | +0x0C | `0x634400` | 0 |
| StyleCommand | +0x08 | `0x634480` | 1 |
| DefensiveStyleCommand | +0x1C | `0x6341F0` | 2 |
| FormationCommand | +0x18 | `0x634270` | 3 |
| AggressionCommand | +0x20 | `0x634170` | 4 |
| PositionCommand | +0x10 | `0x634370` | 5 |
| OrdersCommand | +0x14 | `0x6342F0` | separate family 12 |
| SubstitutionCommand | remaining visitor slot | `0x634500` | separate substitution form |

For the five simple tactical commands, the visitor reads the command value through getter `0x6335B0`, then constructs a 0x38-byte compact record using:

- Strategy -> `0x632A60`
- Style -> `0x632A90`
- DefensiveStyle -> `0x632A00`
- Formation -> `0x632A30`
- Aggression -> `0x6329D0`
- Position -> `0x632AF0`

The shared constructor `0x6329A0` sets:

```text
record +0x28 = 11       # MatchCalculator command-record family
record +0x08 = subcommand kind
record +0x2C = primary command value
```

and inherits the generic time/order/team fields from the base record constructor chain.

### Independent serializer confirmation

Type-11 serializer `0x633A20` switches on `record+0x08` and uses payload widths consistent with the command value domains:

- subcommand 0 Strategy: payload `+0x2C` serialized in 3 bits;
- subcommand 1 Style: payload in 3 bits;
- subcommand 2 DefensiveStyle: payload in 2 bits;
- subcommand 3 Formation: payload in 5 bits;
- subcommand 4 Aggression: payload in 4 bits;
- subcommand 5 Position: serializes additional player/position fields (`+0x0C`, `+0x2C`, `+0x24`) rather than only a scalar.

The event-family serializer's outer switch routes `record+0x28 == 11` specifically to `0x633A20`, independently confirming that these are **type-11 command records** rather than direct calls that mutate team tactical bytes.

### Important architectural boundary

`0x62FD90` does **not** apply these commands. It inserts/copies the 0x38-byte compact record into the MatchCalculator linked list in time/order sequence. Therefore the ConversionVisitor path should not be modeled as immediately writing team `+0x1B4..+0x1B7`.

The remaining task is to find the later consumer that processes type-11 records and applies subcommands 0..5 to live calculator/team tactical state. That consumer is the authoritative bridge needed before manager packet values can be equated with final MatchCalculator tactic indices.
## 0x40D860 is MatchEngine-side initial team data, not backend tactical state

**Confirmed from the high-level match setup at 0x510F06..0x510F28, decoder 0x533B20/0x533B70 and the MatchEngine initialization path at 0x533270 -> 0x6C1D00/0x6C1D30.**

The 0x3C-byte block built by `0x40D860(team)` is stored on the MatchCalculator/match-record object at:

- side 0: `match+0x5A8`;
- side 1: `match+0xB58`.

Those fields are later decoded by `0x533B20 -> 0x533B70` while the game is preparing the external MatchEngine structures. The caller at `0x533270` passes the decoded side data into routines `0x6C1D00/0x6C1D30` in the executable region associated with the embedded source identity:

```text
D:\Projects\FM2001\Libraries\MatchEngine\MatchEngine.cpp
```

Therefore the previously reconstructed manager/user compact tactical fields are **MatchEngine-side initial team data**. They must not be equated with the live DBRTeam tactical bytes consumed by the backend MatchCalculator strength routines.

### Exact packed layout used by 0x40D860

The first dword contains:

```text
bits  0..7   formation ID (team+0x1D8)
bits  8..9   strategy code
bits 10..13  packed aggression source
bits 14..15  With Ball code
bits 16..17  Without Ball code
```

For user-controlled teams the strategy/aggression/style inputs originate from live team tactical state. For AI teams they originate from the manager tactical source bytes already mapped at DBRManager +0x30..+0x33.

The remainder contains up to 18 ordered-roster player position-state bytes:

```text
packet +0x04+i  = 0x4EA3E0(player position state)  # separate balance-position code
packet +0x16+i  = 0x4EA3C0(player position state)  # assigned role
packet +0x28+i  = 0x4EA3D0(player position state)  # auxiliary position byte
```

### MatchEngine decoder 0x533B70

The decoder expands the compact side block into the MatchEngine-facing structure:

```text
out +0x00 = formation ID
out +0x04 = strategy bits 8..9
out +0x08 = With Ball bits 14..15
out +0x0C = Without Ball bits 16..17
out +0x10 = bits 12..13 of the packed aggression nibble
```

It also expands the three per-player byte arrays into dword-spaced MatchEngine arrays for each side participant.

The fact that the MatchEngine decoder retains only bits 12..13 of the packed four-bit aggression source is another reason not to reinterpret the compact manager packet as the backend's live 0..9 DBRTeam Aggression value.

### Backend distinction

The recovered backend strength builders still read the live team object directly:

- `0x62F140` indexes attack coefficients from `team+0x1B6`;
- `0x62F3E0` indexes defence coefficients from `team+0x1B5`;
- the human-team aggression multiplier reads `team+0x1B7`.

This establishes two distinct layers:

1. DBRTeam/live football-management tactical state used by the backend calculator;
2. the compact `0x40D860` snapshot used to initialize MatchEngine/presentation-side team data.

The outstanding tactical question is consequently narrower: determine how live team state is mutated when tactical commands occur and what role the type-11 MatchCalculator command records play in replay/presentation synchronization. Do not use the 0x40D860 AI manager packet as a substitute for live backend tactical state.
## Exact CullingVisitor command-batch behavior

**Confirmed from RTTI, vtable `0x7D7FEC`, constructor `0x634580`, and all visitor handlers.**

The first visitor run over a submitted tactical-command batch is the original class:

```text
CullingVisitor
```

Its vtable has the same typed-command slot ordering as `ConversionVisitor`:

| Visitor slot | Command | CullingVisitor handler |
|---|---|---:|
| +0x04 | SubstitutionCommand | `0x634890` |
| +0x08 | StyleCommand | `0x634830` |
| +0x0C | StrategyCommand | `0x6347D0` |
| +0x10 | PositionCommand | `0x634760` |
| +0x14 | OrdersCommand | `0x6346F0` |
| +0x18 | FormationCommand | `0x634690` |
| +0x1C | DefensiveStyleCommand | `0x634630` |
| +0x20 | AggressionCommand | `0x6345D0` |

The constructor initializes five scalar seen-flags at object bytes `+0x08..+0x0C` and two 18-byte per-slot seen arrays at `+0x0D..+0x1E` and `+0x1F..+0x30`.

The scalar mapping is exact:

```text
+0x08 Aggression
+0x09 DefensiveStyle
+0x0A Formation
+0x0B Strategy
+0x0C Style
```

For each of those five command classes, the first command encountered is appended to the culled-output list and its flag is set. Later commands of the same class in the same batch are skipped.

`OrdersCommand` calls the generic primary-value getter `0x6335B0` and uses that value as an index into the 18-byte array beginning at `CullingVisitor+0x0D`. Thus the first Orders command for each of the 18 command slots is retained and later Orders commands for the same slot are culled.

`PositionCommand` uses the same primary-value getter as an index into the second 18-byte array beginning at `+0x1F`, again retaining only the first command for each slot.

`SubstitutionCommand` handler `0x634890` does not consult a seen flag and always appends its command pointer.

Therefore the command submission pipeline is:

```text
typed command list
    -> CullingVisitor
       - first scalar tactic command per category
       - first Position/Orders command per 18 player slots
       - all substitutions
    -> ConversionVisitor
    -> compact MatchCalculator timeline records
```

This culling stage is not a live tactical-state applier; it only builds the filtered command list that the following ConversionVisitor serializes into MatchCalculator record families.
## Backend DBRTeam tactical state: exact write-site audit

**Confirmed by a whole-executable audit of byte writes to the four live DBRTeam tactical fields, together with their already-mapped MatchCalculator consumers.**

The live backend fields are:

```text
team +0x1B4  Play style
team +0x1B5  Without Ball / defensive style
team +0x1B6  With Ball / attacking style
team +0x1B7  Aggression
```

For genuine DBRTeam instances, the executable has only three classes of writes to these fields:

1. **team construction/default initialization**;
2. **team-object copy/state transfer**, which preserves an already-existing value;
3. **the user tactical UI/controller**.

No separate AI-manager initialization or AI tactical-decision path writes these four DBRTeam bytes.

### Exact fresh-team defaults

The DBRTeam constructor initializes:

```text
+0x1B4 Play style        = 1  # Normal
+0x1B5 Without Ball      = 0  # Normal
+0x1B6 With Ball         = 0  # Normal
+0x1B7 Aggression        = 5
```

Relevant constructor writes are `0x403777`, `0x403737`, `0x40373D`, and `0x40377E`.

### Exact copy path

The team copy/state-transfer routine at `0x40C2AD..0x40C2D7` copies all four bytes verbatim from one DBRTeam object to another:

```text
source +0x1B4 -> destination +0x1B4
source +0x1B5 -> destination +0x1B5
source +0x1B6 -> destination +0x1B6
source +0x1B7 -> destination +0x1B7
```

Therefore a runtime team can preserve non-default values that were already present; the conclusion below applies to the normal fresh AI-team path, not to an arbitrarily copied/mutated object.

### User tactical-control writes

The tactical UI handler around `0x4D6770` resolves the currently user-controlled team and performs the only normal direct gameplay mutations found for these fields.

Play style:

```text
0x4D6DCA -> 0
0x4D6DD7 -> 1
0x4D6DE5 -> 2
```

Without Ball:

```text
0x4D6DF3 -> 0
0x4D6E00 -> 1
0x4D6E0E -> 2
0x4D6E1C -> 3
```

With Ball:

```text
0x4D6E2A -> 0
0x4D6E37 -> 2
0x4D6E45 -> 1
0x4D6E53 -> 3
```

Aggression is clamped/selected through the UI path and written at `0x4D701E`.

### No backend AI-manager write

An exhaustive instruction-level search for byte writes to `+0x1B5`, `+0x1B6`, and `+0x1B7` finds only the constructor, DBRTeam copy path, and user-UI mutations above. The corresponding DBRTeam `+0x1B4` writes have the same constructor/copy/UI structure; apparent dword writes at the same numeric offset elsewhere belong to unrelated object layouts or stack frames rather than this DBRTeam byte.

This resolves the former AI-tactics uncertainty:

- the manager tactical bytes `DBRManager+0x30..+0x33` are used by the separate compact MatchEngine-side snapshot mapped in the previous section;
- they are **not copied into** backend DBRTeam `+0x1B4..+0x1B7`;
- a normally constructed AI club therefore enters the backend calculator with the fresh DBRTeam defaults unless those live fields have been preserved through an existing copied/mutated team state.

That behavior is consistent with the backend's separate fixed AI strength modifiers (attack x1.05 and defence x1.10) and with its direct reads of the DBRTeam fields.

### Type-11 consequence

The MatchCalculator advance path around `0x62FE10` likewise does not apply family-11 tactical records back into DBRTeam state. Its football-record passes process scoring/incidents/substitutions/statistical state, while tactical family 11 remains part of the chronological command/event stream.

The evidence therefore supports this architecture:

```text
live DBRTeam tactical state
    <- constructor / copied state / user tactical controls

typed tactical commands
    -> CullingVisitor
    -> ConversionVisitor
    -> family-11 timeline records

MatchEngine initial tactics snapshot
    <- 0x40D860 (user live state or AI manager presentation preferences)
```

These are related representations, but they are not one shared mutable tactical store.
## Exact initial team roster order

**Confirmed from player startup `0x421CE0` and team append helper `0x40D4F0`.**

The ordered team roster at:

```text
team +0x244  uint16 player IDs
team +0x294  roster count
```

is not initialized by a separate rating/position sort.

Startup routine `0x421CE0` iterates the global runtime DBRPlayer array linearly in its database-loaded order. For each player it:

1. performs player startup state work, including the already-mapped Non-EU derivation;
2. resolves the player's current club/team;
3. obtains the player's uint16 ID from `DBRPlayer+0x04`;
4. calls `0x40D4F0(team, player_id, 1)`.

The append tail of `0x40D4F0` is exact:

```text
index = team+0x294
team[+0x244 + 2*index] = player_id
team+0x294 = index + 1
```

at `0x40D5DF..0x40D5FD`.

The argument value 1 enables additional shirt/position-state handling earlier in the helper, but the roster insertion itself is still an append at the current count. There is no sort before this insertion.

Therefore the **fresh initial runtime roster order equals global Master.dat/DBRPlayer order filtered by current club**.

This matters because the exact AI selector preserves roster order for strict-score ties and the MatchCalculator participant collector preserves this same team-roster order. A clean-room game initialized directly from the shipped database can consequently derive the original starting roster order by filtering the parsed player sequence by club ID. Later transfer/reordering operations may of course mutate runtime roster order and must be preserved as live state.
## Exact AI-opponent pre-match Condition initialization

**Confirmed from match setup 0x510D60, AI selection 0x5111A0, team Condition helper 0x4080F0, RNG helper 0x64D5B0, and the original tuning-key loader.**

For each non-user-controlled team, the original setup order is:

```text
0x5111A0  AI formation / XI / substitutes / participant construction
0x40D860  MatchEngine-side initial team snapshot
...
0x4080F0  overwrite Condition for every player in that team roster
...
MatchCalculator execution
```

The user-team predicate is checked through `0x4139E0`; `0x4080F0` is skipped for a user-controlled team.

### Exact Condition formula

`0x4080F0` walks the full ordered roster `team+0x244`, not only the selected XI/bench, and writes:

```text
DBRPlayer+0x77 =
    OppMinVal
    + RNG(6)
    + RNG(5)
```

The store is a byte store, so tuning-overflow behavior is naturally modulo 256.

The tuning loader at `0x5034D7..0x50350D` names global `0x8217C0` exactly:

```text
OppMinVal
```

and the analyzed executable's initialized default is:

```text
OppMinVal = 90
```

Therefore with shipped defaults each AI-controlled club player enters the match with Condition in **90..99**, consuming exactly two RNG calls per roster player in roster order:

```text
RNG(6)  -> 0..5
RNG(5)  -> 0..4
```

This happens **after** AI lineup selection, so Condition does not affect which XI/bench is chosen by `0x409C90`. It does affect the subsequent MatchCalculator effective-skill and fatigue/injury paths.

### Persistence consequence

The initializer mutates the underlying DBRPlayer objects directly. Thus an AI player's Condition may persist after the match, but the next non-user match setup overwrites it again with a fresh `OppMinVal + RNG(6) + RNG(5)` value before calculation.

This means ordinary between-match Condition recovery is primarily relevant to user-controlled/preserved team state; autonomous AI-vs-AI simulation should reproduce the pre-match randomization rather than carrying raw post-match fatigue forward unchanged.

The clean-room autonomous Premier League AI path now performs this exact whole-roster initialization after lineup selection and before building the calculator-facing side, on the same RNG stream used by the match.
## Exact Pitch Wear environment field and lifecycle

**Confirmed from DBRTeam field writes, match setup, UI bands and the original tuning-key loader.**

The formerly neutral DBRTeam byte at `team+0x1D7`, copied into MatchCalculator `+0xD47`, is exactly **Pitch Wear**.

The original tuning table names the governing globals:

```text
PitchRecover  = 2
PitchWear     = 16
RainPitchWear = 32
MaxPitchWear  = 192
```

in the analyzed executable.

### Initialization and match input

The DBRTeam constructor initializes:

```text
team+0x1D7 = 0
```

At match setup `0x510FE4..0x510FF4`, the first match team (side 0 / home side in the reconstructed fixture path) is resolved and its Pitch Wear byte is copied unchanged to:

```text
MatchCalculator+0xD47
```

The recovered injury-incidence routine later uses the top two bits of this byte:

```text
pitch_wear_contribution = PitchWear >> 6
```

so Pitch Wear contributes 0..3 to the injury incidence score.

### Post-match wear

The post-match team routine around `0x404D40` reads MatchCalculator weather byte `+0xD46`.

If weather code is **2**, it adds `RainPitchWear`; otherwise it adds `PitchWear`. The result is capped at `MaxPitchWear`:

```text
if match_weather == 2:
    wear += RainPitchWear
else:
    wear += PitchWear

wear = min(wear, MaxPitchWear)
```

Thus weather code 2 is independently identified as the rain state for pitch-wear purposes.

### Daily recovery

Global day-advance processing calls `0x40BA50`, which iterates every club/team and invokes `0x40DD70` once per day.

For a non-user-controlled team, `0x40DD70` begins with exactly:

```text
recovery = PitchRecover
```

and subtracts that amount from Pitch Wear, flooring at zero.

For the user-controlled club only, additional grounds/facility-dependent recovery can be added probabilistically. The associated tuning keys include:

```text
PWHeatingGain
PWDrainageGain
PWSprinklerGain
PWGGain
```

Those user-facility modifiers remain a separate reconstruction concern; autonomous AI clubs use the exact base recovery of 2 per day.

### UI bands

The pitch-status UI compares the same DBRTeam byte against:

```text
30
60
90
120
```

to select one of five pitch-condition presentation states, independently confirming that this byte is a bounded wear/condition scalar rather than a weather enum.

This resolves the last unnamed input to `ConditionInjurySettings`: autonomous match calculation should receive the current home club Pitch Wear byte as the environment value, not an invented weather or pitch-type code.
## Exact pre-match temperature and weather generation

**Confirmed from `0x6314E0`, `0x631630`, the current-date weekday test and original weather tuning keys.**

Before AI Condition initialization, match setup generates one shared match environment.

The shipped monthly base-temperature defaults are:

```text
Weather_TempJan = 0
Weather_TempFeb = 5
Weather_TempMar = 10
Weather_TempApr = 15
Weather_TempMay = 20
Weather_TempJun = 25
Weather_TempJul = 30
Weather_TempAug = 25
Weather_TempSep = 20
Weather_TempOct = 15
Weather_TempNov = 10
Weather_TempDec = 5

Weather_GlobalMinTemp = -5
Weather_GlobalMaxTemp = 35
```

The setup weekday flag is derived from the OLE date as `(date+5)%7`; values 5 and 6 take the weekend branch. For the Gregorian calendar used by the game this is exactly:

```text
Monday-Friday -> weekday/evening flag 1
Saturday-Sunday -> flag 0
```

When that weekday/evening flag is set, the base temperature is reduced by exactly **5°C**.

Then:

```text
temperature = monthly_base
            - (5 if weekday/evening else 0)
            + RNG(6) - 3

temperature = clamp(temperature, -5, 35)
```

so the random temperature perturbation is -3..+2.

Weather code `MatchCalculator+0xD46` is then generated by `0x631630`:

```text
temperature <= 0:
    RNG(2)==0 -> code 4
    RNG(2)==1 -> code 3

temperature >= 22:
    code 1
    # no weather RNG call

1 <= temperature <= 21:
    RNG(4)==0 -> code 2
    otherwise -> code 0
```

Code **2** is independently identified as **rain** because the post-match pitch path selects the explicitly named `RainPitchWear` tuning value only for `D46==2`.

The remaining weather codes are intentionally kept numeric until their presentation names are independently recovered.

### Exact RNG order around AI preparation

The high-level setup order is now reconstructed as:

```text
1. select/commit both AI teams
2. construct MatchEngine-side team snapshots
3. derive weekday/evening flag
4. generate temperature
5. generate weather code
6. copy home Pitch Wear into MatchCalculator
7. initialize full home AI roster Condition
8. initialize full away AI roster Condition
9. calculate match
```

The clean-room fixture-level preparation now preserves the meaningful RNG order:

```text
both deterministic AI selections
-> weather RNG
-> home Condition RNG
-> away Condition RNG
-> MatchCalculator RNG
```

and feeds current home Pitch Wear into the recovered Condition/injury settings.
## Exact Premier League suspension lifecycle

**Confirmed from post-match controller `0x5127A0`, DBRPlayer routines `0x419490`, `0x419680`, `0x4197C0`, and RTTI for the normal `League` versus special `Cup` runtime objects.**

The normal Premier League path uses the general DBRPlayer suspension state:

```text
+0x139  cumulative booking counter
+0x13A  rolling five-booking counter
+0x13B  general suspension matches remaining
+0x160  suspension effective date
+0x14 bit 1  currently suspended/unavailable flag
```

The separate `+0x13E` counter belongs to a special competition path. The relevant virtual method on the normal RTTI class `League` returns zero, while the `Cup` implementation enables the special branch. The shipped Premier League therefore uses `+0x13B`, not `+0x13E`.

All of these bytes initialize to zero in the DBRPlayer runtime constructor around `0x41794F..0x41796D`.

### Exact post-match ordering

For each team, `0x5127A0` performs:

```text
1. 0x419490 over the complete club roster
   -> clear suspended bit
   -> serve one already-active ban match when eligible

2. 0x4197C0 over MatchCalculator participants in participant order
   -> process current-match dismissal/booking counters

3. 0x419680 over the complete club roster
   -> set suspended bit for the next competition fixture
```

Only after this discipline pass does the later team post-match routine `0x404CE0` run player Form processing. Therefore any red-card `RNG(3)` draw occurs **before** post-match Form `RNG(100)` draws.

### Serving an existing general suspension — 0x419490

The routine first clears DBRPlayer `+0x14 bit 1`.

For the normal League branch:

```text
if suspension_matches_remaining == 0:
    stop

if suspension_effective_date > current_match_date:
    stop

suspension_matches_remaining -= 1
```

Exactly one match is consumed. If the counter reaches zero, the executable can create the corresponding return-from-suspension news/message object; that presentation side effect is not required for match availability.

### Current-match participant card inputs

The participant records consumed by `0x4197C0` use:

```text
participant +0x48  booking count/input
participant +0x49  dismissal/red-card input
participant +0x4A  injury input
```

The clean-room timeline maps type-5 BOOKED and SENT_OFF incidents to the first two fields for persistence.

### Dismissal path

Dismissal is processed before bookings.

If the player previously had no general suspension counter:

```text
suspension_effective_date = current_match_date + 7 days
```

Then the executable consumes:

```text
RNG(3)
```

with exact result:

```text
RNG(3) == 0  -> add 3 suspension matches
otherwise    -> add 1 suspension match
```

If a suspension counter already existed, adding the new ban does **not** reset the prior effective date.

### Booking path

If the current match booking input is nonzero, `0x4197C0` first evaluates the **pre-increment** cumulative booking byte:

```text
if cumulative_booking_counter % 13 == 12:
    if suspension_matches_remaining == 0:
        suspension_effective_date = current_match_date + 7 days
    suspension_matches_remaining += 3
```

The modulo-13 rule is unusual but instruction-level exact and is intentionally preserved without relabeling it as a modern real-world card rule.

It then increments both booking bytes by the match booking count:

```text
+0x139 += bookings
+0x13A += bookings
```

and applies the five-booking threshold:

```text
if +0x13A >= 5:
    +0x13A -= 5
    if suspension_matches_remaining == 0:
        suspension_effective_date = current_match_date + 7 days
    suspension_matches_remaining += 1
```

The original performs one threshold check/subtraction rather than a loop.

### Seven-day activation gate and next-fixture refresh — 0x419680

After current-match cards are added, the executable resolves the club's next competition fixture beginning from **current date + 1 day**.

For a known next fixture:

```text
suspended = (
    suspension_matches_remaining > 0
    and suspension_effective_date <= next_fixture_date
)
```

Thus a newly issued ban does **not** automatically mean “miss the next match.” A club can play an intervening fixture inside the seven-day effective-date window before the suspension activates.

Example:

```text
Sat Aug 19: new one-match ban; effective Sat Aug 26
Wed Aug 23: player may still be eligible
Sat Aug 26: suspended bit becomes active
after Aug 26 fixture: 0x419490 consumes one suspension match
```

When no future competition fixture context is available, `0x419680` sets the suspended bit whenever the general counter remains nonzero.

### Clean-room implementation

RuntimePlayer now preserves the four normal-league discipline values separately from the boolean availability bit. The autonomous Premier League post-match path reproduces the original three phases in roster/participant order and uses each club's own next unplayed fixture date for the effective-date gate.

Because `base_lineup_eligible()` already rejects `RuntimePlayer.suspended`, the refreshed suspension state automatically feeds the next AI lineup selection.
## Exact persistent match-injury lifecycle

**Confirmed from post-match controller `0x5127A0`, injury creator `0x41A5B0`, persistent-object factory `0x605F70/0x605F90`, injury finalizer `0x60AA20`, return cleanup `0x418AD0`, and the original injury tuning table.**

A MatchCalculator type-5 injury incident is not itself the long-term injury state. After the match, FM2001 can create a separate 12-byte persistent injury object referenced by:

```text
DBRPlayer+0x24C
```

The persistent object stores:

```text
+0x00  absolute return date
+0x04  injury source mode
+0x05  severity code
+0x08  player ID
```

It does **not** retain the anatomical injury bucket. Consequently presentation naming ambiguities do not prevent exact availability/recovery reconstruction.

### AI minimum-availability guard

`0x41A5B0` treats user and non-user teams differently.

For a non-user/AI team it calls the team availability counter and compares it with the tuning key:

```text
MinPlayersAvailForInj = 14
```

If fewer than 14 players are currently available, no persistent injury object is created.

This test happens before the existing-injury check and before injury-generator RNG. Because the post-match controller walks participants in order and marks a newly injured player immediately, that new injury can reduce the available-player count seen by later participants in the same match.

User-controlled teams bypass this 14-player guard.

### Source mode

If no persistent injury already exists, `0x41A5B0` chooses:

```text
Condition >= 75 -> source mode 0
Condition <  75 -> source mode 1
```

The split uses the already-known:

```text
ConditionInjuryInducingLevel = 75
```

This Condition is the **post-calculator** DBRPlayer Condition. The persistent injury finalizer can then reduce it further.

### Mode 0 category table

The normal match-injury dispatcher consumes `RNG(100)` and uses cumulative thresholds:

```text
 0..2   Broken Toe
 3..5   Ankle
 6..11  Achilles
12..17  Shin
18..25  Calf
26..33  Thigh
34..39  Knee
40..49  Hamstring
50..59  Groin
60..68  Hernia
69..77  Abdomen/Stomach
78..83  Ribs
84..87  Collar Bone
88..95  special presentation bucket
96..99  Broken Leg
```

The shipped tuning keys confirm the cumulative boundaries 3, 6, 12, 18, 26, 34, 40, 50, 60, 69, 78, 84, 88 and 96. A separately loaded shoulder-dislocation threshold exists but is not referenced by this dispatcher.

### Mode 1 low-Condition table

For Condition below 75, source mode 1 consumes `RNG(100)` and uses:

```text
 0..9   Ankle
10..19  Achilles
20..29  Calf
30..39  Thigh
40..49  Knee
50..59  Hamstring
60..69  Groin
70..79  Hernia
80..99  Abdomen/Stomach
```

### Exact severity/recovery behavior used by match injuries

The individual generators often hard-code recovery windows rather than using the generic `Injury*OutMin/Max` tuning table.

Key reconstructed branches:

```text
Broken Toe:
    recovery = RNG(4)+3              # 3..6 weeks
    severity = constructor default 4
    Condition drop = 40

Ankle / Calf / Thigh / Hamstring / Groin:
    severity roll RNG(100)
    <50  code0, 1 week,        drop10
    <80  code1, RNG(4)+3,      drop35
    <95  code2, RNG(4)+11,     drop60
    else code3, RNG(4)+11,     drop60

Achilles:
    severity roll RNG(100)
    <80  code1, RNG(4)+3,      drop35
    <95  code2, RNG(12)+12,    drop60
    else code3, RNG(12)+12,    drop60

Shin:
    consumes an otherwise-unused RNG(100)
    code1, RNG(4)+3, drop35

Knee:
    severity roll RNG(100)
    <50  code0, RNG(2)+1,      drop10
    <80  code1, RNG(4)+3,      drop35
    <95  code2, RNG(4)+12,     drop60
    else code3, RNG(4)+11,     drop60

Hernia:
    consumes unused RNG(100)
    code1, RNG(3)+4, drop35

Abdomen/Stomach:
    consumes unused RNG(100)
    code0, RNG(2)+1, drop10

Ribs:
    severity roll RNG(100)
    <50  code0, 1 week,        drop10
    else code1, RNG(4)+3,      drop35

Collar Bone:
    consumes unused RNG(100)
    code1, RNG(4)+3, drop35

special 88..95 bucket:
    consumes unused RNG(100)
    code1, literal 6 weeks, drop35

Broken Leg:
    severity roll RNG(100)
    <60  code1, literal 12 weeks, drop35
    <90  code2, literal 26 weeks, drop60
    else code3, literal 26 weeks, drop60
```

Several of these expose original-code quirks, including the Achilles first severity threshold reading the same 80-valued global used by the ankle path and the special bucket reading the knee-moderate Condition-drop global. The reconstruction preserves the executed behavior rather than replacing it with nearby unused tuning keys.

### Persistent finalization

For an autonomous AI club there is no medical-staff recovery reduction. The common finalizer performs:

```text
injured bit = 1
return_date = current_date + 7 * recovery_weeks

if Condition > condition_drop:
    Condition -= condition_drop
else:
    Condition = 1
```

It also updates DBRPlayer `+0x22` by severity:

```text
code0 -> +1
code1 -> +4
code2/code3 -> +8
code4 -> +0
```

The clean-room runtime preserves this byte neutrally as `injury_history_weight` because its broader gameplay semantics are not yet named.

For a user-controlled team, the original finalizer can reduce recovery weeks through a medical/staff path that consumes additional `RNG(5)` calls. That user-specific medical modifier remains deliberately separate; the autonomous AI path is exact.

### Return from injury

The finalizer schedules a return event for the absolute return date. The return handler eventually calls `0x418AD0`, which:

- destroys/clears the persistent injury object;
- clears the persistent injured bit;
- does **not** restore Condition.

The return event is queued in the global dated-event container. Fast calendar advancement processes due fixtures before the post-match/day event pass, so an injury whose stored return date equals a fixture date remains unavailable for that day's fixture and is cleared afterward. The clean-room season scheduler must therefore clear injury metadata and `injured=False` in the post-fixture phase of the stored return date, leaving current Condition unchanged.

### Exact post-match RNG ordering

A critical correction to the earlier reconstruction is that `0x5127A0` works **participant by participant**:

```text
for participant in participant order:
    persist cards/red card for this player
        -> possible red RNG(3)

    if this participant was injured:
        create persistent injury now
        -> category/severity/recovery RNG

move to next participant
```

Only after the incident pass does the later player/Form processing run.

Thus, for example:

```text
participant 0 injured
participant 1 sent off

RNG order:
    participant 0 injury RNG
    participant 1 red-card RNG(3)
    later Form RNG
```

It is incorrect to process all red cards for a side first and all injuries afterward.

The clean-room autonomous Premier League path now:

1. synchronizes MatchCalculator Condition copies back to runtime players;
2. serves old suspension state;
3. processes cards and persistent injury creation interleaved in participant order;
4. refreshes next-fixture suspension availability;
5. applies home Pitch Wear;
6. runs the later post-match Form pass without re-copying Condition.

This ensures the persistent injury Condition loss cannot be overwritten by a later calculator-state copy.


## Exact fast-calendar day order and due-fixture scheduler

**Confirmed from direct disassembly of the canonical executable.**

The accelerated calendar loop increments the global current date at `0x4A84FD` and then calls `0x4A83D0` once for that new date. `0x4A83D0` is a three-stage dispatcher:

```text
0x4A7280
0x4A8260
0x4A8070
```

The middle stage is the actual dated-match scheduler. `0x4A8260` runs the date-indexed walker `0x6168C0` first on container `0x947AD8` and then on `0x947AF0`.

For the bucket corresponding to the current date, `0x6168C0` walks the stored linked list of scheduled match nodes. After its eligibility checks it invokes virtual slot `+0x10` on the underlying match object. The `LeagueMatch` RTTI/vtable at `0x7C4C24` maps that slot to `0x513010`, the already-recovered match-controller/calculation path.

The scheduler separates user-involved and autonomous matches. Helper `0x616990` iterates the registered user contexts and compares their club with both match sides. The first scheduler pass skips matches for which that helper is true, so eligible autonomous fixtures are calculated first. A second pass walks the bucket again and calculates remaining eligible matches.

### Same-day match order

The original scheduler does not establish fixture-ID order as its execution order. Date-bucket insertion at `0x615950` links nodes into per-date lists, and `0x615AE0` performs an RNG-driven shuffle of one linked list. `0x615BE0` applies that shuffle across schedule buckets during the schedule setup path reached from `0x616620`.

Therefore a clean-room multi-fixture loop must not claim that sorting simultaneous fixtures by static fixture ID reproduces original RNG ordering. Until the schedule-container initialization stream is reproduced, exact cross-fixture RNG order for simultaneous matches remains a separate boundary.

### Post-fixture day maintenance

After the dated-match scheduler returns, `0x4A8070` begins by processing the global dated-event container `0x947AA8` through `0x613EE0(current_date, 1)`. The event walker calls virtual slot `+0x10` for events whose stored date is at or before the supplied date.

The persistent injury return object is RTTI class `MPMInjuryReverse` with vtable `0x7D7760`. Its `+0x10` handler is `0x5D7B40`, which ultimately calls `0x418AD0` for each returned player. Because this event pass occurs after `0x4A8260`, a player returning on a fixture date becomes available only after that day's scheduled fixtures have been processed.

The existing Pitch Wear cadence remains daily. `0x4A8070` calls `0x4138E0` on every day; `0x4138E0` calls club traversal `0x40BA50`, which invokes `0x40DD70` for each club. The separate `0x40BAD0` traversal inside `0x4A8070` is gated by the weekly date test and calls a different club routine, so it is not the Pitch Wear recovery path.
