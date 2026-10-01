# Gate 16 annual-regeneration destructive soak foundation

_Date: 1 October 2026 KST_

## Scope

Gate 16 is not active and is not complete. This is independent cloud-safe
work-ahead under the deferred-blocker policy while Gate 13 still awaits its
real Windows graphical audit.

The file reconstruction/gate16_annual_regeneration_soak.py repeatedly exercises
the already recovered annual primary-season replacement boundary. It does not
pretend that those seasons were played. A caller must provide completed-season
qualification evidence before every rollover.

## Destructive invariants

Each cycle requires:

- a newly constructed Premier League runtime object;
- no prior-season Premier League results after install;
- no prior prepared-match environments after install;
- a nonempty regenerated fixture set;
- stable Premier League fixture count across the soak;
- exactly one scheduler occurrence for every regenerated Premier League
  fixture, with no duplicates or omissions;
- controller CRT state equal to the regeneration's committed state_after.

The test deliberately dirties each old season with a result and a prepared
match environment immediately before the next rollover, then runs 30
consecutive annual replacements. This targets stale-state accumulation and
replacement bugs without inventing match outcomes, rankings or qualification
rules.

## Evidence boundary

Passing this soak demonstrates repeated destructive regeneration, not the
Gate-16 completion criterion that multiple seasons can run automatically.
Still required before Gate 16 can close:

- automatically play/simulate multiple complete seasons through the calendar;
- exercise many deterministic seeds;
- include transfers, injuries, discipline, saves and broader competitions over
  the long run;
- diagnose and regression-lock any deadlocks, roster collapse, invalid
  competition state, save corruption or unbounded growth discovered.

The earliest incomplete validation gate remains Gate 13.
