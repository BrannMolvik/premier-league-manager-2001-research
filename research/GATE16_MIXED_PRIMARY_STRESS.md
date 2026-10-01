# Gate 16 mixed shared-primary scheduler stress

_Date: 1 October 2026 KST_

## Scope

This is independent cloud-safe Gate-16 work-ahead while Gate 13 remains the
earliest incomplete validation gate.

The existing Gate-16 season tests are intentionally Premier-League-heavy.
`reconstruction/test_gate16_mixed_primary_stress.py` targets a different
failure surface: one long calendar driven through Gate 12's shared
`advance_one_day_with_primary_ai_matches` path while five live scheduler-owner
types mutate the same players, calendar, RNG and post-match state:

- Premier League;
- English domestic Cup;
- European Cup;
- annual-qualification Cup;
- procedural League.

The synthetic fixture uses the already proven two-club AI match database. It
schedules eight decisive matches for each non-PL owner across the season, plus
one Premier League fixture, and builds the primary shadow/order from the shared
source-bucket conversion rather than dispatching owner methods directly.

## Long-duration invariants

The stress requires:

- every scheduled primary entry to execute exactly once through the shared
  dispatcher;
- all three Cup owners to finish every node without runtime-created transient
  leakage;
- Cup result-registry growth to equal the number of completed Cup events;
- the procedural League to retain exact fixture identity, complete all results
  and reconcile played totals;
- the Premier League fixture to complete in the same calendar;
- both 16-player rosters to retain exact ownership;
- Condition, Form, injury-return and suspension state to remain valid;
- no pending proposal/deal/bid/scheduled-transfer state to leak from calendar
  maintenance;
- a repeated run with the same CRT seed to reproduce the complete score,
  outcome, player-state and RNG signature.

## Evidence boundary

This is **synthetic destructive/stability evidence**, not a claim about the
original FM2001 fixture calendar or competition frequency. The deliberately
small two-club world keeps CI cost bounded while exercising the real shared
primary dispatch and live owner implementations already reconstructed in Gate
12.

The fixture uses decisive Cup nodes. It intentionally does **not** bypass the
known fail-closed dynamic FA Cup replay boundary: runtime-created replay
construction is source-backed, but its exact post-shuffle `0x615A60` insertion
order is still unresolved and remains a fidelity gap.

A pass strengthens Gate 16's broader-competition/state-growth evidence. It does
not replace canonical real-data multi-season evidence and does not close Gate
16.
