# Player Development and Aging

_Last updated: 23 September 2026_

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

## Club/training modifier after age recalculation

After the base age formula, `0x41EAD0` performs an additional per-skill adjustment when:

1. a club/state predicate reached through `0x417340` is true; and
2. player flag bit tested by `0x417A60` is not set.

It obtains a club-associated structure through `0x417380` and reads a skill-indexed byte at returned-object `+0x30+slot`.

Observed adjustment:

```text
m = club_data[0x30 + slot]

if current + m <= target:
    current = current + m
else:
    current = target - m
```

The semantic identity of this object/byte is not yet confirmed. Training/development influence is a strong hypothesis, but this must be proven from the surrounding club structures and source/RTTI evidence before naming it definitively.

## Next steps

1. Identify the club-associated object returned by `0x417380` and the 17 bytes at `+0x30`.
2. Identify predicates `0x417340` and player flag accessor `0x417A60`.
3. Determine invocation cadence for `0x41EAD0` during season progression.
4. Recover how training systems modify the per-skill club/player development values.
5. Integrate the verified development model into the clean-room reconstruction.
