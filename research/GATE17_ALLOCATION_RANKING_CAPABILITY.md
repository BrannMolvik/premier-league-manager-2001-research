# Gate 17 LeagueAllocation ranking capability audit

_Status: independent work-ahead while Gate 13 shared runtime remains Codex-owned._

## Purpose

The canonical TeamSelect scope and parsed DBTLeagueAllocations are now mapped
country by country. The existing source-backed exchange executor is already
generic, but it cannot run safely until every allocation endpoint has an exact
final ranking of sufficient length.

This checkpoint isolates that remaining dependency without applying any
membership changes.

## Contract

`audit_allocation_ranking_capability()` consumes:

- the exact `PlayableCountryAllocationPlan`;
- the parsed source LeagueAllocation rows;
- immutable rankings keyed by source competition ID.

For every assigned allocation, the audit reconstructs the exact inclusive source
position ranges on both endpoints, including descending ranges. It then records:

- required competition endpoint ID;
- exact required ranking positions;
- observed ranking length;
- whether that endpoint can satisfy the source row;
- a specific failure reason when it cannot.

A ranking is unresolved when it is absent, explicitly `None`, too short for
the highest referenced source position, or the source row references a negative
position. Ranking tuples containing invalid or duplicate club IDs fail closed.

The audit never labels an endpoint as a playoff, promotion place or relegation
place. It checks only whether the original row's required ranking slots can be
read.

## Runtime resolver bridge

`audit_allocation_ranking_resolver()` calls a supplied ranking resolver exactly
once per required endpoint, in first-seen country-plan order, then runs the same
audit.

After the Gate-13 shared-runtime lock is released, the intended integration
point is the existing `GameState.season_transition_ranking(competition_id)`
surface. The audit can therefore be run immediately before annual exchanges to
prove that every source endpoint required by the full TeamSelect scope is live
before any membership mutation occurs.

No GameState method is modified by this checkpoint.

## Release value

The result provides exact:

- assigned allocation IDs;
- resolved and unresolved allocation IDs;
- required endpoint IDs;
- resolved and unresolved endpoint IDs;
- per-allocation endpoint requirements;
- canonical playable-scope catalog SHA-256.

`complete=true` is possible only when every assigned source allocation has
both endpoints fully readable at all positions it consumes.

This gives Gate 17 a machine-readable progression blocker that is independent
from the already-separate human club-selection capability audit.

## Remaining boundary

This audit does **not**:

- publish missing rankings;
- simulate non-English League fixtures;
- choose playoff winners;
- perform LeagueAllocation exchanges;
- modify memberships;
- regenerate a season;
- claim full-scope progression.

Once the runtime ranking publishers are generalized, the next step is to run
this audit at the annual boundary, then feed the exact source rows and verified
rankings into the existing generic `apply_league_allocation_exchanges()`
executor.
