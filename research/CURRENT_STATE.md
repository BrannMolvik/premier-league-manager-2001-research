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

Latest Gate-12 implementation checkpoint:

```text
4eb97457d0e4b6a00cd9a2e85d342e218670e675
Keep synthetic Cup schedule stubs compatible
```

The last fully recorded CI checkpoint remains `ccac3ba2` (710 tests, two
known secondary-schedule failures). Commits `71d1d65f` and `4eb97457`
close the previously-open Cup constructor-policy input without changing the
primary schedule RNG/placement model.

GitHub Actions at that checkpoint:

- reconstruction suite: **710 tests run, 2 failures**, both the unchanged
  pre-existing secondary-schedule assertions;
- the post-placement/post-shuffle domestic-Cup date/order bridge regressions
  passed;
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
  NormalRound completion, including controller save/reload persistence;
- canonical controller construction now retains the verified post-shuffle
  primary buckets and installs FA Cup / League Cup live state from them;
- Cup dates now apply the exact `0x615950` placement displacement to the
  separately recovered Cup source-date convention, including the Christmas
  skip, while same-day Cup order is preserved from shuffled bucket
  head-to-tail traversal.

The normal human/AI matchday loop still remains Premier-League-only. One
important boundary remains explicit: the repository currently has different
recovered source-week conventions for fixed Premier League fixtures and Cup
rounds even though both occupy the primary container. Therefore a universal
primary-bucket-to-Gregorian-date mapping must not be invented merely to merge
their same-day order.

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

1. Preserve the verified post-shuffle domestic-Cup schedule bridge through
   `ccac3ba2`; do not reopen solved Cup draw, replay-date or placement work.
2. The match-constructor policy input is now closed. `71d1d65f` parses the
   packed round fields at offsets 28..31 and carries their recovered policy
   values into scheduled Cup nodes; `4eb97457` keeps older synthetic schedule
   stubs compatible. Do not reopen this trace unless new contradictory evidence
   appears.
3. The fixed-League date argument is now instruction-closed. `0x4F4500`
   copies packed DBRRound week unchanged and weekday-1 into `League+0x60`;
   `0x6173D0` passes the selected 8-byte entry directly to `0x615950`.
   There is no hidden week decrement. `0x6169F0 -> 0x64CC70` gives the
   primary container the first Monday on or after July 1 as its anchor.
   Therefore the older clean-room Premier League helper is seven days early
   in 2000/01 and must be corrected to the same primary-container convention
   already used by Cups.
4. Correct the shared PL date conversion and the canonical Christmas-Day
   placement boundary before merging execution. With the executable anchor,
   Christmas 2000 is source `25/1`, not `26/1`. Re-run the canonical
   primary schedule audit after this correction and refresh any affected
   bucket digest/order checkpoint before enabling shared PL/Cup matchdays.
5. Then merge due FA Cup / League Cup matches into the shared AI/human calendar
   path and add deterministic AI-only, human-involved, Replay and TwoLeg
   save/reload regressions.

## Known live fidelity boundaries

- Gate 12: FA Cup/League Cup nodes, definitive outcomes, completed-node
  identities, persisted Cup match-score/link state, dynamic FA Cup Replay
  insertion and the post-placement/post-shuffle domestic schedule bridge are
  GameState/save safe. Automatic constructor-policy derivation and actual
  shared human/AI Cup execution remain open. The constructor-policy producer
  is closed; the remaining calendar blocker is the exact fixed-League
  primary-container calendar correction and its Christmas placement audit.


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
