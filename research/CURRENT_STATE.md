# Current State

_Last reconciled: 30 September 2026_

This is the **canonical live resume point**. Historical chronology belongs in
`PROGRESS.md`; established technical evidence belongs in `FINDINGS.md` and
topic-specific research files.

## Current gate

**Gate 12 - Other competitions**

Gates 1 through 11 are complete. Gate 11 closed on 29 September 2026 after the
deterministic 38-round / 380-fixture human-manager season regression and its
completion audit. Gate 12 has completed the main live English domestic-cup and European bridges
and now has the source-backed English regular-season divisional LeagueMatch set
live as well. The remaining special domestic-Cup ticket-posting branch is
explicitly deferred as a fidelity/source-access gap rather than guessed.

Evidence:

- `research/GATE11_COMPLETION_AUDIT.md`
- `research/GATE12_ENGLISH_DOMESTIC_CUPS.md`
- `research/GATE12_EUROPEAN_COMPETITIONS.md`
- `research/GATE12_ENGLISH_DIVISIONS.md`
- `research/GATE12_ENGLISH_SEASON_TRANSITION.md`

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
e0a69e8e0d65b9549363e90ace8ee6e68fe74e67
Test qualification Cup primary due routing
```

GitHub Actions at that checkpoint ran **818 tests with 2 failures**, exactly
the unchanged known secondary-schedule assertions. Qualification-only Cup
entries now participate in the autonomous primary due-entry router; annual
source-continuity and state/RNG transaction regressions also pass, and
repository asset policy passed. The European runtime bridge is now covered end-to-end: live child
groups publish type-2 standings and source-backed type-3 cross-group pools,
Champions League / UEFA Cup knockout nodes execute through the shared CupMatch
runtime in canonical primary order for AI and human control, and a real
type-3 Champions-League-group -> UEFA knockout dependency survives save/reload.

Internal save schema is now **34** and additionally preserves the separate
annual-qualification Cup owner. European Cup schedules, live procedural-League
fixtures/results, type-2/type-3 rankings, club-competition membership, domestic
Cup state, and qualification-Cup state all survive reload.

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

1. Preserve the now-verified annual transaction: live qualification is captured
   before membership swaps, English LeagueAllocation movement is previewed
   without mutation, annual materialization runs on a cloned controller
   match_rng, and GameState plus the live CRT state commit only after the full
   replacement validates.
2. Make the **complete canonical annual qualification snapshot** available
   through a real season. Canonical type-3 ranking sources are now partitioned
   into played Leagues `(0, 17, 21, 27, 31, 40, 50, 54)` and 44
   DummyLeagues. The played sources are already included in canonical live
   procedural-League coverage.
3. Preserve the verified startup/current-season DummyLeague rankings already
   published from lazy-sort output. Do not consume extra RNG or re-sort a
   DummyLeague merely to populate rollover state.
4. Preserve all ten required annual Cup sources
   `(1, 5, 9, 10, 19, 23, 33, 91, 98, 101)` in their live domestic,
   European, or qualification-Cup owners through their finals. Their exact
   `(winner, loser)` final pair is now exposed without rebuilding draw logic.
5. Close the remaining autonomous-season scheduler boundary for dynamically
   inserted FA Cup replays. The exact replay date and `0x615A60` insertion
   call are source-backed, but the repository does not yet prove same-day
   insertion order after the initial primary bucket shuffle. Do not invent
   append/prepend ordering.
6. Once replay insertion order is source-closed, run the real canonical primary
   season until every required played-League ranking and Cup final pair is live,
   capture the complete qualification snapshot, then execute promotion/relegation
   -> annual materialization -> atomic replacement. Verify the regenerated
   year-two primary runtime keeps all played annual qualification-source Leagues
   live. Missing qualification sources must remain an explicit failure, never a
   shipped historical fallback.

## Known live fidelity boundaries

- Gate 12: FA Cup/League Cup execution and save state are source-backed and
  verified. Schema **31** preserves the full-primary shadow, Cup outcomes,
  live procedural-League fixtures/results and per-competition/context position
  rankings. Shared `0x5127A0`
  discipline/injury and `0x404CE0` morale/Form are integrated behind the
  exact-or-pending shadow guard. English Cup attendance policy inputs are
  source-backed; only the special both-controlled-participants posting policy
  remains deferred. European startup is canonical; group standings, primary-order group execution,
  type-2 progression, type-3 cross-group transfers, Champions League / UEFA Cup
  knockout execution, human routing and save/reload are live and regression
  covered. The regular-season English divisional LeagueMatch set (2/3/4/7) is live,
  ordered and reload-safe. The cross-division annual membership transition is
  also now live and save-persistent: exact source rankings, playoff winners,
  Conference 2, and all 14 English allocation swaps are covered. The annual primary regeneration primitive is also verified: year-two Premier
  League is procedural, current live memberships feed participant selection,
  later-season Christmas placement is calendar-derived, and bucket order is
  freshly shuffled. Cross-season qualification requirements, DummyLeague invalidation/lazy-sort
  timing, primary-root finalization order, and the positional Cup final pair
  are source-backed. Annual primary state replacement is now atomic and
  controller-CRT-owned. All required startup DummyLeague rankings and all ten annual Cup source owners
  are now wired, qualification-only Cups participate in autonomous primary-day
  routing, and annual regeneration preserves every played qualification League
  into the following season. The remaining scheduler blocker is dynamic FA Cup
  Replay insertion into the post-shuffle primary execution order: replay date
  and construction are exact, but `0x615A60` same-day insertion order is not
  yet documented. After that is closed, the active Gate-12 proof is the real
  canonical full-season qualification snapshot and atomic year-two rollover.


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

Unless required to unblock the active Gate-12 next-season regeneration, defer:

- original save-file compatibility;
- Gate-13 original management presentation;
- Gate-14 audio/match presentation and FastView/3D;
- later fidelity/long-duration/release gates.

Record useful side leads in `research/BACKLOG.md` instead.
