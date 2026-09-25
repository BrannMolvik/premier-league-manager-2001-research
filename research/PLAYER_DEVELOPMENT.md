# Player Development and Aging

_Last updated: 24 September 2026_

This file tracks the recovered FM2001 player-development model. It separates verified executable behavior from remaining hypotheses.

## Relevant runtime fields

Within a 592-byte runtime `DBRPlayer` object:

- `+0x1E..+0x2E`: 17 current-skill bytes
- `+0x2F..+0x3F`: 17 corresponding peak/target skill bytes
- `+0x111..+0x121`: 17 saved baseline-skill bytes
- `+0x122`: saved/baseline age
- `+0x123`: physical peak age
- `+0x124`: outfield-skill peak age
- `+0x125`: late/goalkeeper-group peak age

The complete skill ordering is:

0 Speed  
1 Strength  
2 Stamina  
3 Determination  
4 Injury Proneness  
5 Passing  
6 Shooting  
7 Tackling  
8 Heading  
9 Control  
10 Technique  
11 Awareness  
12 Agility  
13 Goalkeeping  
14 Confidence  
15 Leadership  
16 Set Piece

## Peak-age tuning values

The executable's initialized tweak globals contain:

- `AGEPhyical_lowest_peak` = 25
- `AGEPhyical_highest_peak` = 26
- `AGESkill_lowest_peak` = 27
- `AGESkill_highest_peak` = 29
- `AGEGoalie_lowest_peak` = 30
- `AGEGoalie_highest_peak` = 32
- `AGEPeakPeriod` = 5

Function `0x64D540` returns:

```text
floor(rand() * N / 32768)
```

with the CRT-style random source in the 0..32767 range. Therefore peak generation is effectively:

```text
physical_peak = 25 + random(1)       -> normally 25
skill_peak    = 27 + random(2)       -> 27 or 28
late_peak     = 30 + random(2)       -> 30 or 31
```

If the generated peak exactly equals the player's current age at initialization, the game increments the chosen peak by one.

## Initialization: 0x41E970

The initializer:

1. Gets current player age through `0x4173B0`.
2. Generates the three per-player peak ages described above.
3. Logs a "Player Too Young" diagnostic if age < 15 and clamps the working baseline age to 15.
4. Logs a "Player Too Old" diagnostic if age > 50 and clamps the working baseline age to 50.
5. Stores the clamped baseline age in `player+0x122`.
6. Copies all 17 current-skill bytes from `+0x1E..+0x2E` into `+0x111..+0x121`.
7. Calls age-curve helper `0x41E7F0`.

Thus the game preserves the player's initial/current database skill state as an age-specific baseline from which later age recalculations can be reconstructed.

## Smooth age-curve helper: 0x41E7F0

The helper computes one curve for each of the player's three peak ages.

For age `A` and peak `P`, it first forms:

```text
if A < P:
    r = (A - 10) / (P - 10)
else:
    r = (60 - A) / (60 - P)
```

It then applies the cubic smoothstep:

```text
curve = 3*r^2 - 2*r^3
```

Evidence:

- constants at `0x7BDCA8` and `0x7BDCA0` are 2.0 and 3.0;
- helper `0x6692C0` is used as the floating-point power routine;
- the emitted sequence is `3*r^2 - 2*r^3`;
- the normalization boundaries are hard-coded ages 10 and 60.

The helper writes separate physical, skill and late/goalkeeper curve outputs.

In the currently traced `0x41E970` / `0x41EAD0` paths these computed curve outputs are not obviously consumed afterward; the piecewise recalculation below is independently visible. Their exact downstream purpose, if any beyond legacy/vestigial calculation, remains open.

## Main age/skill recalculation: 0x41EAD0

Notation:

- `A`: current age
- `L`: saved baseline age at `player+0x122`
- `B`: saved baseline skill at `player+0x111+slot`
- `T`: target/peak skill at `player+0x2F+slot`
- `P`: selected peak age for this skill
- `D`: `AGEPeakPeriod` (=5 in the shipped defaults)

The routine loops over all 17 skills and reconstructs the current byte at `player+0x1E+slot`.

### Effective peak groups observed in loop order

Explicit peak-selection branches occur for:

- physical peak: slots 0, 1, 2
- skill peak: slots 5, 6, 7, 8
- late/goalkeeper peak: slots 9, 12, 13, 15

For other slots the previous selected peak value remains in the local variable. Because the loop is strictly sequential, the effective shipped grouping is therefore:

- physical peak: slots 0..4
  - Speed, Strength, Stamina, Determination, Injury Proneness
- skill peak: slots 5..8
  - Passing, Shooting, Tackling, Heading
- late/goalkeeper peak: slots 9..16
  - Control, Technique, Awareness, Agility, Goalkeeping, Confidence, Leadership, Set Piece

This grouping is directly implied by the generated assembly, although the broad developer label `AGEGoalie_...` is unusual for the entire final group.

### Case 1: baseline age is at or before peak (L <= P)

If current age is at or before the baseline age:

```text
A <= L:
V = B * 0.5 * (1 + (A - 10)/(L - 10))
```

If the player has moved from baseline age toward peak:

```text
L < A <= P:
V = B + (T - B) * (A - L)/(P - L)
```

If the player is past peak but within the configured peak period:

```text
P < A <= P + D:
V = T
```

After the peak period:

```text
A > P + D:
V = T * (60 - A)/(60 - P)
```

### Case 2: player was already past peak at baseline (L > P)

For an age at or before peak, the game reconstructs the historical pre-peak value from the target:

```text
A <= P:
V = T * 0.5 * (1 + (A - 10)/(P - 10))
```

For ages between peak and the saved baseline:

```text
P < A <= L:
V = B + (T - B) * (L - A)/(L - P)
```

Equivalent form:

```text
V = T + (B - T) * (A - P)/(L - P)
```

For ages after the baseline:

```text
A > L:
V = B * (60 - A)/(60 - L)
```

### Integer conversion and floor

The floating result is converted to integer by helper `0x668350`, which temporarily sets x87 rounding toward zero. For positive skill values this is effectively floor/truncation.

At the end of each slot, the code applies the normal raw-byte-to-0..30 rating conversion and enforces a minimum displayed rating of 1. If the converted rating would be below 1, current raw skill is set to `0x09` (9), the smallest raw value that maps to rating 1 under the game's scaling formula.

## Why target can be lower than current

The second skill array should be described as a **peak/target skill state**, not as an invariant hard ceiling.

The recalculation formulas explicitly support:

- `T > B`: improvement toward the peak target;
- `T == B`: stable peak;
- `T < B`: decline toward a lower target or reconstruction from a baseline already above target.

This explains the small minority of original database records where target < current without treating them as corrupt data.

## Per-player club training modifier after age recalculation

The object returned through `0x417380` is now identified as the player's **per-club training record**.

Each club-side training object owns 40 records of 200 bytes each. Player runtime bytes `+0x70/+0x76` are 1-based selectors into that table. Whole-record `+8` stores the player ID, and the embedded training subobject begins at whole-record `+0x24`.

The primary 17 one-byte per-skill training counters are at whole-record `+0x30..+0x40` (subobject `+0x0C..+0x1C`).

After the base age formula, `0x41EAD0` reads the selected player's per-skill training byte:

```text
m = training_record[0x30 + slot]

if current + m <= target:
    current = current + m
else:
    current = target - m
```

A second 17-byte region in the training subobject is used for temporary timed effects/cooldowns and is not a second monthly-development boost vector.



## Exact training profile vectors

Routine `0x4EAA00` initializes seven contiguous 17-byte vectors at global `0x876B40`. Direct binary cross-check gives the exact bytes in source-storage order:

- attacking: `[25,0,0,0,0,0,25,0,25,25,0,0,0,0,0,0,0]`
- defensive: `[0,0,0,25,0,0,0,25,25,0,0,12,0,0,0,0,13]`
- midfield: `[0,0,25,0,0,25,0,0,0,25,0,0,0,0,0,0,25]`
- goalkeeper: `[0,0,0,0,0,12,0,0,0,25,0,0,25,25,0,0,13]`
- rest/recovery: all zero
- fitness: `[25,25,25,9,0,0,0,0,0,0,0,8,8,0,0,0,0]`
- technique: `[0,0,0,0,0,0,0,0,25,0,25,0,0,0,12,13,25]`

Method selector `0x4EA9A0` maps runtime IDs:

0 rest/recovery, 1 attacking, 2 midfield, 3 defensive, 4 goalkeeper, 5 fitness, 6 technique.

The non-25 weights (12, 13, 9 and 8) are therefore part of the original probability model and should not be rounded to generic high/low emphases.

Routine `0x41A870` was rechecked directly: active training adds +8 only when `current+8 < 255` **and** `current+8 < target`. Equality with the target does not step.

## Active training profiles

The exact seven 17-skill profile vectors have been reconstructed. Method IDs are:

0. Rest / recovery
1. Attacking
2. Midfield
3. Defensive
4. Goalkeeper
5. Fitness
6. Technique

Successful active training for a skill calls player routine `0x41A870`, adding +8 raw skill while remaining below the development target.

## Active training success probability

For a skill whose selected training profile has nonzero weight:

```text
threshold = profile_weight * Q * 0.5
success if random_integer(0..99) < threshold
```

Quality multiplier `Q`:

- starts at 1.00;
- Youth Team Coach rating 1..5 gives 1.25 / 1.30 / 1.35 / 1.40 / 1.45;
- if there is no Youth Team Coach, an Assistant Manager gives fallback 1.25;
- a Training Centre adds +0.25.

The identities of the Youth Team Coach, Assistant Manager and Training Centre paths are proven from EA's own formatter/RTTI/building code.

## Invocation cadence

The date/calendar path strongly establishes that the main age/development recalculation runs on the **first day of each month** for club players.

## Next steps

1. Finish naming remaining training subobject countdown/date/timed-effect fields.
2. Reproduce the monthly age + training update in clean-room code and validate against known records.
3. Trace injury/condition interactions with training.
4. Continue into contracts/transfers/season logic without revisiting the now-resolved training-record identity.


## 25 September startup RNG ordering correction

The peak-age formulas were already correct, but direct disassembly now fixes their position in the shared game RNG stream.

DBRPlayer constructor 0x4178D0 pushes bound 15 and later calls 0x64D540 at 0x41797F. The result is subtracted from global byte 0x821C25 and stored at player +0x18E. Global 0x821C25 is loaded from the named tuning key maximummorale; the shipped value is 100. Thus construction performs:

    player+0x18E = 100 - RNG(15)

DBRPlayer load routine 0x418B90 later calls 0x41E970 for the three peak draws and then calls RNG(5) at 0x418EF5. That result is incremented, multiplied by 12, stored at player +0xC0, and used to derive date +0x154. The higher-level semantic label for +0xC0/+0x154 remains unresolved.

DBTPlayers loader 0x421C80 proves table-wide ordering: it invokes its allocation/construction virtual before entering the per-record load loop. Therefore all constructor RNG(15) draws for the full player table occur before any player's three peak draws or post-load RNG(5).

The clean-room GameState now reproduces this two-phase ordering with MsvcCrtRng. RuntimePlayer exposes +0x18E as morale and preserves the unresolved +0xC0 value neutrally as startup_month_span.