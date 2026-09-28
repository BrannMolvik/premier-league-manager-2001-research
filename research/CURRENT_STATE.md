# Current State

_Last reconciled: 28 September 2026_

This is the **canonical live resume point**. Historical chronology belongs in
`PROGRESS.md`; established technical evidence belongs in `FINDINGS.md` and
topic-specific research files.

## Current gate

**Gate 11 - Broader management systems**

Gates 1 through 10 are complete.

Gate 10 closed after source-backed cash/Balance, transfer and payroll postings,
normal Premier League gate receipts, exact Balance-credit secondary debit,
financial board objectives, persistent dismissal reasons, and the authentic
single-user control exit were integrated and regression-tested.

Evidence: `research/GATE10_FINANCES_AND_BOARD.md`.

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

Latest verified Gate-11 code checkpoint:

```text
c767083a522a9a5b0bb580ffe31c302d9879147a
Fix live performance history fixture hooks
```

GitHub Actions at that checkpoint:

- reconstruction suite: **629 tests run, 2 failures**, both the unchanged
  pre-existing secondary-schedule assertions;
- all new scouting/performance/history/RNG/live-fixture tests passed;
- repository asset-policy workflow: **passed**.

Current internal save schema: **14**.

Gate 10 now has a clean-room Balance/current-cash runtime slice:
- current cash is represented explicitly and fresh controlled-club Balance cash
  is source-backed from Master.dat club +165;
- controlled-buyer affordability uses that live cash instead of a callback;
- completed transfer purchases debit and sales credit materialized Balance
  objects through category-1000 ledger postings;
- Balance cash and ledger state survive save/reload.

Canonical executable SHA-256:

```text
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3
```

The authorized disc image was re-materialized during the Gate-9 closure audit
and the extracted executable reverified against that hash. Raw extraction data
remains outside Git.

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

## Gate 11 goal

Complete the core management-game loop around the stable Premier League
simulation, finance, transfer, save/load, and human-matchday backend.

Targets include:

- training/development workflows;
- scouting;
- youth;
- morale;
- medical/injury management;
- discipline;
- messages/news;
- recurring manager tasks.

## Gate 11 strongest starting position

Several target systems already have substantial research or backend behavior:

- player monthly development/aging and the seven training profiles are deeply
  reconstructed and tested, but the human-facing training workflow has not yet
  been audited as a complete management loop;
- injury generation/return and discipline/suspensions already function through
  full Premier League seasons;
- youth generation is part of the recovered startup RNG chain;
- scouting has identified deterministic search RNG behavior but is not yet a
  complete human workflow;
- messages/news and recurring management tasks are much less integrated.

## Exact next task

1. **Gate 10 COMPLETE:** see `research/GATE10_FINANCES_AND_BOARD.md`.
2. **Gate 11 training slice verified:** RuntimePlayer now persists the original
   fresh method (**5 = Fitness**), eight-week countdown, active count, 17
   per-skill counters/states and seven method result counters. Human managers
   can change a player method without resetting accumulated state, and save
   schema 13 preserves the training record.
3. **Weekly eligibility resolved:** Saturday active training skips injured
   players and the separate selection-exclusion bit 2; ordinary suspension does
   not block this path.
4. **Weekly RNG boundary resolved:** `0x4EACE0` consumes one RNG(100) only
   for nonzero profile weights in slots 0..16; method draw counts are
   0/4/4/5/5/6/5. Its timed-effect prepass consumes no RNG, and later
   condition/injury logic is a different function.
5. **Weekly transition implemented and verified:** the explicit-quality
   primitive reproduces exact profile draws, +8 gains, countdown-zero -8
   reversals and eligibility skips without altering calendar progression.
6. **Active dependency:** fresh staff types, ratings, employed-list ownership
   and Training Centre absence are resolved and the exact training-quality
   primitive is implemented. The full secondary schedule leaves
   **`0x61D6DFA2`**. The cleared 200-person generic staff pool plus two
   immediate candidate rebuilds leave **`0x1D1A278D`**. Fresh startup
   weekly-aligns July 1 forward before the first `0x4A8070`, so its
   day-of-month-1 branch is skipped. The first Arsenal/user phase of
   `0x6194D0` consumes exactly 38 draws and leaves **`0xDFCED283`**.
   The global player scan then leaves the fresh transfer-candidate list empty;
   the 895-club vector is source-backed, so the first two `0x619DC0` calls
   consume exactly 894 draws each and leave **`0xBD5CC00F`**. The reverse
   `0x61991F` transfer-list loop is bounded to exactly **894 club visits**
   and 894 mandatory RNG(10) dispatch draws; its 1000-player cap cannot stop
   the fresh loop early. Nested RNG is mapped: `0x61A9A0` has no direct RNG
   beyond its final rating-dependent `0x417470` check, while `0x4050F0`
   performs up to 20 attempts with RNG(10) + one roster-index draw per attempt
   plus the optional rating draw. Fresh roster order used by `0x4050F0` is
   executable-proven as canonical player-table order.

   **Bounded-RNG correction:** the instruction-level qsort semantics remain
   correct, but the selector replay committed after that audit accidentally
   used Python-style modulo for bounded CRT draws. This is not FM2001
   behavior. Direct executable inspection proves both `0x619DC0` and
   `0x61991F` call `0x64D540`, whose exact result is
   `floor(rand15 * bound / 32768)`; the repository's
   `MsvcCrtRng.randbelow()` already implements that formula correctly.
   Consequently the modulo-derived twice-shuffled vector beginning
   `488, 439, 509, ...`, the reverse sequence beginning club 805, and all
   selector visits/states subsequently derived from those bounded values are
   **superseded and must not be continued**.

   Replaying the corrected literal `0x668DA4` qsort with the exact scaled
   `0x64D540` shuffle from `0xDFCED283` still reaches the draw-count
   checkpoints **`0xC6B73181 -> 0xBD5CC00F`**, but the twice-shuffled
   vector instead begins **`25, 738, 783, 262, 812, 2, 397, 819, ...`**.
   Canonical reverse visits therefore restart
   **`118, 750, 510, 1216, 430, 622, 877, 243, ...`**. The first dispatch
   from `0xBD5CC00F` is scaled RNG(10)=3; Carlisle/Steve Soley's subsequent
   rating draw is scaled RNG(100)=82 (not modulo-derived 88), still passes
   the <=50 threshold, and leaves **`0x6A346701`** after visit 1.
   The exact replay helper is now durable at
   `tools/replay_gate11_transfer_list.py`. Its committed Git blob is
   byte-for-byte identical to the source-backed script that validates both the
   corrected scaled first-40 prefix and, in diagnostic mode, all 40 superseded
   modulo visit/state checkpoints. The full exact scaled replay completes all
   **894** reverse visits, transfer-lists **625** players, and leaves the shared
   CRT state **`0x126CF137`**. This is now the canonical post-`0x61991F`
   fresh transfer-list population boundary.

   **Startup quality bridge corrected:** the loan tail reaches the shipped
   **200-player loan-list cap** after **292 eligible club visits**, ending club
   **866** at **`0x472F4DFF`**. The following `0x425680` RNG(10) returns
   2 and leaves **`0xA54D70C6`**. Direct canonical-executable audit then
   revealed a previously omitted mandatory call to **`0x5E3FD0`** before
   `0x4D1760`. On the fresh empty list its 37-way factory accepts 12 selector
   values **33, 8, 12, 22, 2, 3, 27, 5, 0, 23, 28, 18** with no retry and
   leaves **`0x418CAA72`**. Only after that do the six fixed support-staff
   records (types 1, 2, 3, 4, 5, 13) consume RNG(25)/RNG(2) age/rating pairs.
   The fresh Youth Team Coach (type 3) therefore has rating **2**, fresh
   training quality is **1.30**, and the true post-`0x4D1760` shared CRT
   state is **`0xFA1C595E`**. The earlier interpretation of
   `0x418CAA72` as post-fixed-staff state is superseded.

   **Post-staff daily bridge CLOSED:** the interval is RNG-bearing but now
   replayed exactly. Fresh concession and no-sponsor timers consume
   `RNG(14)=4` and `RNG(7)=6`, producing waits 11 and 13. The fresh
   Arsenal user has 37 active training records; all begin Condition 80 and take
   the source-backed `0x61C580` recovery path for seven daily passes before
   first active Saturday training. Daily draw counts are
   **111, 111, 111, 111, 111, 126, 142**. The exact shared CRT state entering
   the first `0x42AE40 -> 0x61CBA0 -> 0x61C520 -> 0x4EACE0` is
   **`0x216C6081`**; final Condition range is **86..93**, sum **3342**.
   `0x61D710` is fresh-empty, `0x6596D0` is a no-op, and the other
   audited pre-weekly calls add no RNG on this boundary. Durable regression:
   `tools/replay_gate11_training_bridge.py`.
7. **Calendar integration checkpoint:** configured user training is now part of
   normal `GameState.advance_one_day()` progression. The hook preserves the
   proven daily-recovery-before-Saturday-training order and remains opt-in so
   unresolved neighboring scheduler state cannot silently alter the shared RNG.
   Commits `b62665d8` / `ddab924a`; both new calendar-integration tests pass.
   Full CI at `ddab924a` ran 576 tests and still has only the two pre-existing
   secondary-schedule assertion failures already recorded at `6809b70f`.
8. **Commercial replay corrected:** `6822e7ea` incorrectly charged RNG to
   Arsenal selector slots whose `0x65DBC0` capacity is zero. Direct
   `0x5E5330` audit proves those slots jump to the next selector before
   `0x5E5170/0x5E5230`. Corrected day-11 concession cost is **104 draws**;
   day 12 succeeds on selector 3 / candidate 19 after **53 draws**. Corrected
   second weekly pre/post states are **0x509630B6 -> 0xA3C5013C** and third
   weekly states **0x7B8D5F58 -> 0xE176B24E**. Durable replay:
   `tools/replay_gate11_commercial_training.py`.
9. **Commercial integration verified:** GameState now uses live stadium,
   club and AccessFanBase state for concession selection and runs commercial
   maintenance before daily/weekly training. CI at `4c560cb3` runs 585 tests
   with only the same two pre-existing secondary-schedule failures.
10. **Sponsor timer closed:** `0x617C80` contains no hidden offer-selection
   RNG. It only selects the sponsor/no-sponsor wait range, draws a wait when
   zero, and resets timer/date without RNG on expiry.
11. **Save continuity verified:** internal save schema **14** persists the
   configured training inputs, concession/sponsor timers and compact
   concession source snapshot. CI at `c7650cf3` runs 586 tests with only the
   two unchanged secondary-schedule failures.
12. **Scouting workflow in progress:** the first-stage `0x4AE680` filter,
   exact `0x4AF7F0` deterministic reseed hash, primary Fisher-Yates ordering,
   secondary score/cap/shuffle structure and shipped scouting limits are now
   instruction-mapped. A data-free `reconstruction/scouting.py` core implements
   the exact reseed/shuffle and 50-candidate / 20-result caps. CI at
   `c80e3d24` ran **590 tests**; all four new scouting tests passed and only
   the two unchanged secondary-schedule assertions failed.
13. **Scouting result ordering closed:** all six `0x4AEEA0` qsort
   modes are now instruction-mapped and implemented. Modes are surname/first-name
   ascending, age ascending, neutral six-byte-history average descending,
   preferred-position display descending, club name ascending, and player value
   descending. Exact ties fall back to surname/first-name ordering. Original
   labels directly support Name/Age/Position/Club/Value; the mode-2 display label
   remains neutral.
14. **Human scouting action verified:** `run_scouting_search()` composes the
   proven primary filter-output shuffle, optional secondary score/cap/reseed
   stage, and final six-mode sort. `HumanGameplayController.search_scouting_players()`
   exposes that pipeline over live RuntimePlayer state while keeping unresolved
   first-stage panel semantics as an explicit predicate and requiring explicit
   resolvers for the unmaterialized history-average/position-display/value
   inputs only when those sort modes are used. CI at `a859299f` ran **601
   tests**; all new scouting tests passed and only the two unchanged
   secondary-schedule assertions failed. Asset policy passed.
15. **Mapped first-stage scouting filter verified:** the runtime now reproduces
   the exact inclusive age/value gates, mode-15 15..18 age clamp, preferred-
   position-0 broad class mapping, out-of-range class-selector bypass and final
   status-control OR structure. Live `0x4205F0` valuation was corrected to use
   preferred-position-0 class, temporary/current-club division and registered-
   club country. `search_scouting_players_mapped()` derives the source-backed
   player state directly while retaining only genuinely unresolved gates as
   explicit resolvers. CI at `664eb6ab` ran **610 tests**; all new scouting
   and valuation tests passed and only the two unchanged secondary-schedule
   assertions failed. Asset policy passed.
16. **Scouting first-stage semantics narrowed:** direct executable tracing now
   resolves the country-context selector, preferred-position membership gate,
   `ScoutStrengthMin` threshold identity and the scouting-specific
   `0x41E450` loan eligibility shape. Country selector mode 0 requires the
   active club country; mode 1 requires a different country with runtime country
   `+0x18 != 0`; other nonzero modes require a different country with
   `+0x18 == 0`. The optional selector is exact membership in the player's
   three preferred-position IDs. `ScoutStrengthMin` compares against
   `floor((30*byte+128)/255)` from the still-unowned auxiliary per-player
   scouting byte behind `0x876868`.
17. **Scouting materialization completed:** the source-backed country and
   preferred-position filters are live, RuntimePlayer persists bit-12 loan-list
   state, and scouting uses the exact `0x41E450` eligibility reduction. The
   unresolved status bit 7 and auxiliary `0x876868` scouting byte remain
   deliberately neutral rather than guessed.
18. **Six-match performance history completed:** RuntimePlayer persists the
   exact six-byte circular `0x41FB60` history plus count/write index, internal
   saves preserve it, and scouting sort mode 2 now reads the live history
   average instead of requiring a resolver.
19. **Exact match-performance target implemented:** `match_performance.py`
   reproduces the `0x6309D0` target-rating arithmetic, including the three
   runtime-role bands, scorer/secondary-attribution terms, card/Form effects,
   the exact clamp sequence, prior-history continuity clamp, shared-CRT draws,
   and the distinct MatchEngine-RNG low-rating lift. Focused tests at
   `c9c1b948` pass.
20. **Live performance history verified:** all active goal-family secondary
   attribution is instruction-mapped and preserved in ChanceRecord. Open play
   uses finisher primary / carrier secondary; delivered free kicks/corners use
   receiver primary / taker secondary; direct free kicks and penalties use the
   taker in both slots. The exact `0x6309D0 -> 0x630FC0 -> 0x41F9C0`
   finalizer now appends ratings for appeared players before gate/incident/Form
   processing whenever an explicit distinct MatchEngine RNG is supplied.
   `match_engine_rng.py` implements the canonical `0x981BF0` ran1 stream.
   Legacy callers remain unchanged and never alias the shared CRT as that
   separate generator. CI at `c767083a` ran **629 tests** with only the two
   unchanged secondary-schedule assertion failures; asset policy passed.
21. **Scouting status/Strengths dependency closed:** canonical
   localization/control bindings prove panel `+0x76F8` / `player+0x14`
   bit 7 is exactly **Out of contract**. The former `0x876868` "auxiliary
   byte" is the Strengths selector value, where 0 = All and 1..17 address
   `current_raw[0..16]` through `[player + selector + 0x1D]`. The displayed
   conversion is `floor((30*raw+128)/255)`, values below
   `ScoutStrengthMin` reject, and the shipped default at `0x8223F4` is
   **20**. The mapped human scouting action now derives this gate directly from
   live player skills. CI at `dcff0e50` ran **632 tests** with only the same
   two pre-existing secondary-schedule failures; all new scouting regressions
   pass and asset policy passes. Evidence:
   `research/GATE11_SCOUTING_STATUS_AND_STRENGTH.md`.
22. **Live Out-of-contract scouting state completed:** the ordinary non-user
   first-of-month `0x41ABC0` lifecycle is source-backed and implemented with
   its exact 30-day window, one/two `RNG(100)` ordering, rating branches,
   roster/tenure/age/`0x417580` eligibility gates, 12-month renewal and
   mapped state clears. RuntimePlayer persists `out_of_contract`, internal
   save schema 16 preserves it, and mapped scouting now consumes that live
   state without requiring an external resolver. CI at `69e42cdf` ran
   **639 tests**; only the same two pre-existing secondary-schedule assertions
   fail and asset policy passes. Evidence:
   `research/GATE11_OUT_OF_CONTRACT_LIFECYCLE.md`.
23. **Controlled-player ordinary contract lifecycle completed:** source-backed
   `0x41BEE0` ordinary handling is live. Controlled players set Out of
   contract from 21 days before expiry, enter the 112-day assistant-manager
   renewal-suggestion window with exact single `RNG(10)` placement, preserve
   the `+0x164` suggestion latch and exact ordinary/Bosman event kinds, run
   mapped expiry cleanup, and detach only at 21 days past expiry. The unified
   first-of-month contract pass preserves club/roster RNG order and active-loan
   branch ownership. Internal save schema 18 preserves controlled contract
   state and queued renewal mail. CI at `391d0845` ran **654 tests** with
   only the same two pre-existing secondary-schedule failures; asset policy
   passed. Evidence: `research/GATE11_CONTROLLED_CONTRACT_EXPIRY.md`.
24. **Special contract sentinel bounded/deferred:** exhaustive DBRPlayer xrefs
   found no proven fresh-game writer that sets `player+0x138 = 0xFE`.
   Constructor zero, save/load serialization and `0x41BEE0`'s own
   `0xFE -> 0xFF -> 0` transitions are direct; the retire/testimonial
   transfer-refusal paths do not access the byte. The special expired branch
   is instruction-bounded to canonical `!Spare` recycle behavior but remains
   neutrally named and compatibility-only until a producer is proven.
25. **Fresh human youth slice verified:** the separate DBRUser youth list
   is materialized with its 20-record cap, exact candidate/name RNG ordering,
   live generated player identity, neutral status bit 3, promotion/release
   roster transitions and youth training-state copy. Multi-user candidate scans
   now exclude prior users' bit-3 youth before the 512-entry cap. Internal save
   schema **21** preserves both mutable generated identity and immutable source
   identity plus the youth records/training state. CI at `20300c8b` ran
   **662 tests** with only the same two pre-existing secondary-schedule
   failures; asset policy passed. Evidence:
   `research/GATE11_YOUTH_WORKFLOW.md`.
26. **Active youth dependency:** resolve the lifetime and exact final state of
   the second initializer `0x425680 -> 0x61DE40`. It clears the youth list,
   generates a first cohort, applies `0x61DD30`, generates a second cohort,
   assigns a common `player+0x154` date and resets each record's training
   state. Bound the `0x4A8070/0x425680` caller chain before classifying this
   as one-shot/seasonal/recurring, then integrate only the source-backed cadence
   and two-cohort RNG/state transitions.

## Known live fidelity boundaries

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

Unless required to unblock Gate 11, defer:

- systems outside the active Gate-11 management-workflow slice;
- broader competition season-transition behavior;
- original save-file compatibility;
- full original UI fidelity;
- FastView/3D.

Record useful side leads in `research/BACKLOG.md` instead.
