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


## CupMatch completion producer trace

Recovery generation 59 re-materialized the authorized disc image and reverified
the canonical root executable:

```text
FOOTBAL.EXE
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3
```

The live class-specific knockout completion path is now instruction-closed far
enough to implement without inventing replay, extra-time or two-leg semantics.

### Match subclasses and constructors

Canonical RTTI/vtables and constructors are:

| Runtime class | Type virtual | Vtable | Constructor |
|---|---:|---:|---:|
| `CupMatch` | 2 | `0x7C9D9C` | `0x510520` |
| `CupMatchReplay` | 3 | `0x7C9E80` | `0x510600` |
| `FirstLegMatch` | 4 | `0x7C9EF8` | `0x510640` |
| `SecondLegMatch` | 5 | `0x7C9F70` | `0x510680` |

All four expose the shared result virtual `+0x44 -> 0x514000`.

`CupMatch+0x54` is the linked-match pointer. `0x510520` stores the supplied
link and, when non-null, writes the reverse link back into the other match.
The first/replay or first-leg/second-leg pair is therefore bidirectionally
linked even though the decisive second object consumes the first object's
completed score.

The constructor also packs three boolean inputs into `CupMatch+0x44` bits
`0x2`, `0x4`, and `0x8`. The first two have now been bounded by their
actual MatchEngine consumers:

- bit `0x2` supplies the engine's 90-vs-120-minute capability at
  `0x510DD7 -> MatchEngine+0xD0C`; `0x63173E` passes 90 when clear and
  120 when set;
- bit `0x4` supplies the decisive tie-break/penalty path at
  `0x510E06 -> MatchEngine+0xD10`.

For a base type-2 `CupMatch`, `0x510DC2..0x510DD5` explicitly suppresses
the 120-minute path when bit `0x4` is clear. This is how the same round data
can carry extra-time capability while an ordinary replay-eligible first match
still stops at 90 minutes.

Canonical domestic-round state confirms the interpretation:

- FA Cup rounds 1-5 have replay dates and the decisive flag clear;
- FA Cup quarterfinal, semifinal and final have no replay date and the decisive
  flag set;
- League Cup one-off rounds likewise carry the decisive flag;
- `FirstLegMatch` forces all three flags clear;
- `SecondLegMatch` inherits the round's 120-minute capability and forces the
  decisive flag set.

### NormalRound draw -> Replay

The ordinary completion virtual is `0x5136E0`.

At `0x51391B`, a completed unlinked `CupMatch` calls shared result virtual
`0x514000`. A non-null club continues the resolved-round path. A null result
creates the replay:

1. `0x51392A..` computes the replay schedule date;
2. `0x513967` allocates a 0x5C-byte match object;
3. `0x51399E -> 0x510600` constructs `CupMatchReplay`;
4. the constructor reverses the two ClubRefs, links the original match, forces
   both bit `0x2` and bit `0x4`, and preserves bit `0x8`;
5. `0x5139BA -> 0x615A60` inserts the replay into the schedule.

This is the only fresh runtime constructor call for `CupMatchReplay`; the
other constructor reference is the load/deserialization path.

Replay date arithmetic is retained in raw executable form rather than
over-interpreting field names:

```text
candidate = global_current_day - selected_date_anchor[+8] + 14
round = current_round_vector[pair_index]
if round[+0x2C] > 6:
    floor = round[+0x2C] + 7 * round[+0x28]
    candidate = max(candidate, floor)
```

The linked replay is decisive, so an unresolved first match does not recursively
spawn another replay.

### Two-leg completion and exact aggregate tie

`FirstLegMatch` is built by the TwoLeg round builder at `0x4F6A02`.
`SecondLegMatch` is built at `0x4F6A64` with reversed ClubRefs and the
first leg as its linked match.

During completion:

- aggregate side 0 is current score 0 + linked score 1;
- aggregate side 1 is current score 1 + linked score 0;
- on tied aggregate, shared `0x514000` compares current score 1 with linked
  score 1, which is the recovered away-goal secondary comparison;
- if those values differ, the shared result virtual is already definitive;
- if they are equal too, `SecondLegMatch` has
  `MatchEngine+0xD14 = 1`, and `0x51367D..0x513695` allows the decisive
  tie-break path only when the same away-goal comparison is equal.

The tie-break path first consumes penalty/tie-break events through
`0x632940`, incrementing `CupMatch+0x5A/+0x5B`. If the totals are still
equal, `0x513697 -> 0x64D540(2)` chooses a side and increments one of those
bytes. Score virtuals `0x513E90/0x513EB0` include those bytes, so the next
`0x514000` result is definitive.

This closes the previously deferred exact-tied-aggregate continuation without
guessing a generic penalty implementation.

### Clean-room implementation boundary

The next implementation slice may now model:

- the four Cup match kinds;
- constructor-derived flags and linked/reversed participants;
- NormalRound replay creation after an unresolved first match;
- TwoLeg first/second-leg linkage;
- a decisive tie-break score adjustment supplied by the recovered RNG/event
  path;
- registry finalization only after the decisive match resolves.

The MatchEngine event-level presentation of penalties can remain deferred; the
Gate-12 requirement is the source-backed competition outcome lifecycle needed
to advance the human season.
