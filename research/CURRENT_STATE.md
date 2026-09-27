# Current State

_Last reconciled: 28 September 2026_

This is the **canonical live resume point**. Historical chronology belongs in
`PROGRESS.md`; established technical evidence belongs in `FINDINGS.md` and
topic-specific research files.

## Current gate

**Gate 10 - Finances and board systems**

Gates 1 through 9 are complete.

Gate 9 closed after the modern runtime gained persistent contract/transfer
state, live human cash bids and player terms, safe scheduled transfer
completion, a callable human transfer workflow, and the recovered Saturday AI
acquisition path.

Evidence: `research/GATE9_TRANSFERS_AND_CONTRACTS.md`.

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

Latest verified Gate-10 **code** checkpoint:

```text
3fc54ed8524fabade0f37be7017f84d5e967a279
Test gate secondary debits as doubles
```

GitHub Actions at that checkpoint:

- reconstruction suite: **533 tests passed**;
- repository asset-policy workflow: **passed**.

Current internal save schema: **10**.

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

## Gate 10 goal

Make money and board constraints materially affect management.

Roadmap completion requires:

- club cash/balance represented;
- wage and transfer budgets represented;
- match and recurring income/cost paths integrated;
- player wages and transfer spending/income persisted;
- board expectations/job-security behavior integrated where recovered;
- remaining approximations explicitly labeled.

## Gate 10 strongest known evidence

Existing reverse engineering already establishes:

- DBRUser owns six Balance pointers at `+0x670..+0x684`;
- current cash is the qword at active Balance `+0x10`;
- transfer buyer debit is `0x404B30 -> 0x5DC650`;
- transfer seller credit is `0x404BB0 -> 0x5DC510`;
- controlled-club affordability check `0x404AE0` compares against the same
  current-cash value;
- transfer postings use accounting category 1000;
- current cash and the legacy chairman transfer-budget message concept are
  separate;
- `EAMchairbudgetsettings +0x58` is the displayed transfer-budget payload
  field, but the A0/A1/settings/warning budget-event family has no mapped
  ordinary fresh-game producer;
- its generic factory route is DBRUser save/load deserialization only;
- named budget-default globals have loader writes but no recovered live
  consumer;
- normal Finance Overview and Transfer UI have no reference to this chairman
  budget family and instead use live Balance/accounting state;
- the concession subsystem contains an exact monthly category-300 Balance
  credit path, but the recovered fresh-game generator never activates a
  persistent record, so it is dormant/legacy state rather than an ordinary
  live income producer;
- live match-day receipts are now instruction-located at
  `0x513252 -> 0x5DA2F0 -> 0x5DC510`: categories 1 and 2 combine the two
  DBRUser `+0x694 +0x08/+0x0C` ticket prices with recovered attendance-count
  components; high-level category 0 sums categories 1+2+3 and category 3 is the
  separate ticket/season-ticket sale path;
- ticket `+0x08` paired with stadium-entry `+0x1C` is the terrace class,
  while ticket `+0x0C` paired with stadium-entry `+0x28` is seating;
- the four home/visiting × terrace/seating demand cells, ticket-price response,
  fan-base/capacity caps, truncation and randomized subtraction inside
  `0x5DA2F0` are instruction-locked, and the ordinary/type-6 upstream
  side-modifier helpers `0x5DBA60/0x5DBCD0` are now translated as well;
- the source formats behind `+0x694/+0x6B0` are instruction-locked and
  materialized by the modern runtime: the original per-club `.MAP` supplies
  the 40×40 building grid and per-instance flags, 26 fixed stadium anchors
  recover the ticket sections, and the original WAD member
  `Lists\\Buildings.dat` supplies the 3,000×0x74 live building records used
  by capacity helpers;
- normal Premier League gate integration is now live: PL FanFactor is 0.5,
  EPBase gives 30.0 seating / 22.5 terrace reference prices, fresh controlled
  facility factor is exactly 0.90, pre-result side modifiers are source-backed,
  and four gate RNG draws are consumed after MatchCalculator but before
  incident/Form RNG for every normal league fixture; category 1/2 receipts are
  posted when the controlled home club has a materialized Balance/ticket state;
- original Balance credit `0x5DC510` constructs a category-1600 debit at
  exact floating amount `incoming * 0.002`, with no integer conversion before
  debit; the clean-room Balance now preserves this fractional posting and
  schema-10 saves preserve fractional cash/ledger state. Finance Overview
  queries category 1600, but its user-facing label remains deliberately
  unresolved.
- fresh DBRUser Balance objects are constructed at zero, then initializer
  `0x425680` copies the controlled club's `Master.dat` float64 at packed
  +165 through runtime `DBRClub +0xD0/+0xD4` into active Balance +0x10;
  the modern canonical human-club selection path now mirrors this source-backed
  initialization;

## Exact next task

1. **Completed:** clean-room Balance/current-cash runtime object.
2. **Completed:** Gate-9 affordability callback removed; controlled purchases
   now test live current cash.
3. **Completed:** completed transfer buyer debit / seller credit posts category
   1000 and persists through internal save schema 9.
4. **Completed:** deterministic insufficient-funds and equal debit/credit
   regressions; CI at `80bc0313` passed **492 tests**.
5. **Completed research boundary:** no mapped ordinary fresh-game producer or
   Finance/Transfer UI consumer exists for the separate chairman
   transfer/wage-budget event family. Treat it as legacy/persistence-compatible
   unless new executable evidence proves an active store; do not invent one.
6. **Completed:** weekly player payroll is integrated on the recovered
   Saturday cadence using stored weekly wages, loaned-in exclusion and
   category-101 Balance postings. The first-of-month support-staff path is
   recovered as category 102 but concrete amounts remain deferred until the
   original CSupportStaff cost state is materialized.
7. **Completed:** normal Premier League gate receipts are integrated through
   the recovered source-backed stadium/ticket state, FanFactor, reference
   prices, side modifiers, four-draw RNG ordering and category-1/category-2
   Balance postings. CI at `0d3010df` passed **531 tests**.
8. **Completed:** Balance credit `0x5DC510`'s secondary
   category-1600 debit is integrated as an exact floating
   `incoming * 0.002` posting, with debit-before-primary ledger order and a
   rounding-sensitive regression. Internal save schema 10 preserves fractional
   finance values. CI at `3fc54ed8` passed **533 tests**.
9. **Completed:** fresh controlled-club starting cash is sourced from
   `Master.dat` club +165 (runtime DBRClub +0xD0/+0xD4) and materialized when
   canonical human club control is selected. Arsenal starts at 28,000,000 and
   Manchester United at 34,000,000 in the shipped data. The explicit cash setter
   remains only as a deliberate override/test hook.
10. **Active:** close the finance-linked board/job-security path at
   `0x5E1D90`: recover the stored Balance financial-objective target,
   `ChairmanPercentBudgetMiss` tolerance, evaluation cadence/state transition,
   and reason-5 sacking outcome that feeds `EAMManagerSackedFailedBudget`.
   Implement only the proven financial-objective behavior; do not substitute the
   dormant chairman quarterly-budget message family.
11. **Concession trace resolved for current Gate-10 purposes:** `0x5E56F0`
   returns the active record's `+0x160` qword, `0x5E5640` posts category
   300 on day-of-month 1, but `0x5E5330` never appends its generated stack
   candidate or increments the fresh-game active count. Leave normal concession
   income disabled unless a genuine activation writer is later recovered.
12. Do not infer attendance from unmapped `DBTAccessFanBase` fields merely
   because the table is already parsed. The original 26-section stadium state
   and stadium capacity/entry model are separate dependencies.

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

Unless required to unblock Gate 10, defer:

- broader management systems beyond finance/board dependencies;
- broader competition season-transition behavior;
- original save-file compatibility;
- full original UI fidelity;
- FastView/3D.

Record useful side leads in `research/BACKLOG.md` instead.
