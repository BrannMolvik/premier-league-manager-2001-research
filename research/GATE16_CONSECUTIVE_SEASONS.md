# Gate 16 consecutive played-season stress

_Date: 1 October 2026 KST_

## Scope

This is cloud-safe Gate-16 work-ahead while Gate 13 remains the earliest
incomplete validation gate.

The test in reconstruction/test_gate16_consecutive_seasons.py is materially
different from the earlier multi-seed test. It keeps one GameState and one
controller RNG alive while playing three complete 20-club seasons, with the
normal annual primary regeneration API between seasons.

## Synthetic-world boundary

The fixture uses a 20-club synthetic Premier League and the ordinary
380-fixture double round robin. The eight required English LeagueAllocation
IDs are present only so the recovered transition API is exercised. In this
stress fixture each allocation selects two positions inside the same synthetic
competition whose club memberships are all already 0. This is neutral plumbing
for the fake world and is not evidence about original promotion/relegation.

At each completed season the test publishes a source-comparator-compatible
ranking using unique synthetic CP1252 short names, then calls
HumanGameplayController.regenerate_annual_primary_season for the next year.

## Long-duration invariants

Across all three seasons the same live world must:

- complete all 380 fixtures per season;
- advance calendar dates monotonically across both annual rollovers;
- replace the Premier League runtime object each year;
- begin each regenerated season with zero stored results and exactly 380 new
  fixtures;
- preserve the controller CRT state returned by annual regeneration;
- keep all 20 clubs in the synthetic competition;
- reconcile played totals, goals and wins/losses every season;
- maintain at least 16 live rostered players per club;
- keep roster ownership coherent;
- keep Condition, Form and suspension counters within valid bounds.

This carries player/calendar/RNG state through more than two years instead of
recreating a fresh GameState for each season.

## Evidence boundary

A pass is strong synthetic evidence for the Gate-16 criterion that multiple
seasons can run automatically. It does not replace canonical real-data
multi-season evidence, and it does not by itself close Gate 16. Broader
competition state, transfers, save/reload cycles, many more seeds and any
failure-driven regressions still need long-duration coverage.


## Save/reload continuation stress

Recovery 129 extends the same three-season synthetic world with internal
save/reload checkpoints during every season and immediately after each annual
primary regeneration.

The added regression requires five round-trips in total:

- season one after 120 completed Premier League fixtures;
- immediately after the 2001 annual primary regeneration;
- season two after 160 completed fixtures;
- immediately after the 2002 annual primary regeneration;
- season three after 200 completed fixtures.

Every round-trip compares the complete serialized controller snapshot before
and after reload. The season must then continue to all 380 fixtures with table,
roster, Condition, Form, suspension and monthly-development invariants still
valid. This specifically targets save corruption that only appears after the
live calendar, player state, controller RNG and regenerated competition runtime
have already accumulated long-duration changes.

A failure at either post-regeneration checkpoint is treated as a real Gate-16
save-continuity defect, not worked around by rebuilding a fresh season.

This remains synthetic evidence. It does not substitute for canonical
real-data multi-season save/reload testing or the still-needed broader
competition and transfer stress.
