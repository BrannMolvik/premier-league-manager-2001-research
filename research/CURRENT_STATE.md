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
efe8a3039536cda6e7470d0237262d859c6cad03
Test exact weekly training RNG transition
```

GitHub Actions at that checkpoint:

- reconstruction suite: **559 tests passed**;
- repository asset-policy workflow: **passed**.

Current internal save schema: **13**.

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
8. **Active dependency:** materialize the minimum fresh concession/sponsor timer
   runtime needed to preserve the exact shared-RNG interleaving already mapped
   through the third training Saturday in `6822e7ea`. Do not enable recurring
   multi-week training by default until those commercial draws are represented.
9. After live multi-week training is source-backed and verified, audit the next
   Gate-11 management workflow rather than broadening training with guessed UI
   behavior.

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
