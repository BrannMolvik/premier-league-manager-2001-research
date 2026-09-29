# Gate 12 - English Domestic Cups

_Last updated: 29 September 2026_

## Scope

Gate 12 begins by connecting the already-recovered generic Cup startup runtime
to live season progression. This note starts with the canonical English
domestic cups rather than reopening their solved startup allocation/shuffle
work.

Canonical source files were re-extracted from the authorized FM2001 disc and
reverified before this audit:

- `FOOTBAL.EXE` SHA-256
  `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`;
- `Static.dat` SHA-256
  `e0ff7c10a5f5f973a87cf6cd2d3770e623071899a0b30378debd0e7d13edb9d8`;
- `English.str` SHA-256
  `aa594a55ad95c672b69184e5f3ff8349e41fe95b48c5dcb3c8fcfe2bcdf5b601`.

## Canonical English domestic competition IDs

The English root country/region used by the F.A. Premier League is **26**.

Relevant primary-container competitions are:

| ID | Name | Runtime kind | Matchdays |
|---:|---|---:|---:|
| 0 | F.A. Premier League | League | 38 |
| 1 | FA Cup | Cup | 8 |
| 5 | League Cup | Cup | 7 |
| 6 | Charity Shield | Cup | 1 |
| 8 | Challenge Shield | Cup | 6 |
| 2 | Division 1 (ENG) | League | 46 |
| 3 | Division 2 (ENG) | League | 46 |
| 4 | Division 3 (ENG) | League | 46 |
| 7 | Conference | League | 42 |

Gate 12 starts with competition **1** and **5**.

## FA Cup source structure

Competition 1 is a NormalRound Cup throughout:

| Round | ID | Week/day | Replay week/day | Teams | New entrants |
|---|---:|---|---|---:|---:|
| 1st Round | 38 | 19/6 | 20/3 | 80 | 80 |
| 2nd Round | 39 | 23/6 | 24/3 | 40 | 0 |
| 3rd Round | 40 | 29/6 | 31/3 | 64 | 44 |
| 4th Round | 41 | 32/6 | 33/3 | 32 | 0 |
| 5th Round | 42 | 35/6 | 36/3 | 16 | 0 |
| Quarter Final | 43 | 38/6 | 0/0 | 8 | 0 |
| Semi Final | 44 | 42/6 | 0/0 | 4 | 0 |
| Final | 45 | 45/6 | 0/0 | 2 | 0 |

Its six allocation instructions are all type 5 ranked/direct-club sources:

```text
source 0   quantity 20
source 2   quantity 24
source 7   quantity 22
source 89  quantity 10
source 3   quantity 24
source 4   quantity 24
```

The existing startup materializer already handles this allocation order,
participant insertion, Fisher-Yates/qsort pairing, winner ClubRefs and schedule
nodes.

## League Cup source structure

Competition 5 combines TwoLegRound and NormalRound:

| Round | ID | Type | Week/day | Second/replay week/day | Teams | New entrants |
|---|---:|---|---|---|---:|---:|
| 1st Round | 185 | TwoLeg | 7/3 | 9/3 | 70 | 70 |
| 2nd Round | 186 | TwoLeg | 12/3 | 13/3 | 50 | 15 |
| 3rd Round | 187 | Normal | 19/3 | 0/0 | 32 | 7 |
| 4th Round | 188 | Normal | 22/3 | 0/0 | 16 | 0 |
| Quarter Final | 189 | Normal | 25/3 | 0/0 | 8 | 0 |
| Semi Final | 190 | TwoLeg | 30/3 | 32/3 | 4 | 0 |
| Final | 191 | Normal | 36/7 | 0/0 | 2 | 0 |

Canonical allocation instructions are:

```text
type 3 source 5 quantity 1
type 3 source 1 quantity 1
type 5 source 0 quantity 5
type 5 source 0 quantity 15
type 5 source 2 quantity 24
type 5 source 3 quantity 24
type 5 source 4 quantity 24
```

The packed instruction request total is 94 while the Cup's entrant capacity is
92; the already-recovered `0x4F57E0` behavior silently drops the two late
refs once all round entrant quotas are full. This is already covered by the
generic startup materializer and must not be “fixed” as a data error.

## What is already solved

The generic Gate-3/Gate-4 competition reconstruction already provides:

- canonical Cup allocation instruction ordering;
- direct club, competition-position and match-result ClubRef descriptors;
- FA/League Cup entrant buckets;
- exact first participant shuffle and ClubRef qsort;
- pairings for NormalRound and TwoLegRound;
- FirstLeg/SecondLeg node direction and dates;
- next-round symbolic winner references;
- exact global schedule-node insertion/conflict behavior;
- deterministic participant/pairing/schedule digests.

Therefore Gate 12 should not rebuild cup draws.

## First live-runtime gap

`GameState` currently owns only a mutable `PremierLeagueState`. The generic
Cup runtime is a startup/materialization layer, not a live competition result
store. Consequently a scheduled Cup node can describe:

```text
winner of ("cup_result", competition_id, round_id, pair_index)
```

but normal gameplay has no persistent object that records that match result and
resolves the later type-1 ClubRef when the next round becomes due.

This is the first Gate-12 bridge.

The executable semantics are already instruction-closed:

- ClubRef type 0 -> direct cached club;
- ClubRef type 1 selector 0 -> referenced match winner/result club;
- ClubRef type 1 selector nonzero -> the opposite/losing club;
- resolver `0x4F28E0` uses the referenced match virtual `+0x44`;
- loser/opposite selection is helper `0x513FB0`.

For the FA Cup and League Cup, initial entrants are direct refs; later knockout
rounds are connected by type-1 match-result refs. Therefore a persistent
winner/loser result-token resolver is the smallest source-backed runtime piece
that unlocks domestic-cup progression without guessing score/replay rules.

## Implementation order

1. Add a deterministic runtime result registry keyed by the existing
   `("cup_result", competition_id, round_id, pair_index)` token.
2. Resolve direct type-0 refs and type-1 winner/loser refs exactly.
3. Add deterministic tests showing a recorded first-round result resolves the
   already-materialized next-round participant.
4. Then trace/implement actual `CupMatch` completion rules needed to populate
   those outcomes, including FA Cup replay behavior and League Cup two-leg
   aggregate/tie behavior.
5. Only after result production is source-backed should Cup nodes enter the
   normal `GameState` calendar/human-fixture path.

This sequencing preserves the solved startup RNG stream and avoids inventing
domestic-cup result semantics.


## Live result-resolution checkpoint

The first live-runtime bridge is now implemented and verified.

Checkpoints:

- `9f6e39f7`: persistent Cup result-token registry and exact type-0/type-1
  ClubRef resolution;
- `4167244b`: deterministic winner/loser selector and next-round resolution
  tests;
- `c2334465`: shared CupMatch virtual `+0x44` / `0x514000` modeled from
  match-state snapshots, including linked reversed-leg aggregate totals;
- `64c4f24c`: single-match, two-leg and exact-tie virtual-semantics tests;
- `87d3c2b0`: definitive snapshots can populate the persistent registry
  directly; unresolved draws do not consume the result token and can therefore
  be superseded by a later Replay/SecondLeg object.

GitHub Actions at `87d3c2b0b92da0cd2441455b1ac4d8811b84f457`
ran **690 reconstruction tests**. The only two failures are the unchanged
secondary root-order and secondary bucket-count assertions already present
before Gate 12. All new Cup tests pass. Repository asset policy passes.

### Active trace

The shared result virtual is no longer the missing piece. The next dependency is
the class-specific producer path that makes a knockout result definitive:

1. trace NormalRound draw handling into FA Cup Replay object creation,
   linkage, schedule insertion and completion;
2. trace TwoLegRound first-leg state into the reversed SecondLeg object;
3. for an exact tied aggregate where `0x514000` still returns no club, trace
   the source-backed continuation/tie-break path rather than guessing
   extra-time or penalties;
4. only after those paths are instruction-closed should the clean-room
   construct a definitive `CupMatchResolutionSnapshot` and record it.

Domestic Cup nodes remain deliberately outside `GameState` until this
producer path is source-backed.
