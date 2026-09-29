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


## Replay date and domestic schedule anchor closure

Recovery generation 60 reopened only the replay-date producer around
`0x51392A` against the canonical executable and canonical Static.dat. This
also corrected an inherited date-conversion assumption in the first live
domestic-Cup schedule bridge.

### Exact schedule-container selector

`CupMatch::GetScheduleContainer` at `0x510300` is:

```text
510300  mov ecx,[match+0x0C]
510303  mov eax,0x947AF0
510308  test byte [ecx+0x0C],0x02
51030C  jne 0x510313
51030E  mov eax,0x947AD8
510313  ret
```

The two global schedule containers are constructed through `0x615700`.
The primary container `0x947AD8` is initialized with the 2000-season anchor;
`0x947AF0` is the secondary/older-season container.

Canonical Static.dat gives schedule-container code **1** for both competition
1 (FA Cup) and competition 5 (League Cup). They therefore use the primary
2000-season calendar path.

### Primary Cup source-date conversion

Container initialization `0x6169F0` constructs July 1 of the season year and
aligns **forward** to the first Monday on or after July 1. Round constructor
`0x4F5420` then copies the packed source fields exactly as:

```text
runtime +0x20 = packed scheduled_week
runtime +0x24 = packed scheduled_weekday - 1
runtime +0x28 = packed replay_week
runtime +0x2C = packed replay_weekday - 1
```

Insertion routine `0x615950` forms the relative schedule day as:

```text
7 * runtime_week + runtime_zero_based_weekday
```

and adds the selected container's `+0x08` anchor.

This differs from the previously reused Premier League helper, whose recovered
league convention anchors to the Monday containing July 1. The first
`DomesticCupScheduleState` implementation therefore placed domestic Cup
nodes one week early and is superseded by the source-exact Cup-specific
conversion.

Canonical examples:

```text
FA Cup round 1      packed 19/6 -> Saturday 18 November 2000
League Cup round 1  packed  7/3 -> Wednesday 23 August 2000
```

### Exact NormalRound replay arithmetic

The live replay branch at `0x51392A..0x5139BA` is now closed:

```text
container = match->GetScheduleContainer()        ; 0x510300
relative_current = global_current_day - container[+0x08]
candidate = relative_current + 14

round = owning_cup_round_vector[current_round_index]
if round[+0x2C] > 6:
    floor = 7 * round[+0x28] + round[+0x2C]
    candidate = max(candidate, floor)

construct reversed linked CupMatchReplay
insert through 0x615A60(container, replay, candidate)
```

The `round[+0x28/+0x2C]` fields are the packed replay week and
`replay_weekday - 1`, not an unrelated date object.

Canonical FA Cup replay-capable rounds 38-42 all have packed
`replay_weekday = 3`, so runtime `+0x2C = 2`. The `> 6` floor branch is
therefore never taken for shipped FA Cup replays. Their exact live replay date
is simply **the current match-completion day plus 14 days**.

The later FA Cup rounds have packed replay `0/0` and are decisive rather than
replay-producing. League Cup one-off NormalRounds are likewise decisive, while
its TwoLeg rounds already use the packed replay week/day as the startup
SecondLeg date.

### Replay trigger

At `0x51391B`, an unlinked normal `CupMatch` calls its shared result virtual
`+0x44 -> 0x514000`. A non-null club follows the resolved-round path. A null
result falls directly into the replay constructor path.

There is therefore no additional guessed replay-eligibility switch at
completion time. A source-configured normal match that remains unresolved
creates the replay; a source-configured decisive normal match resolves instead.

This closes the date/input dependency required for clean-room dynamic FA Cup
Replay insertion without treating packed `replay_week/replay_weekday` as a
generic replay date.


## Constructor-policy closure and fixed-League calendar boundary

Commits `71d1d65ffb62f10d8e80a6cd30bf30422a11880d` and
`4eb97457d0e4b6a00cd9a2e85d342e218670e675` close the previously-open
CupMatch constructor-policy producer.

The packed DBRRound fields now materialized by the clean-room are:

- packed word +28 -> runtime round +0x24 source / extra-time-capability input;
- packed byte +30 -> the auxiliary input ORed into the same recovered
  constructor capability;
- packed byte +31 -> decisive tie-break input.

The scheduled Cup node carries those recovered values directly. FirstLeg
forces all three policy booleans false; SecondLeg inherits the round's
extra-time capability and forces the decisive bit, matching the constructor
trace already recorded above. Synthetic round stubs that predate these fields
default them to false only for isolated compatibility tests.

### Remaining calendar contradiction

The remaining pre-execution blocker is no longer a Cup date conversion question.
It is the exact date pair passed by the fixed-League builder
`0x6173D0` into `0x615950`.

Current source-backed/live facts conflict if one assumes that builder passes the
raw DBRRound week unchanged:

- live Premier League conversion maps packed round `8/3` to
  **Wednesday 23 August 2000**;
- source-exact League Cup conversion maps packed round `7/3` to the same
  Gregorian date;
- raw primary-container arithmetic gives different indices:
  `7*8+3-1 = 58` versus `7*7+3-1 = 51`.

A single primary schedule container cannot make bucket 58 and bucket 51 the
same day. Therefore at least one additional fixed-League transformation or
argument adjustment exists between DBRRound state and `0x615950`, or the
older live PL date helper encodes a non-executable calendar convention.

Exact next trace: inspect `0x6173D0` at its `0x615950` call site and prove
the two date arguments, including any week decrement/normalization performed
before the call. Preserve the Cup anchor and the verified post-shuffle bucket
order while this is unresolved.


## Fixed-League date argument closure

Recovery generation 63 re-materialized the authorized disc image and verified
the canonical root `FOOTBAL.EXE` SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

The previously-open fixed-League date transform is now instruction-closed.

At `0x4F4500` (League::AddRound):

- runtime DBRRound byte `+0x18` is copied unchanged into the first dword of
  the 8-byte `League+0x60` date entry;
- runtime DBRRound byte `+0x19` is decremented once and stored as the second
  dword, i.e. source weekday becomes zero-based;
- no week decrement occurs.

At fixed builder `0x6173D0`:

- the outer round index is multiplied by 8;
- `League+0x60 + 8*round_index` is pushed directly;
- `0x4F3B50` selects the schedule container;
- `0x615950` is called with that exact date-entry pointer.

Therefore a Premier League packed date `8/3` reaches `0x615950` as
`(8,2)`; the clean-room's older Monday-containing-July-1 convention cannot
be an executable transformation hidden inside the fixed builder.

The primary container anchor is independently confirmed at
`0x6169F0 -> 0x64CC70`. Mode 0 passes year code 100 (2000) and constructs
July 1 before advancing to the next date satisfying the helper's Monday
alignment. For 2000 this is Monday **3 July 2000**.

Consequences:

- primary-container source `7/3` -> Wednesday **23 August 2000**;
- primary-container source `7/6` -> Saturday **26 August 2000**;
- primary-container source `8/3` -> Wednesday **30 August 2000**;
- the existing Premier League `season_weekday_date` helper is seven days
  early for the shipped 2000/01 season;
- the same correction moves the actual 2000 Christmas-Day source pair from
  the clean-room hard-coded `26/1` to **`25/1`** for the
  `0x615950` Christmas skip.

Next implementation step: unify the live Premier League date conversion with
the proven primary-container anchor, correct the Christmas placement constant,
then rerun the canonical primary schedule audit before enabling shared PL/Cup
execution.


### Calendar correction validation

The clean-room implementation now uses the same executable-backed primary
calendar for fixed League and Cup nodes. Commit `1b388b66` restored the
suite to its prior baseline: 710 tests with only the two known secondary
scheduler failures, while asset policy passed.

Canonical Static.dat contains no round with scheduled or replay/second-leg
pair `25/1` or `26/1`. The corrected Christmas-Day branch is therefore
startup-neutral for the shipped primary schedule: no one of the 9,346 nodes
changes bucket because of this correction.

The remaining Gate-12 work is execution, not date reconstruction.


### Cup AI strategy context

The `0x409500 -> 0x409680` Cup formation context is now instruction-closed.

- `Cup+0x3C` = total runtime round count.
- `CupMatch+0x50` = zero-based current round index.
- Thus `rounds_from_final = total_rounds - zero_based_round_index`.
- With one-based Static.dat round numbers this becomes
  `scheduled_matchday_count - round_number + 1`.
- Runtime competition precedence is `-initialization_order_value`.

This feeds the existing exact `cup_round_strategy_bias()` helper. Linked
Replay/SecondLeg objects can additionally use the already-recovered aggregate
deficit term.

The next execution blocker is not strategy. It is match duration:
`simulate_normal_match()` currently hard-codes the 90-minute phase plan, while
decisive Cup runtime objects may require extra time.


### First live AI Cup execution

`e45c02da` verifies the first domestic-Cup match that is actually scored by
the shared reconstructed MatchCalculator and completed into the Cup result
registry.

Decisive Cup objects now use the existing recovered extra-time phase plan
through minute 120. Replay/SecondLeg tie resolution continues to use the
already-closed Cup completion lifecycle.

This bridge is intentionally not mislabeled as full post-match integration.
The current method syncs MatchCalculator Condition and home pitch wear, but
PL-specific incident/suspension scheduling, gate receipts and morale/Form are
still separate follow-on work.


### Shared post-match incident branch

Direct tracing of canonical `FOOTBAL.EXE` closes an important post-match
boundary.

The shared match execution routine at `0x511370` calls `0x5127A0` when:

- match flag byte `+0x44` does not carry the separate `0x20` suppression
  bit; and
- `0x5112E0` returns false.

`0x5112E0` calls the owning competition virtual `+0x30`, already mapped as
the primary/secondary schedule-container selector. English FA Cup and League
Cup use the primary container, and `CupMatch` constructor `0x510520` does
not set the `0x20` suppression bit. Domestic Cup matches therefore enter the
same `0x5127A0` card/injury persistence routine as primary League matches.

Inside `0x5127A0`, the next-fixture source is also shared:

1. global current relative schedule day is incremented by one;
2. `0x510300` selects the match's primary/secondary schedule container from
   match state;
3. `0x615D10` scans that container forward for a matching team;
4. the resulting match/date context is passed to player routine `0x419680`
   when suspension state is refreshed.

Therefore the remaining clean-room blocker is not Cup-specific discipline
rules. It is faithful representation of the **whole primary container** when
computing the next team fixture. Restricting that lookup to PL + domestic Cups
would be incomplete for clubs participating in other primary competitions.
