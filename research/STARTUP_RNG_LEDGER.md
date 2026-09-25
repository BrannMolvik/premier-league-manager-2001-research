# Startup RNG Ledger

_Last verified: 26 September 2026_

## Scope

This file is the canonical **standard new-game RNG ledger from the application CRT seed through the currently recovered primary-competition RNG state**.

The precompetition sequence is exact. Primary Cup scheduling now has an exact hidden-state call total, while exact bounded-output interleaving/pair identities remain the reopened Gate-3 task before the first Premier League schedule-bucket shuffle.

The original executable uses one shared MSVC CRT RNG stream.

## Primitive

The analyzed executable uses the classic 32-bit MSVC CRT state update:

```text
state = state * 0x343FD + 0x269EC3  (mod 2^32)
rand15 = (state >> 16) & 0x7FFF
```

Bounded helper `0x64D540(n)` computes:

```text
floor(rand15 * n / 32768)
```

Even `RNG(1)` consumes one raw CRT draw.

## Standard first-start ordering

### 1. Application seed

```text
0x531098 -> 0x66A767     obtain current-time value
0x53109E -> 0x66950F     srand(seed)
```

No later mandatory reseed occurs before ordinary new-game competition setup.

The Scouting reseed at `0x4AF7F0` belongs to `PScouting2K` and is not on this path.

### 2. Front-end background Loader444

Startup loads `FM2001_art\generic\bground.444`.

The **first Loader444 decode consumes exactly 260 raw CRT draws**:

```text
0x6864A0 lazy table initialization: 259 raw rand() calls
0x6868E0 conversion path:              1 raw rand() call
                                             ---
                                             260
```

The modern port may decode the original asset differently, but must advance the shared game RNG by these 260 draws for fidelity.

### 3. Intro / initial PStartMenu

After the background:

```text
PREMINTRO.TGQ
 -> initial PStartMenu built inline at 0x53120F..0x53129C
 -> front-end event/idle loop
 -> user chooses New Game
```

This path consumes **zero additional game-CRT draws**.

The first PStartMenu object ends with vtable `0x7C64E0`.

### 4. PStartMenu New Game -> database loader

PStartMenu event/control ID 2 follows:

```text
0x4C3770
 -> ID-2 branch 0x4C37C7
 -> deterministic setup
 -> 0x4C392F call 0x50D630
```

The club, manager, and auxiliary loaders in `0x50D630` are RNG-clean on the standard path.

### 5. DBTPlayers startup

The shipped database has **30,064 players**.

`DBTPlayers` first constructs the complete runtime player array:

```text
30,064 x RNG(15)
```

Then it loads every player in table order:

```text
for each of 30,064 players:
    RNG(1)
    RNG(2)
    RNG(2)
    RNG(5)
```

Therefore DBTPlayers consumes:

```text
30,064 constructor draws
+ 4 * 30,064 load draws
= 150,320 raw CRT draws
```

The Non-EU startup branch adds no RNG draw.

Cumulative raw-draw count after DBTPlayers:

```text
Loader444       260
DBTPlayers  150,320
             -------
             150,580
```

### 6. TeamSelect lifetime

After `0x50D630`, TeamSelect is allocated/constructed and activated.

The standard TeamSelect lifetime from construction through the later Start/Continue click consumes **zero CRT draws** before entering `0x4C41C0`.

The `0x4C41C0..0x4C42EE` prefix is also zero-draw.

### 7. 0x413830 generated-name/youth block

At `0x4C4304`, `0x413830` executes the recovered user-dependent startup RNG work.

#### 7a. 0x414330 generated-name sequence

For the shipped database:

- 1,157 teams qualify for one generated-name call;
- each generated-name call consumes two bounded draws;
- that contributes **2,314** draws;
- 54 additional generated-name calls use the currently selected user's team country;
- those contribute another **108** draws.

Total:

```text
0x414330 = 2,422 bounded/raw CRT draws
```

Cumulative fixed prefix:

```text
Loader444       260
DBTPlayers  150,320
0x414330      2,422
             -------
             153,002 raw CRT draws
```

The bounds of the generated-name draws depend on nationality source-vector counts, but each bounded call advances the CRT stream exactly once.

#### 7b. Per-user youth generation

`0x413980` runs one `0x61DF90` youth-generation block for each linked human user, in user-list order.

The shipped `!Spare` source pool has at least the full fixed **512-candidate** buffer, so normal startup generation is not candidate-limited.

For each user:

1. determine the target size:
   - option 0: `4 + RNG(2)`
   - option 1: `5 + RNG(2)`
   - option 2: `6 + RNG(3)`
   - missing/other: 4 with no option draw;
2. for every generated player:
   - `RNG(current_candidate_count)`
   - `RNG(name_bound)`
   - `RNG(name_bound)`
   - remove selected source by swap-with-last.

Thus, for a single ordinary user whose destination list begins empty:

| option | target | per-user raw draw count |
| --- | --- | --- |
| missing/other | 4 | 12 |
| 0 | 4 or 5 | 13 or 16 |
| 1 | 5 or 6 | 16 or 19 |
| 2 | 6, 7 or 8 | 19, 22 or 25 |

For multiple human managers, consume one block per user in linked-list order.

The exact RNG state is therefore deterministic from:

- initial seed;
- linked-user order/count;
- selected-user country for the fixed 54-name block;
- each user's club country;
- each user's youth option value.

The existing `startup_rng.py` replay helpers already model these bounds/order.

### 8. Competition-entry boundary

After `0x413830`, the path through the immediate wrappers and user-field writes to:

```text
0x4C4379 -> 0x4F7380
0x4C4381 -> 0x4F7C00
```

adds no CRT draw before the competition/schedule initialization boundary.

Therefore the shared CRT state entering competition setup can be reproduced exactly from the known seed and new-game configuration.

## One-user cumulative counts before competition entry

The fixed count before the per-user youth block is **153,002** raw draws.

For one user:

- missing/other option: **153,014**
- option 0: **153,015 or 153,018**
- option 1: **153,018 or 153,021**
- option 2: **153,021 / 153,024 / 153,027**

These counts are diagnostics only. Correct replay must still execute the draws in original order because bounded outputs affect selected youth/name data and later state.

## Gate-2 conclusion

The seed-to-competition mandatory RNG path is bounded.

Confirmed mandatory consumers before competition initialization are:

1. Loader444 first-decode side effect;
2. DBTPlayers construction/loading;
3. `0x414330` generated-name sequence;
4. one `0x61DF90` youth-generation block per linked user.

All other audited standard-path front-end/database/TeamSelect wrappers between these blocks are zero-draw for the game CRT stream.

## Gate-3 boundary

Gate 3 must turn this ledger into a single executable replay and then continue through:

- primary/mode-0 competition initialization;
- any remaining competition-specific RNG consumers;
- the first `0x947AD8 / 0x615BE0` Premier League bucket shuffle;
- fixed-seed intermediate-state tests.


## 9. Primary competition RNG correction

A Gate-4 audit found an omitted pre-`0x615BE0` consumer: every primary Cup
round scheduler shuffles its runtime participant array before the global
schedule-bucket shuffle.

Runtime round classes are:

- type 1 `NormalRound` -> `0x4F64D0`;
- type 2 `TwoLegRound` -> `0x4F6820`;
- type 3 `MiniLeagueRound` -> `0x4F6B10`.

Each round scheduled with N participants consumes:

```text
RNG(N), RNG(N-1), ..., RNG(2)
```

for exactly N-1 calls.

Canonical Static.dat plus the runtime round-fill logic proves:

```text
primary Cups:       27
primary Cup rounds: 115
Normal / TwoLeg / MiniLeague: 80 / 32 / 3
sum(N-1):           1,737 calls
Europe selectors:      2 calls
total competition:  1,739 calls
```

The old assumption that the primary competition tail was merely adjacent
`RNG(6), RNG(6)` calls is superseded. Those two selector calls remain real but
are interleaved with Cup initialization/scheduling.

### Hidden-state replay

Because every bounded draw advances the MSVC LCG exactly once, the hidden state
after primary competition initialization can be reproduced exactly from the
1,739-call total even before every Cup pairing output is materialized.

For the synthetic Gate-3 post-youth checkpoint:

```text
0x2797444C
  + 1,739 CRT calls
= 0x986E4579
```

`competition_startup.py` now separates:

- the isolated Europe selector mechanics; and
- `replay_primary_mode0_pre_shuffle_state`, which advances the complete mapped
  primary competition **state** cost from parsed Cup/round metadata.

### Remaining Gate-3 work

Exact Cup fixture/pairing outputs still require the true bounded-call order:

1. country/root competition initialization order;
2. Europe selector position within that order;
3. each Cup's runtime round sort order;
4. each round's exact Fisher-Yates bound sequence.

That ordering matters to which teams are paired, even though it does not change
the final hidden LCG state after all 1,739 calls.


## 10. Exact primary competition bounded-call order

The reopened Gate-3 work now goes beyond hidden-state call counting. The
canonical **bounded-call event order** before primary `0x615BE0` is
reproducible.

### Cup round ordering

Cup virtual `+0x04 = 0x4F6D60` appends runtime rounds in source attachment
order. Cup virtual `+0x08 = 0x4F6E30` then qsorts the round-pointer array
before `Cup::init` schedules it.

Comparator `0x4F6E50` compares each round's virtual slot-0 8-byte schedule
key:

- NormalRound / TwoLegRound: `(scheduled_week, scheduled_weekday-1)`;
- MiniLeagueRound: the first schedule pair of its referenced child League.

All canonical primary Cups contain at most eight runtime rounds, so the
analyzed CRT qsort uses its exact small-array selection-sort path. Equal keys
are therefore deterministic rather than left as a stable-sort assumption.

### Root competition ordering

Country roots are attached in global competition source order, qsorted by
runtime `+0x18 = -initialization_order_value`, and traversed backwards.

For small root arrays the exact CRT qsort behavior is reproduced. This resolves
Spain's equal-key pair as:

```text
Spanish Cup -> Super Cup -> Primera -> Segunda -> Spanish Spare
```

The large equal-key group in country 116 contains only one primary-Cup
RNG-bearing subtree (World Club Championship), so its position among zero-draw
roots cannot change the competition RNG event stream.

Children are visited in source/global competition order.

### Europe selector positions

The Europe root selector executes inside Cup initialization **before** that
Cup's round scheduler loop.

The canonical primary competition stream contains:

```text
117 RNG-bearing events
  115 Cup round participant shuffles
    2 Europe-root selectors
1,739 bounded CRT calls total
```

The selector events are event indices:

```text
99  Champions League
108 UEFA Cup
```

For synthetic state `0x2797444C`:

```text
before Champions League selector: 0xA16F47F1
RNG(6) -> candidate index 0 -> club 1118
after selector:                   0x82C7CAF0

before UEFA Cup selector:         0x1A3358D6
RNG(6) -> candidate index 4 -> club 1143
after selector:                   0x5FA76C41

after all 1,739 calls:            0x986E4579
```

The complete ordered bound stream is canonically fingerprinted by SHA-256 over
little-endian uint16 bounds:

```text
baef6479394ffee84e7a9aec58d74f1c5418ccaeaad7f617d9ed0f77e95fd8df
```

`reconstruction/competition_startup.py` now materializes this event sequence
and the Fisher-Yates **participant-slot permutation** for each Cup round.
`reconstruction/verify.py` locks the canonical event count, selector positions,
bound-stream digest, selected Europe candidates, and final CRT state.

### Remaining distinction: slot permutation versus club pairing

NormalRound and TwoLegRound perform a participant-record qsort after the
mandatory Fisher-Yates. Therefore the recovered randomized slot permutation is
not yet sufficient to claim the final club/winner-reference pairings.

The remaining Gate-3 task is to materialize the 16-byte participant records,
their allocation/source order, and comparator `0x4F67D0`, then apply the
post-randomization qsort and pairing logic.
