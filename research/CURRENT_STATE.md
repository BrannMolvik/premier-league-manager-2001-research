# Current State

_Last reconciled: 29 September 2026_

This is the **canonical live resume point**. Historical chronology belongs in
`PROGRESS.md`; established technical evidence belongs in `FINDINGS.md` and
topic-specific research files.

## Current gate

**Gate 12 - Other competitions**

Gates 1 through 11 are complete. Gate 11 closed on 29 September 2026 after the
deterministic 38-round / 380-fixture human-manager season regression and its
completion audit. Gate 12 is now connecting the already-recovered generic
competition runtime to live English domestic cups before expanding to Europe
or the remaining league/divisional structures.

Evidence:

- `research/GATE11_COMPLETION_AUDIT.md`
- `research/GATE12_ENGLISH_DOMESTIC_CUPS.md`

## Porting mission

This is a **Windows 11 modernization/port**. The supplied FM2001 archive/disc
contents are authorized for project use. Original FM2001 resources and
recoverable original behavior are the default source of truth. Use them
directly, convert them, or wrap them as needed; do not replace or redesign them
for convenience. Replacement is only justified when the original is
technically incompatible with the Windows 11 runtime after reasonable
adaptation, or genuinely inaccessible/unrecoverable from the authorized source.
Legacy runtime/game code may be reimplemented where direct execution is
incompatible, while preserving recovered original behavior.

Authorized original resources belong under `original_assets/` with provenance
tracked according to `research/ASSET_POLICY.md`.

## Verified repository state

Latest verified Gate-12 code checkpoint:

```text
a41feea2c51bc40d614c59c606467b59680bc040
Test dynamic replay controller save roundtrip
```

GitHub Actions at that checkpoint:

- reconstruction suite: **707 tests run, 2 failures**, both the unchanged
  pre-existing secondary-schedule assertions;
- the source-dated dynamic FA Cup replay insertion and controller save/reload
  regressions passed;
- repository asset-policy workflow: **passed**.

The active Cup slice now has:

- a persistent result-token registry for direct and match-result ClubRefs;
- exact winner/loser selector semantics for referenced Cup matches;
- the shared CupMatch result virtual `0x514000`, including linked reversed-leg
  aggregate totals and its secondary comparison;
- the instruction-closed NormalRound replay and TwoLeg first/second-leg
  lifecycle, including exact decisive fallback ordering;
- `GameState.cup_results` as the live persistent registry;
- a live `DomesticCupScheduleState` over the already-materialized FA Cup and
  League Cup nodes, preserving source date conversion, symbolic ClubRefs and
  first-leg completion identity;
- lazy due-node resolution through the live Cup result registry;
- `GameState.domestic_cups` plus install/due-node helpers that consume no draw
  RNG;
- persistent `CupMatchRuntimeState` objects behind scheduled nodes, including
  completed FirstLeg scores and reconstructed bidirectional FirstLeg/SecondLeg
  linkage after reload;
- internal save schema **25**, which serializes/restores definitive Cup outcomes,
  live domestic schedule/completion state and Cup match score/link state;
- the exact `0x51392A` NormalRound replay-date producer, including the primary
  schedule-container anchor and shipped FA Cup +14-day replay arithmetic;
- dynamic reversed `CupMatchReplay` insertion after unresolved FA Cup
  NormalRound completion, including controller save/reload persistence.

The normal human/AI matchday loop still remains Premier-League-only. The next
bridge must consume domestic Cup nodes from the **post-placement, post-shuffle
primary schedule container**, because conflict placement can move a node away
from its packed source date and the shuffled bucket order is the executable's
same-day execution order.

## Stable startup / scheduler checkpoint

The corrected canonical path through primary schedule finalization remains:

- DBTPlayers startup RNG: **180,384 calls** for 30,064 players;
- synthetic post-youth state: **`0x4B68DE28`**;
- actual-count primary competition RNG: **5,836 calls**;
- state entering primary `0x615BE0`: **`0x4F5CF274`**;
- complete primary schedule nodes: **9,346**;
- primary buckets: **373**;
- primary bucket-shuffle calls: **9,178**;
- state after primary schedule shuffle: **`0xD25DFFE6`**;
- first PL fixture order: **0, 6, 8, 5, 1, 9, 3, 2, 4, 7**.

See `research/STARTUP_WAGE_RNG_CORRECTION.md` and
`research/GATE4_SCHEDULE_ORDER.md`.

## Stable gameplay / save checkpoints

- Gate 6: three deterministic full 38-round / 380-fixture Premier League
  seasons.
- Gate 7: six human-controlled Arsenal fixtures while all surrounding matches
  continued in recovered scheduler order.
- Gate 8: source-bound internal save/reload with exact continuation across a
  mid-matchday boundary.
- Gate 9: human and AI transfer/contract runtime integrated with calendar
  progression.

Evidence:

- `research/GATE6_FULL_SEASON.md`
- `research/GATE7_HUMAN_GAMEPLAY.md`
- `research/GATE8_INTERNAL_SAVE.md`
- `research/GATE9_TRANSFERS_AND_CONTRACTS.md`

Gate-10 live cash-flow trace: `research/GATE10_LIVE_CASH_FLOW_TRACE.md`.

## Gate 12 active slice

The canonical English domestic-cup audit is complete for startup structure:

- competition 1 is the eight-round FA Cup;
- competition 5 is the seven-round League Cup;
- existing Gate-3/Gate-4 code already owns canonical allocation, participant
  shuffle/qsort, knockout pairing, TwoLeg direction, symbolic winner refs and
  schedule-node construction;
- the first live gap was not draw construction, but persistent resolution of
  symbolic Cup results.

That first bridge is now implemented through `reconstruction/cup_progression.py`.
Do not rebuild solved Cup startup RNG/draw behavior.

## Exact next task

1. Preserve the verified Cup startup/draw, persistent match-state, replay-date
   and dynamic replay work through `a41feea2`; do not reopen those solved
   paths.
2. Bridge the already-reconstructed **post-placement/post-shuffle primary
   schedule buckets** into live domestic Cup state so conflict-moved dates and
   head-to-tail `0x615C10` execution order are retained rather than inferred
   from raw packed round dates.
3. Merge due FA Cup / League Cup matches into the normal AI/human calendar
   execution path using the existing shared match backend and
   `CupMatchRuntimeState` completion lifecycle.
4. Cover AI-only, human-involved, replay and TwoLeg progression with
   deterministic save/reload regressions before expanding Gate 12 beyond
   English domestic cups.

## Known live fidelity boundaries

- Gate 12: FA Cup/League Cup nodes, definitive outcomes, completed-node identities,
  persisted Cup match-score/link state and dynamic FA Cup Replay insertion are
  GameState/save safe. Domestic Cup nodes still need to be bound to the
  post-placement/post-shuffle primary container and then executed through the
  shared human/AI matchday loop.


See `research/FIDELITY_GAPS.md`. Most relevant now:

- chairman budget-message payloads remain loadable from legacy event/save
  state, but no ordinary fresh-game producer/consumer is mapped;
- normal Premier League match-day gate income is integrated through the
  source-backed stadium/ticket state, exact fresh prices, side modifiers and
  recovered four-draw RNG placement. The special both-controlled-clubs
  cup/knockout path remains research-only and broader facility-upgrade
  attendance bonuses await the later building system;
- concession payout is intentionally not integrated into ordinary progression:
  its category-300 monthly credit path is exact, but the fresh-game generator
  does not create active records in the recovered executable;
- Balance credit's secondary category-1600 debit is integrated exactly at the
  recovered floating 0.2% rate; only its EA-facing display label remains
  unresolved;
- broader player-negotiation refusal/duration branches remain explicit deferred
  states;
- exact due-transfer ordering relative to same-day fixtures is not yet
  instruction-locked;
- later AI transfer-window toggling, autonomous contract-category source and
  buy-counter lifecycle remain bounded gaps;
- original FM2001 save compatibility remains separate;
- broader competitions, original front-end fidelity and FastView/3D remain
  later gates.

## Do not work on yet

Unless required to unblock the active Gate-12 domestic-cup slice, defer:

- European competitions and remaining English league/divisional structures;
- original save-file compatibility;
- Gate-13 original management presentation;
- Gate-14 audio/match presentation and FastView/3D;
- later fidelity/long-duration/release gates.

Record useful side leads in `research/BACKLOG.md` instead.
