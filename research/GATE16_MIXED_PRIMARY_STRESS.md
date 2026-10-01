# Gate 16 mixed shared-primary scheduler stress

_Date: 1 October 2026 KST_

## Scope

This is independent cloud-safe Gate-16 work-ahead while Gate 13 remains the
earliest incomplete validation gate.

The existing Gate-16 season tests are intentionally Premier-League-heavy.
`reconstruction/test_gate16_mixed_primary_stress.py` targets a different
failure surface: one long calendar driven through Gate 12's retained global
primary order and shared `simulate_due_primary_ai_entries` dispatcher while
five live scheduler-owner types mutate the same players, calendar, RNG and
post-match state:

- Premier League;
- English domestic Cup;
- European Cup;
- annual-qualification Cup;
- procedural League.

The fixture keeps the already-tested 20-club synthetic Premier League world so
League strategy cut lines remain structurally valid, but places only one real
Premier League fixture into the bounded mixed-owner primary order. It schedules
eight decisive matches for each non-PL owner across the remaining season and
builds the primary shadow/order from the shared source-bucket conversion rather
than dispatching owner methods directly.

Each simulated date advances the real game calendar, executes that date's
retained primary entries through the shared dispatcher, then runs the recovered
post-fixture calendar/player maintenance. Weekly transfer/payroll maintenance is
deliberately excluded because Gate 16 already has a separate five-year
autonomous-transfer stress; this test isolates the shared competition scheduler
rather than duplicating that subsystem.

## Long-duration invariants

The stress requires:

- the complete dated execution signature to match the retained global primary
  order exactly, so no scheduled entry is skipped, duplicated or reordered;
- all three Cup owners to finish every node with one persistent match state per
  scheduled event;
- Cup result-registry growth to equal the number of completed Cup events;
- the procedural League to retain exact fixture identity, complete all results
  and reconcile played totals;
- the bounded Premier League entry to complete in the same calendar while the
  underlying table remains a valid 20-club structure;
- the repeatedly exercised club rosters to retain their initial sizes and exact
  player ownership;
- Condition, Form, injury-return and suspension state to remain valid;
- a repeated run with the same CRT seed to reproduce the complete order, score,
  outcome, player-state and RNG signature.

## First CI finding and repair

The first PR run, reconstruction workflow `36842205701`, ran 1,132 tests with
22 expected source-gated skips and produced exactly two errors, both in the new
stress. The initial fixture had reduced the Premier League to two clubs. The
existing League strategy path correctly rejected that artificial structure
because its source-backed competition cut-line counts exceeded the table size.

That was a stress-fixture defect, not a production scheduler defect. The repair
keeps a valid 20-club Premier League table and limits only the entries exposed
through this stress's primary order. No production League strategy or cut-line
logic was weakened.

## Evidence boundary

This is **synthetic destructive/stability evidence**, not a claim about the
original FM2001 fixture calendar or competition frequency. The synthetic world
keeps CI cost bounded while exercising the real shared primary dispatch and live
owner implementations already reconstructed in Gate 12.

The fixture uses decisive Cup nodes. It intentionally does **not** bypass the
known fail-closed dynamic FA Cup replay boundary: runtime-created replay
construction is source-backed, but its exact post-shuffle `0x615A60` insertion
order is still unresolved and remains a fidelity gap. The production
`primary_entries_due_today` guard is left unchanged.

## Verification

The repaired final PR head `8bc252fdc5f0c960cd4cb8845a6fe1711b6a211d`
passed reconstruction workflow `36846018068`: **1,132 tests** in 297.493
seconds with **22 expected source-gated skips and zero failures**. Repository
asset-policy workflow `36846018016` also passed.

PR #58 squash-merged to canonical `main` as
`24447d846b96fe68d2eba7c17d0053de638e43ef`.

This strengthens Gate 16's broader-competition/state-growth evidence. It does
not replace canonical real-data multi-season evidence and does not close Gate
16.
