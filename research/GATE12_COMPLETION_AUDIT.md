# Gate 12 Completion Audit

_Date: 30 September 2026_

## Result

**Gate 12 - Other competitions is complete.**

The canonical real-data world now runs English domestic Cups, European
qualification/groups/knockouts, the required English divisions, annual
promotion/relegation, qualification-source competitions, and next-season
primary regeneration as one connected runtime. The Premier League is no longer
an isolated simulation.

Implementation checkpoint audited:

```text
6a966c022b68680dca5c950fa950ee586ba6f062
Use exact League name tie-breaker in European groups
```

## Canonical annual run

The audit used the authorized canonical FM2001 game data and the shared primary
AI scheduler. The recovered fresh-game calendar begins on **4 July 2000**.

Annual qualification became complete on **4 June 2001**, after **335 simulated
days**.

Required played League sources:

```text
0, 17, 21, 27, 31, 40, 50, 54
```

All **44** required DummyLeague sources were finalized through the recovered
annual DummyLeague lifecycle.

All ten required annual Cup sources published their live final
`(winner, loser)` pair:

```text
1, 5, 9, 10, 19, 23, 33, 91, 98, 101
```

The run also proved the source-derived Cup child procedural-League chain:

- Champions League phase 1: competition 14;
- Champions League phase 2: competition 167;
- World Club Championship group phase: competition 192.

A real phase-2 tie between Arsenal and Leeds exposed the final missing European
ranking bridge. Recovered League comparator `0x4F45E0` orders by points
descending, played ascending, goal difference descending, goals for descending,
goals against ascending, then DBRClub short-name bytes lexically. Using the
canonical CP1252 short-name bytes resolved the group exactly as Real Madrid CF,
Arsenal, Leeds United, PSV Eindhoven and allowed the remaining Champions League
knockout path to complete on its original dates.

## Atomic rollover result

The complete qualification snapshot and English transition were captured before
mutation. Annual materialization used a cloned controller CRT stream and
committed state plus RNG only after the replacement validated.

Observed canonical rollover:

- qualification capture date: **2001-06-04**;
- membership changes: **28**;
- rollover season year: **2001**;
- controller RNG before rollover: **`0xCE9A6E40`**;
- post-DummyLeague preview RNG: **`0xD12D4AE4`**;
- controller RNG after committed rollover: **`0x6F763739`**;
- annual materialization draw count: **15,539**;
- year-two Premier League fixtures: **380**;
- year-two primary-order dates: **150**;
- year-two live procedural competition IDs:
  `2, 3, 4, 7, 17, 21, 27, 31, 40, 50, 54, 192`.

Every played annual qualification-source League remained live after rollover.

## Regression / CI audit

The full reconstruction suite ran **828 tests with 2 failures**, exactly the
two unchanged secondary-schedule assertions:

1. `test_secondary_root_order_uses_same_crt_qsort_then_mode_filter`;
2. `test_secondary_container_bucket_counts_reach_canonical_staff_seed`.

No new Gate-12 regression failed. GitHub **Repository asset policy** passed at
the audited implementation checkpoint.

## Completion criteria

- [x] Each newly supported competition format has deterministic regression
  coverage.
- [x] The Premier League no longer behaves as an isolated world.

## Residual boundaries

Gate 12 does not claim every unrelated FM2001 fidelity gap is closed. The
special both-controlled-participants Cup revenue-posting policy remains
deferred, as do original save compatibility and the two known secondary
scheduler discrepancies. They remain tracked in `research/FIDELITY_GAPS.md`.

The next active gate is **Gate 13 - Restore original management presentation**.
