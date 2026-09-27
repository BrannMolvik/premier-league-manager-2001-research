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
   primitive is implemented. The remaining blocker is shared-CRT placement:
   lock the secondary schedule-container `0x947AF0 -> 0x616620` RNG stream.
   Its completion state is now proven to be exactly the state entering the
   fresh 200-person support-staff pool generator. Then replay the known pool /
   user-assignment draws through the first `0x425680 -> 0x4D1760` fixed-staff
   initialization.
7. Attach Saturday calendar execution only after that startup quality bridge is
   deterministic on the shared RNG and source-backed.
8. After live weekly training is verified, audit the next Gate-11 management
   workflow rather than broadening training with guessed UI behavior.

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
