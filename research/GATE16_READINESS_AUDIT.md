# Gate 16 readiness audit

_Date: 1 October 2026 KST_

## Status

**Criteria prevalidated by work-ahead; do not mark Gate 16 complete yet.**

Gate 13 remains the earliest incomplete validation gate, and Gate 15 has open
fidelity items. Under the deferred-blocker policy, later-gate work may advance
but Gate 16 must not be declared passed before its prerequisites close.

## Completion-criteria evidence

### Multiple seasons can run automatically

Prevalidated.

- Three consecutive fully played synthetic seasons:
  `3d6037d71365a2ddce53d2e6b40eda9baa02cf93`.
- Five save/reload round-trips across those seasons:
  `73ca421609cc6e929156c72f5b021b02a6efca3b`.
- Canonical shipped-data seed 1: three consecutive annual
  qualification/regeneration cycles, exit 0, final date 2003-06-02.
- Canonical shipped-data seed 2: three consecutive annual
  qualification/regeneration cycles, exit 0, final date 2003-06-02.

Machine-readable canonical receipts:

- `research/evidence/GATE16_CANONICAL_MULTISEASON_SEED1_RECOVERY137.json`
- `research/evidence/GATE16_CANONICAL_MULTISEASON_SEED2_RECOVERY137.json`

### Many deterministic seeds are exercised

Prevalidated.

The existing complete-season synthetic stress exercises six deterministic
seeds (`f08a014bc73c8ca4a7e11e3f10ef79e42ca13e62`). Recovery 137 adds two
independent canonical shipped-data player seeds, each across three consecutive
annual cycles. The two canonical seeds produced different RNG states and
different legitimate European-Cup materialized shapes while satisfying the same
fail-closed invariants.

### No unexplained destructive long-duration failure remains

Prevalidated for the currently modeled systems.

Coverage now includes:

- 30 annual regeneration replacements;
- three consecutive fully played synthetic seasons;
- 12 annual regeneration save/reload round-trips with payload-spread guard;
- five-year / 260-week autonomous transfer churn;
- yearly save/reload during that transfer churn;
- mixed shared-primary execution across Premier League, domestic Cup, European
  Cup, qualification Cup and procedural League owners;
- two canonical shipped-data three-season runs.

Discovered failures were investigated rather than suppressed:

- invalid two-club stress fixture: test-fixture defect, repaired without
  weakening production logic;
- contract month-end Python date overflow: bounded compatibility clamp added and
  exact original normalization retained in `FIDELITY_GAPS.md`;
- post-rollover immutable source-fixture identity: production save-continuity
  defect fixed and regressed;
- canonical seed-1 cycle-2 European node delta: proven legitimate UEFA Cup
  participant-dependent materialization;
- canonical current-regeneration projection mismatch: audit-only defect fixed
  in PR #65 and regressed.

No deadlocked calendar, roster collapse, invalid competition state, runaway
injury/discipline state, save corruption or unexplained unbounded season-owned
state growth remains in these tested paths.

### Regressions exist for discovered failures

Prevalidated.

Every production or audit defect discovered by the Gate-16 stress work either
has committed regression coverage or is explicitly retained as a bounded
fidelity approximation. PR #65's final projection correction passed asset-policy
run `36867367968` and reconstruction run `36867368043`, then merged as
`7f3f83eb98b9f29039b691197505dbe74c8b0851`.

## Canonical seed summary

Seed 1:

- elapsed: 1617.49 s;
- final RNG: 1945051110;
- fresh European node counts: 371, 371, 373.

Seed 2:

- elapsed: 1440.49 s;
- final RNG: 221122291;
- fresh European node counts: 367, 371, 371.

The differences are expected current-season qualification/materialization
effects, not stale cross-season accumulation.

## Gate transition rule

Do not check Gate 16 complete in `ROADMAP.md` yet. When Gates 13-15 are
actually closed, rerun the relevant full suite and reconcile this audit against
the then-current runtime. If no intervening change invalidates these results,
this evidence is sufficient to satisfy Gate 16's present roadmap criteria.
