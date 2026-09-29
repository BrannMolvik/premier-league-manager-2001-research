# Current State

_Last reconciled: 29 September 2026_

This is the **canonical live resume point**. Historical chronology belongs in
`PROGRESS.md`; established technical evidence belongs in `FINDINGS.md` and
topic-specific research files.

## Current gate

**Gate 12 - Other competitions**

Gates 1 through 11 are complete. Gate 11 closed on 29 September 2026 after the
deterministic 38-round / 380-fixture human-manager season regression and its
completion audit. Gate 12 has completed the main live English domestic-cup bridge and is now
expanding the same recovered generic competition runtime into Europe. The
remaining special domestic-Cup ticket-posting branch is explicitly deferred as
a fidelity/source-access gap rather than guessed.

Evidence:

- `research/GATE11_COMPLETION_AUDIT.md`
- `research/GATE12_ENGLISH_DOMESTIC_CUPS.md`
- `research/GATE12_EUROPEAN_COMPETITIONS.md`

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

Latest verified Gate-12 implementation checkpoint:

```text
867262db85c2955eea56e277718df13773d847cc
Verify completed-group ranking publication
```

GitHub Actions at that checkpoint ran **762 tests with 2 failures**, exactly
the unchanged known secondary-schedule assertions; repository asset policy
passed. Live Champions League child/procedural-League state now materializes
from the persisted full-primary schedule shadow, records group results, and
publishes source-backed ClubRef type-2 rankings only after the complete group
schedule has finished and the proven points / goal-difference / goals-for keys
produce an unambiguous order.

Internal save schema is now **30** and preserves those live procedural-League
fixtures/results alongside the ranking registry. ClubRef type 3, used by the
Champions-League-group-to-UEFA transfer path, remains deliberately unresolved
until its distinct MiniLeague group-position resolver is source-backed.

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
- internal save schema **26**, which serializes/restores definitive Cup outcomes,
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

Premier League and English domestic-Cup human/AI execution now share the
post-shuffle primary matchday order, decisive Cup extra time, save/reload,
post-match persistence, and result-token progression. The next live-world
boundary is European group/competition ranking state, not Cup match duration.

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

1. Preserve all verified English domestic-Cup execution and the completed
   European child-group execution/type-2/type-3 progression work. Do not reopen
   solved draw, replay, TwoLeg, extra-time, calendar, primary-shadow or
   MatchCalculator ordering.
2. European child competition **14/167** LeagueMatch nodes now execute in the
   shuffled primary order through the shared MatchCalculator. The live group
   state records those scores and publishes type-2 positions only after a
   complete exact ranking.
3. ClubRef type 3 is now instruction-closed and integrated. It is **not** a
   type-2 alias: the executable takes one equal position from every sibling
   child League/group, globally sorts those clubs with the League comparator,
   then selects by the decoded ordinal. The clean runtime publishes this
   cross-group pool only when the recovered numeric comparator keys are exact;
   ties that would require the final source-name byte comparison remain pending.
4. Internal save schema **31** persists type-3 cross-group ranking pools.
   Verification at `0864839`: **774 tests**, with only the same two known
   secondary-schedule failures; repository asset policy passes.
5. The active Gate-12 boundary is now to attach European competition **9**
   (Champions League) and **10** (UEFA Cup) knockout CupMatch nodes to the
   existing shared CupMatch runtime and primary matchday controller. Preserve
   their already-canonical symbolic cross-competition refs and post-shuffle
   order; do not reconstruct their startup draw/allocation.
6. After European knockout execution is live, verify save/reload and
   cross-competition progression through a real type-3 UEFA transfer dependency
   before moving to broader competitions.
7. The special English domestic-Cup category-1/category-2 posting policy remains
   a separate fidelity gap. The canonical executable is now available for
   direct tracing, but do not let that side branch displace the active European
   knockout slice.

## Known live fidelity boundaries

- Gate 12: FA Cup/League Cup execution and save state are source-backed and
  verified. Schema **31** preserves the full-primary shadow, Cup outcomes,
  live procedural-League fixtures/results and per-competition/context position
  rankings. Shared `0x5127A0`
  discipline/injury and `0x404CE0` morale/Form are integrated behind the
  exact-or-pending shadow guard. English Cup attendance policy inputs are
  source-backed; only the special both-controlled-participants posting policy
  remains deferred. European startup is already canonical; group standings, primary-order group
  execution, type-2 progression and type-3 cross-group transfer resolution are
  live. The active gap is European knockout attachment to the shared CupMatch
  controller.


See `research/FIDELITY_GAPS.md`. Most relevant now:

- chairman budget-message payloads remain loadable from legacy event/save
  state, but no ordinary fresh-game producer/consumer is mapped;
- normal Premier League match-day gate income is integrated through the
  source-backed stadium/ticket state, exact fresh prices, side modifiers and
  recovered four-draw RNG placement. English Cup attendance policy inputs and
  RNG placement are integrated, but the special both-controlled-participants
  posting policy remains unresolved because the canonical binary source is not
  currently accessible through connected storage;
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

Unless required to unblock the active Gate-12 European slice, defer:

- remaining English league/divisional structures after the active European bridge;
- original save-file compatibility;
- Gate-13 original management presentation;
- Gate-14 audio/match presentation and FastView/3D;
- later fidelity/long-duration/release gates.

Record useful side leads in `research/BACKLOG.md` instead.
