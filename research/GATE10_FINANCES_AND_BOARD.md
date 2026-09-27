# Gate 10 - Finances and Board Systems

**Status: COMPLETE (28 September 2026)**

Gate 10 makes money and board constraints materially affect the reconstructed
Premier League management loop while preserving unresolved original behavior as
explicit fidelity boundaries rather than replacing it with invented systems.

## Verified completion checkpoint

Latest Gate-10 implementation checkpoint audited:

```text
5d626f0fda83d3f7b8ca09d82061002017b68b37
Test single-user dismissal control exit
```

GitHub Actions for that exact SHA:

- reconstruction test suite: **550 tests passed**;
- repository asset-policy workflow: **passed**.

Internal save schema at Gate-10 closure: **12**.

## Completion-criteria audit

### Club cash/balance is represented

Complete.

- The active Balance owns current cash and dated/category ledger entries.
- Fresh controlled-club current cash is sourced from the original
  `Master.dat` club float64 at packed `+165`.
- Transfer affordability reads the same live cash state used by finance
  postings.
- Balance cash and ledger state persist through the modern internal save.

### Wage and transfer budgets are represented

Complete according to recovered shipped behavior.

The executable contains legacy chairman budget-message payloads, including
transfer/wage-budget display fields, but no ordinary fresh-game producer or
normal Finance/Transfer UI consumer has been recovered for a separate live
chairman budget scalar. The shipped management constraint that is demonstrably
live is Balance/current cash plus the recovered accounting paths.

The modern port therefore does **not** invent a second wage/transfer-budget
system. Wage obligations, transfer affordability, transfer debits/credits, and
board financial objectives are represented through the recovered live state.
The legacy chairman-budget event family remains loadable/researchable and is
explicitly tracked as a fidelity boundary.

### Match and recurring income/cost paths are integrated

Complete for the recovered ordinary Premier League slice.

Integrated:

- normal Premier League match-day gate receipts;
- exact home/visiting ticket accounting categories 2/1;
- original source-backed stadium/ticket capacities and section allocation;
- original ticket-price response, FanFactor, side modifiers, facility factor,
  four-draw RNG placement, truncation and randomized subtraction;
- Balance credit's exact secondary category-1600 debit at
  `incoming * 0.002`;
- weekly player payroll on the recovered Saturday cadence, category 101;
- transfer spending/income, category 1000.

Deliberately not invented:

- fresh-game concession income, because the recovered generator never activates
  a persistent concession record;
- support-staff salary amounts, because the original CSupportStaff cost state is
  not yet materialized;
- broader cup/knockout gate branches and later facility-upgrade attendance
  effects, which belong to broader competition/building fidelity.

### Player wages and transfer spending/income persist

Complete.

- Runtime players carry the recovered weekly wage state.
- Weekly payroll debits the controlled club.
- Transfer completion debits buyer and credits seller through the recovered
  Balance category.
- Relevant finance/player/transfer state survives save/reload.

### Board expectations/job-security behavior is integrated where recovered

Complete.

The modern runtime now includes the recovered Premier League financial-objective
lifecycle:

- source-backed/fidelity-mapped candidate objective IDs;
- objective selection and target cash;
- three-year deadline state;
- same-Premier-League sporting progression for IDs 13/1/5/6;
- exact success / >95% near-miss / <=95% dismissal threshold behavior;
- persistent manager-sacking reason equivalent to DBRUser `+0x10D8`;
- reason-specific dismissal state preserved through save schema 12;
- authentic single-user control exit after maintenance, matching the original
  return to the Start Menu family while keeping DBRUser/Balance state intact.

### Approximations remain explicitly labeled

Complete.

Live deviations and deferred fidelity work remain in
`research/FIDELITY_GAPS.md`. Gate 10 did not convert unresolved finance
behavior into guessed mechanics.

## Important non-blocking fidelity boundaries

The following remain intentionally outside Gate-10 completion:

- legacy chairman budget-message family has no recovered ordinary producer/UI
  consumer;
- support-staff category-102 cadence is known but exact staff amount state is not
  yet materialized;
- fresh concessions stay disabled because original fresh-game activation is
  absent;
- special cup/knockout gate handling is research-only until broader competition
  integration;
- future stadium/facility upgrades are deferred to the building/management
  systems that own them;
- perfect Premier League statistical ties can still use the modern deterministic
  fallback, which can theoretically affect a board objective exactly at a
  cutoff.

These are fidelity work, not reasons to keep the finance/board gate open.

## Gate 11 handoff

Gate 11 should broaden the playable management loop around the already-stable
Premier League backend. Training/development mechanics are unusually mature
already, so the next task should begin by auditing which Gate-11 target has the
largest gap between recovered research and actual human-play integration before
implementing new behavior.
